#!/usr/bin/env python3
"""
Spellaroo - Web-based Spelling Quiz Application
Flask web application for the Spellaroo spelling quiz game
"""

import os
import sys
import json
import time
import random
import secrets
import sqlite3
import hashlib
import hmac
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Google OAuth imports
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import requests

# Add the current directory to Python path to import word_lists
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from word_lists import word_dictionary

app = Flask(__name__)

# SECRET_KEY is mandatory outside the dev server; a signed session cookie with a
# known key is forgeable. In debug we fall back to an ephemeral random key.
_secret = os.environ.get('SECRET_KEY')
if not _secret:
    if os.environ.get('FLASK_DEBUG') or __name__ == '__main__':
        _secret = secrets.token_hex(32)
        print("WARNING: SECRET_KEY not set; using an ephemeral dev key (sessions reset on restart).")
    else:
        raise RuntimeError("SECRET_KEY environment variable must be set in production.")
app.secret_key = _secret

# Behind Apache's reverse proxy, honor X-Forwarded-Proto/Host so url_for(_external=True)
# builds https:// URLs (required for the Google OAuth redirect_uri to match).
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Session cookie hardening (Secure is relaxed for the plain-HTTP dev server in __main__)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

# CSRF protection for all state-changing POSTs (forms send a hidden csrf_token;
# AJAX sends it via the X-CSRFToken header — see base.html).
csrf = CSRFProtect(app)

# Rate limiting (brute-force protection on auth routes). In-memory storage is
# fine for a single gunicorn host; move to Redis if scaled to multiple workers/hosts.
limiter = Limiter(get_remote_address, app=app, default_limits=[])

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

# If no environment variables are set, use development defaults
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    # Development mode - these will need to be replaced with real credentials
    GOOGLE_CLIENT_ID = "your-google-client-id.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = "your-google-client-secret"
    print("WARNING: Using default Google OAuth credentials. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables for production.")

def create_google_oauth_flow():
    """Create Google OAuth flow"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [url_for('google_callback', _external=True)]
            }
        },
        scopes=['openid', 'email', 'profile']
    )
    flow.redirect_uri = url_for('google_callback', _external=True)
    return flow

@app.context_processor
def inject_globals():
    """Expose common values (current year, login state) to all templates."""
    return {
        'current_year': datetime.now().year,
        'logged_in': 'user_id' in session,
        'nav_user_name': session.get('user_name'),
    }

# Add custom template filters
@app.template_filter('from_json')
def from_json_filter(s):
    """Template filter to parse JSON strings"""
    try:
        return json.loads(s) if s else []
    except (json.JSONDecodeError, TypeError):
        return []

# Database setup
DATABASE = 'quiz_sessions.db'

def init_db():
    """Initialize the database"""
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_id INTEGER,
                date_time TEXT,
                grades TEXT,
                word_type TEXT,
                total_words INTEGER,
                correct_count INTEGER,
                incorrect_count INTEGER,
                incorrect_words TEXT,
                percentage REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create users table with Google OAuth support
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                google_id TEXT UNIQUE,
                birth_year INTEGER,
                birth_month INTEGER,
                auth_provider TEXT DEFAULT 'local',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migration: Add google_id and auth_provider columns if they don't exist
        try:
            conn.execute('ALTER TABLE users ADD COLUMN google_id TEXT UNIQUE')
        except sqlite3.OperationalError:
            pass  # Column already exists
            
        try:
            conn.execute('ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT "local"')
        except sqlite3.OperationalError:
            pass  # Column already exists
            
        # Make password_hash nullable for Google OAuth users
        try:
            # Check if we need to migrate the table structure
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # If password_hash is NOT NULL, we need to recreate the table
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
            table_sql = cursor.fetchone()[0]
            if 'password_hash TEXT NOT NULL' in table_sql:
                # Backup existing data
                cursor.execute("SELECT id, name, email, password_hash, birth_year, birth_month FROM users")
                existing_users = cursor.fetchall()
                
                # Drop and recreate table
                conn.execute('DROP TABLE users')
                conn.execute('''
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT,
                        google_id TEXT UNIQUE,
                        birth_year INTEGER,
                        birth_month INTEGER,
                        auth_provider TEXT DEFAULT 'local',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Restore existing data
                for user in existing_users:
                    conn.execute('''
                        INSERT INTO users (id, name, email, password_hash, birth_year, birth_month, auth_provider)
                        VALUES (?, ?, ?, ?, ?, ?, 'local')
                    ''', user)
        except Exception as e:
            print(f"Migration warning: {e}")

        # Server-side quiz state: keeps the answer list off the client cookie.
        # The cookie only holds an opaque quiz_id token.
        conn.execute('''
            CREATE TABLE IF NOT EXISTS quiz_state (
                quiz_id TEXT PRIMARY KEY,
                user_id INTEGER,
                config TEXT,
                updated_at REAL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Per-user saved quiz preferences (remembers last setup choices).
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_prefs (
                user_id INTEGER PRIMARY KEY,
                prefs TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        conn.commit()

def save_user_prefs(user_id, prefs):
    """Remember a user's last quiz setup (grades, word type, count)."""
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('INSERT OR REPLACE INTO user_prefs (user_id, prefs) VALUES (?, ?)',
                     (user_id, json.dumps(prefs)))
        conn.commit()

def load_user_prefs(user_id):
    with sqlite3.connect(DATABASE) as conn:
        row = conn.execute('SELECT prefs FROM user_prefs WHERE user_id = ?', (user_id,)).fetchone()
    return json.loads(row[0]) if row else None

def get_user_misses(user_id, limit=None):
    """Aggregate a user's historically misspelled words, most-frequent first.
    Returns a list of (word, count)."""
    from collections import Counter
    counter = Counter()
    with sqlite3.connect(DATABASE) as conn:
        rows = conn.execute('SELECT incorrect_words FROM sessions WHERE user_id = ?', (user_id,)).fetchall()
    for (blob,) in rows:
        try:
            for w in json.loads(blob or '[]'):
                if w in word_dictionary:
                    counter[w] += 1
        except (json.JSONDecodeError, TypeError):
            pass
    items = counter.most_common(limit) if limit else counter.most_common()
    return items

def compute_streak(dates):
    """Given a set of date objects a user completed a quiz, return the current
    consecutive-day streak ending today or yesterday."""
    from datetime import date, timedelta
    if not dates:
        return 0
    days = set(dates)
    today = datetime.now().date()
    # Streak counts only if the user played today or yesterday.
    start = today if today in days else (today - timedelta(days=1) if (today - timedelta(days=1)) in days else None)
    if start is None:
        return 0
    streak, d = 0, start
    while d in days:
        streak += 1
        d -= timedelta(days=1)
    return streak

# ---- Server-side quiz-state helpers -------------------------------------------------

def save_quiz_state(quiz_id, user_id, config):
    """Persist quiz config (word list, progress) server-side, keyed by opaque token."""
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            'INSERT OR REPLACE INTO quiz_state (quiz_id, user_id, config, updated_at) VALUES (?, ?, ?, ?)',
            (quiz_id, user_id, json.dumps(config), time.time())
        )
        conn.commit()

def load_quiz_state(quiz_id, user_id):
    """Load a quiz config, but only if it belongs to this user."""
    if not quiz_id:
        return None
    with sqlite3.connect(DATABASE) as conn:
        row = conn.execute(
            'SELECT config FROM quiz_state WHERE quiz_id = ? AND user_id = ?',
            (quiz_id, user_id)
        ).fetchone()
    return json.loads(row[0]) if row else None

def clear_quiz_state(quiz_id):
    """Remove a finished/abandoned quiz's server-side state."""
    if not quiz_id:
        return
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('DELETE FROM quiz_state WHERE quiz_id = ?', (quiz_id,))
        conn.commit()

def compare_spellings(correct_word, user_input):
    """Return the correct word with correctly-placed chars lowercase and
    wrong/missing chars UPPERCASE, via edit-distance alignment. Ported from the
    CLI (word_quiz.py) so the web app shows the same teaching feedback."""
    if not user_input:
        return correct_word.upper() if correct_word else ""
    if not correct_word:
        return ""

    s1 = correct_word.lower()
    s2 = user_input.lower()
    m, n = len(s1), len(s2)

    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    alignment = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and s1[i - 1] == s2[j - 1]:
            alignment.append((s1[i - 1], True)); i -= 1; j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            alignment.append((s1[i - 1], False)); i -= 1; j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            alignment.append((s1[i - 1], False)); i -= 1
        else:
            j -= 1

    return "".join(c if ok else c.upper() for c, ok in reversed(alignment))

def build_word_pool(grades, word_type):
    """Build word pool based on grade levels and word type"""
    sight_words = []
    non_sight_words = []
    
    # Collect words from selected grade levels using unified dictionary
    for word, data in word_dictionary.items():
        # Check if word appears in any of the selected grade levels
        if any(grade in data["grade_levels"] for grade in grades):
            if data["sight_word"]:
                sight_words.append(word)
            else:
                non_sight_words.append(word)
    
    # Remove duplicates (though they shouldn't exist in the new format)
    sight_words = list(set(sight_words))
    non_sight_words = list(set(non_sight_words))
    
    # Build final word pool based on word type
    if word_type == 's':  # sight words only
        result = sight_words
    elif word_type == 'o':  # non sight words only
        result = non_sight_words
    elif word_type == 'f':  # 50/50 mix
        min_count = min(len(sight_words), len(non_sight_words))
        if min_count < 5:
            # If we don't have enough of one type, return all available
            result = sight_words + non_sight_words
        else:
            # Take equal amounts from each
            result = random.sample(sight_words, min_count) + random.sample(non_sight_words, min_count)
    elif word_type == 'r':  # random mix
        result = sight_words + non_sight_words
    else:
        result = []
    
    return result

def save_session_data(session_id, grades, word_type, total_words, correct_count, incorrect_count, incorrect_words):
    """Save quiz session data to database"""
    try:
        percentage = (correct_count / total_words * 100) if total_words > 0 else 0
        user_id = session.get('user_id')
        
        with sqlite3.connect(DATABASE) as conn:
            conn.execute('''
                INSERT INTO sessions 
                (session_id, user_id, date_time, grades, word_type, total_words, correct_count, incorrect_count, incorrect_words, percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                user_id,
                datetime.now().isoformat(),
                json.dumps(grades),
                word_type,
                total_words,
                correct_count,
                incorrect_count,
                json.dumps(incorrect_words),
                percentage
            ))
            conn.commit()
    except Exception as e:
        print(f"Error saving session data: {e}")

def normalize_email(email):
    """Lowercase + strip so Kid@X.com and kid@x.com map to one account."""
    return email.strip().lower() if email else email

def hash_password(password):
    """Hash password using PBKDF2 (werkzeug)"""
    return generate_password_hash(password)

def verify_password(password, password_hash):
    """Verify a password against a werkzeug hash, or a legacy SHA-1 hex digest."""
    if not password_hash:
        return False
    if ':' in password_hash:
        return check_password_hash(password_hash, password)
    # Legacy SHA-1 hash (accounts created before the PBKDF2 upgrade)
    legacy = hashlib.sha1(password.encode('utf-8')).hexdigest()
    return hmac.compare_digest(legacy, password_hash)

def create_user(name, email, password=None, birth_year=None, birth_month=None, google_id=None, auth_provider='local'):
    """Create a new user account"""
    try:
        email = normalize_email(email)
        password_hash = hash_password(password) if password else None

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, email, password_hash, birth_year, birth_month, google_id, auth_provider)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, email, password_hash, birth_year, birth_month, google_id, auth_provider))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None  # Email already exists
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def create_google_user(name, email, google_id):
    """Create a new Google OAuth user account"""
    return create_user(name, email, google_id=google_id, auth_provider='google')

def get_user_by_google_id(google_id):
    """Get user by Google ID"""
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, email, birth_year, birth_month, google_id, auth_provider
                FROM users WHERE google_id = ?
            ''', (google_id,))
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'birth_year': user[3],
                    'birth_month': user[4],
                    'google_id': user[5],
                    'auth_provider': user[6]
                }
            return None
    except Exception as e:
        print(f"Error getting user by Google ID: {e}")
        return None

def get_user_by_email(email):
    """Get user by email address"""
    try:
        email = normalize_email(email)
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, email, birth_year, birth_month, google_id, auth_provider
                FROM users WHERE email = ?
            ''', (email,))
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'birth_year': user[3],
                    'birth_month': user[4],
                    'google_id': user[5],
                    'auth_provider': user[6]
                }
            return None
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None

def authenticate_user(email, password):
    """Authenticate user by email and password (local auth only)"""
    try:
        email = normalize_email(email)
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, email, password_hash, birth_year, birth_month, auth_provider
                FROM users WHERE email = ? AND auth_provider = 'local'
            ''', (email,))
            user = cursor.fetchone()
            
            if user and user[3] and verify_password(password, user[3]):
                # Transparently upgrade legacy SHA-1 hashes to PBKDF2 on login
                if ':' not in user[3]:
                    conn.execute('UPDATE users SET password_hash = ? WHERE id = ?',
                                 (hash_password(password), user[0]))
                    conn.commit()
                return {
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'birth_year': user[4],
                    'birth_month': user[5],
                    'auth_provider': user[6]
                }
            return None
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None

def get_user_by_id(user_id):
    """Get user information by ID"""
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, email, birth_year, birth_month, google_id, auth_provider
                FROM users WHERE id = ?
            ''', (user_id,))
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'birth_year': user[3],
                    'birth_month': user[4],
                    'google_id': user[5],
                    'auth_provider': user[6]
                }
            return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def login_required(f):
    """Decorator to require login for routes"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute; 50 per hour", methods=["POST"])
def login():
    """User login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email and password:
            user = authenticate_user(email, password)
            if user:
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password.', 'error')
        else:
            flash('Please enter both email and password.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute; 20 per hour", methods=["POST"])
def register():
    """User registration page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        birth_year = request.form.get('birth_year')
        birth_month = request.form.get('birth_month')
        
        # Validation
        if not all([name, email, password, confirm_password, birth_year, birth_month]):
            flash('All fields are required.', 'error')
        elif password != confirm_password:
            flash('Passwords do not match.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
        else:
            try:
                birth_year = int(birth_year)
                birth_month = int(birth_month)
                
                if birth_year < 1900 or birth_year > datetime.now().year:
                    flash('Please enter a valid birth year.', 'error')
                elif birth_month < 1 or birth_month > 12:
                    flash('Please enter a valid birth month (1-12).', 'error')
                else:
                    user_id = create_user(name, email, password, birth_year, birth_month)
                    if user_id:
                        flash('Registration successful! Please log in.', 'success')
                        return redirect(url_for('login'))
                    else:
                        flash('Email address is already registered.', 'error')
            except ValueError:
                flash('Please enter valid numbers for birth year and month.', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout"""
    clear_quiz_state(session.get('quiz_id'))
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.errorhandler(429)
def ratelimit_handler(e):
    """Friendly response when rate limits are hit on auth routes."""
    flash('Too many attempts. Please wait a minute and try again.', 'error')
    return redirect(request.referrer or url_for('login'))

# Google OAuth routes
@app.route('/auth/google')
def google_login():
    """Initiate Google OAuth login"""
    try:
        flow = create_google_oauth_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        session['state'] = state
        # google-auth-oauthlib enables PKCE by default; the code_verifier is
        # generated here and must be replayed in the callback's token exchange.
        session['code_verifier'] = flow.code_verifier
        return redirect(authorization_url)
    except Exception as e:
        print(f"Google OAuth error: {e}")
        flash('Google login is not available. Please use email/password login.', 'error')
        return redirect(url_for('login'))

@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        if 'state' not in session or request.args.get('state') != session['state']:
            flash('Invalid state parameter', 'error')
            return redirect(url_for('login'))
        
        flow = create_google_oauth_flow()
        flow.code_verifier = session.get('code_verifier')
        flow.fetch_token(authorization_response=request.url)
        
        credentials = flow.credentials
        request_session = google_requests.Request()
        
        # Verify the token and get user info
        idinfo = id_token.verify_oauth2_token(
            credentials.id_token, request_session, GOOGLE_CLIENT_ID
        )
        
        google_user_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo['name']
        
        # Check if user exists by Google ID
        user = get_user_by_google_id(google_user_id)
        
        if not user:
            # Check if user exists by email (might be a local account)
            existing_user = get_user_by_email(email)
            if existing_user:
                if existing_user['auth_provider'] == 'local':
                    flash('An account with this email already exists. Please sign in with your email and password.', 'error')
                    return redirect(url_for('login'))
                else:
                    # Update existing Google user with new Google ID
                    user = existing_user
            else:
                # Create new Google user
                user_id = create_google_user(name, email, google_user_id)
                if user_id:
                    user = get_user_by_id(user_id)
                else:
                    flash('Error creating user account', 'error')
                    return redirect(url_for('login'))
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['auth_provider'] = 'google'
            flash(f'Welcome, {user["name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed', 'error')
            return redirect(url_for('login'))
            
    except ValueError as e:
        print(f"Token verification failed: {e}")
        flash('Google authentication failed', 'error')
        return redirect(url_for('login'))
    except Exception as e:
        print(f"Google OAuth callback error: {e}")
        flash('Google login failed. Please try again.', 'error')
        return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = get_user_by_id(session['user_id'])
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('logout'))
    
    # Get user's quiz statistics
    streak = 0
    badges = []
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*), AVG(percentage), SUM(total_words), SUM(correct_count)
                FROM sessions WHERE user_id = ?
            ''', (session['user_id'],))
            stats = cursor.fetchone()

            user_stats = {
                'total_quizzes': stats[0] or 0,
                'average_score': round(stats[1] or 0, 1),
                'total_words': stats[2] or 0,
                'total_correct': stats[3] or 0
            }

            # Daily streak from distinct quiz dates
            rows = conn.execute('SELECT created_at FROM sessions WHERE user_id = ?',
                                (session['user_id'],)).fetchall()
        dates = []
        for (ts,) in rows:
            try:
                dates.append(datetime.fromisoformat(ts.replace('Z', '')).date())
            except (ValueError, AttributeError):
                pass
        streak = compute_streak(dates)

        # Simple achievement badges
        tq = user_stats['total_quizzes']
        if tq >= 1: badges.append(('🎯', 'First Quiz'))
        if tq >= 10: badges.append(('🔟', '10 Quizzes'))
        if tq >= 50: badges.append(('🏅', '50 Quizzes'))
        if user_stats['average_score'] >= 90 and tq >= 5:
            badges.append(('🌟', 'Spelling Star'))
        if streak >= 3: badges.append(('🔥', f'{streak}-Day Streak'))
    except Exception as e:
        print(f"Error getting user stats: {e}")
        user_stats = {'total_quizzes': 0, 'average_score': 0, 'total_words': 0, 'total_correct': 0}

    return render_template('profile.html', user=user, stats=user_stats,
                           streak=streak, badges=badges)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    """Edit display name and (for local accounts) change password."""
    user = get_user_by_id(session['user_id'])
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('logout'))

    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        current_pw = request.form.get('current_password') or ''
        new_pw = request.form.get('new_password') or ''
        confirm_pw = request.form.get('confirm_password') or ''

        if not name:
            flash('Name cannot be empty.', 'error')
            return render_template('profile_edit.html', user=user)

        with sqlite3.connect(DATABASE) as conn:
            conn.execute('UPDATE users SET name = ? WHERE id = ?', (name, user['id']))
            conn.commit()
        session['user_name'] = name

        # Optional password change (local accounts only)
        if new_pw or confirm_pw or current_pw:
            if user['auth_provider'] != 'local':
                flash('Password change is not available for Google accounts.', 'error')
            elif len(new_pw) < 6:
                flash('New password must be at least 6 characters.', 'error')
            elif new_pw != confirm_pw:
                flash('New passwords do not match.', 'error')
            elif not authenticate_user(user['email'], current_pw):
                flash('Current password is incorrect.', 'error')
            else:
                with sqlite3.connect(DATABASE) as conn:
                    conn.execute('UPDATE users SET password_hash = ? WHERE id = ?',
                                 (hash_password(new_pw), user['id']))
                    conn.commit()
                flash('Profile and password updated.', 'success')
                return redirect(url_for('profile'))

        flash('Profile updated.', 'success')
        return redirect(url_for('profile'))

    return render_template('profile_edit.html', user=user)

@app.route('/practice_missed')
@login_required
def practice_missed():
    """Start a quiz built from the user's historically misspelled words."""
    misses = get_user_misses(session['user_id'])
    words = [w for w, _ in misses]
    if not words:
        flash('No missed words yet — take a quiz first!', 'info')
        return redirect(url_for('setup'))

    selected_words = words[:20]
    config = {
        'grades': ['missed'],
        'word_type': 'r',
        'selected_words': selected_words,
        'current_word_index': 0,
        'correct_answers': [],
        'incorrect_answers': [],
        'start_time': datetime.now().isoformat()
    }
    clear_quiz_state(session.get('quiz_id'))
    quiz_id = secrets.token_urlsafe(24)
    session['quiz_id'] = quiz_id
    save_quiz_state(quiz_id, session['user_id'], config)
    return redirect(url_for('quiz'))

@app.route('/')
def index():
    """Main page: public landing for visitors, dashboard for logged-in users."""
    if 'user_id' not in session:
        return render_template('landing.html', word_count=len(word_dictionary))
    return render_template('index.html',
                           user_name=session.get('user_name'),
                           word_count=len(word_dictionary))

@app.route('/privacy')
def privacy():
    """Privacy policy (COPPA-conscious: explains what kids' data is stored)."""
    return render_template('privacy.html')

@app.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    """Quiz setup page"""
    if request.method == 'POST':
        try:
            # Handle both kindergarten ('k') and regular grades (1-12)
            grade_inputs = request.form.getlist('grades')
            grades = []
            
            for grade_input in grade_inputs:
                if grade_input.lower() == 'k':
                    grades.append('k')
                else:
                    try:
                        grade_num = int(grade_input)
                        if 1 <= grade_num <= 12:
                            grades.append(grade_num)
                    except ValueError:
                        pass
            
            word_type = request.form.get('word_type', 'r')
            num_words = int(request.form.get('num_words', 10))
            
            if not grades:
                return jsonify({'error': 'Please select valid grade levels (k for kindergarten, 1-12 for grades)'}), 400
            
            # Build word pool
            available_words = build_word_pool(grades, word_type)
            
            if len(available_words) < num_words:
                return jsonify({'error': f'Only {len(available_words)} words available for selected criteria'}), 400
            
            # Select random words for quiz
            selected_words = random.sample(available_words, num_words)

            # Store quiz configuration server-side; the cookie only holds an
            # opaque token, so the answer list never reaches the client.
            config = {
                'grades': grades,
                'word_type': word_type,
                'selected_words': selected_words,
                'current_word_index': 0,
                'correct_answers': [],
                'incorrect_answers': [],
                'start_time': datetime.now().isoformat()
            }
            clear_quiz_state(session.get('quiz_id'))
            quiz_id = secrets.token_urlsafe(24)
            session['quiz_id'] = quiz_id
            save_quiz_state(quiz_id, session['user_id'], config)

            # Remember these choices for next time
            save_user_prefs(session['user_id'], {
                'grades': grades, 'word_type': word_type, 'num_words': num_words
            })

            return redirect(url_for('quiz'))

        except Exception as e:
            return jsonify({'error': str(e)}), 400

    # Preselect the user's last-used settings (falls back to defaults in the template)
    prefs = load_user_prefs(session['user_id']) or {}
    return render_template('setup.html', prefs=prefs)

@app.route('/quiz')
@login_required
def quiz():
    """Quiz page"""
    config = load_quiz_state(session.get('quiz_id'), session['user_id'])
    if not config:
        return redirect(url_for('setup'))

    current_index = config['current_word_index']

    if current_index >= len(config['selected_words']):
        return redirect(url_for('results'))
    
    current_word = config['selected_words'][current_index]
    word_data = word_dictionary[current_word]
    
    return render_template('quiz.html', 
                         word=current_word,
                         definition=word_data['definition'],
                         current_index=current_index + 1,
                         total_words=len(config['selected_words']))

@app.route('/submit_answer', methods=['POST'])
@login_required
def submit_answer():
    """Handle quiz answer submission"""
    quiz_id = session.get('quiz_id')
    config = load_quiz_state(quiz_id, session['user_id'])
    if not config:
        return jsonify({'error': 'No active quiz session'}), 400

    current_index = config['current_word_index']

    if current_index >= len(config['selected_words']):
        return jsonify({'error': 'Quiz already completed'}), 400

    current_word = config['selected_words'][current_index]
    user_answer = (request.json.get('answer') or '').strip().lower()

    # Check answer
    is_correct = user_answer == current_word.lower()

    # Character-by-character diff (lowercase = right, UPPERCASE = wrong/missing)
    diff = None if is_correct else compare_spellings(current_word, user_answer)

    if is_correct:
        config['correct_answers'].append(current_word)
    else:
        config['incorrect_answers'].append({
            'word': current_word,
            'user_answer': user_answer,
            'correct_answer': current_word,
            'diff': diff
        })

    # Move to next word and persist server-side
    config['current_word_index'] += 1

    # Check if quiz is complete
    is_complete = config['current_word_index'] >= len(config['selected_words'])

    if is_complete:
        # Save session data, then drop the server-side quiz state
        save_session_data(
            quiz_id,
            config['grades'],
            config['word_type'],
            len(config['selected_words']),
            len(config['correct_answers']),
            len(config['incorrect_answers']),
            [item['word'] for item in config['incorrect_answers']]
        )
        save_quiz_state(quiz_id, session['user_id'], config)
    else:
        save_quiz_state(quiz_id, session['user_id'], config)

    response_data = {
        'correct': is_correct,
        'correct_answer': current_word,
        'definition': word_dictionary[current_word]['definition'],
        'diff': diff,
        'is_complete': is_complete
    }
    
    # If not complete, add next word info for automatic progression
    if not is_complete:
        next_word = config['selected_words'][config['current_word_index']]
        response_data.update({
            'next_word': next_word,
            'next_definition': word_dictionary[next_word]['definition'],
            'next_index': config['current_word_index'] + 1,
            'total_words': len(config['selected_words'])
        })
    
    return jsonify(response_data)

@app.route('/results')
@login_required
def results():
    """Results page"""
    config = load_quiz_state(session.get('quiz_id'), session['user_id'])
    if not config:
        return redirect(url_for('setup'))

    total_words = len(config['selected_words'])
    correct_count = len(config['correct_answers'])
    incorrect_count = len(config['incorrect_answers'])
    percentage = (correct_count / total_words * 100) if total_words > 0 else 0

    return render_template('results.html',
                         total_words=total_words,
                         correct_count=correct_count,
                         incorrect_count=incorrect_count,
                         percentage=percentage,
                         incorrect_answers=config['incorrect_answers'],
                         grades=config['grades'],
                         completed_at=datetime.now().strftime('%B %-d, %Y, %-I:%M %p') if os.name != 'nt' else datetime.now().strftime('%B %d, %Y, %I:%M %p'),
                         word_dictionary=word_dictionary)

@app.route('/statistics')
@login_required
def statistics():
    """Statistics page"""
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get the logged-in user's recent sessions
            recent_sessions = conn.execute('''
                SELECT * FROM sessions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 20
            ''', (session['user_id'],)).fetchall()

            # Get the logged-in user's overall statistics
            overall_stats = conn.execute('''
                SELECT
                    COUNT(*) as total_sessions,
                    AVG(percentage) as avg_percentage,
                    SUM(total_words) as total_words_attempted,
                    SUM(correct_count) as total_correct
                FROM sessions
                WHERE user_id = ?
            ''', (session['user_id'],)).fetchone()
            
        # Top misspelled words for this user (with definitions)
        top_missed = [
            {'word': w, 'count': c, 'definition': word_dictionary[w]['definition']}
            for w, c in get_user_misses(session['user_id'], limit=10)
        ]

        return render_template('statistics.html',
                             recent_sessions=recent_sessions,
                             overall_stats=overall_stats,
                             top_missed=top_missed)
    except Exception as e:
        return render_template('statistics.html',
                             recent_sessions=[],
                             overall_stats=None,
                             top_missed=[],
                             error=str(e))

@app.route('/quiz/quit', methods=['POST'])
@login_required
def quit_quiz():
    """Abandon the current quiz and clear its server-side state."""
    clear_quiz_state(session.get('quiz_id'))
    session.pop('quiz_id', None)
    flash('Quiz ended.', 'info')
    return redirect(url_for('setup'))

@app.route('/api/word_data/<word>')
def get_word_data(word):
    """API endpoint to get word data"""
    if word in word_dictionary:
        return jsonify(word_dictionary[word])
    return jsonify({'error': 'Word not found'}), 404

@app.route('/api/available_words')
def get_available_words():
    """API endpoint to get available words for given criteria"""
    try:
        # Handle both kindergarten ('k') and regular grades (1-12)
        grade_inputs = request.args.getlist('grades')
        grades = []
        
        for grade_input in grade_inputs:
            if grade_input.lower() == 'k':
                grades.append('k')
            else:
                try:
                    grade_num = int(grade_input)
                    if 1 <= grade_num <= 12:
                        grades.append(grade_num)
                except ValueError:
                    pass
        
        word_type = request.args.get('word_type', 'r')
        available_words = build_word_pool(grades, word_type)

        return jsonify({
            'count': len(available_words),
            'words': available_words[:50] if len(available_words) > 50 else available_words
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # Dev-server-only relaxations: plain HTTP means no Secure cookies,
    # and oauthlib must be allowed to use http:// redirect URIs.
    app.config['SESSION_COOKIE_SECURE'] = False
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    init_db()
    print("Initializing Spellaroo...")
    print(f"Word dictionary loaded: {len(word_dictionary)} words")
    app.run(debug=True, host='0.0.0.0', port=5557)