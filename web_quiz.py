#!/usr/bin/env python3
"""
Web-based Spelling Quiz Application
Flask web application for the spelling quiz game
"""

import os
import sys
import json
import random
import sqlite3
import hashlib
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

# Add the current directory to Python path to import word_lists
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from word_lists import word_dictionary

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

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
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                birth_year INTEGER NOT NULL,
                birth_month INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

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

def hash_password(password):
    """Hash password using SHA1"""
    return hashlib.sha1(password.encode('utf-8')).hexdigest()

def verify_password(password, password_hash):
    """Verify password against SHA1 hash"""
    return hashlib.sha1(password.encode('utf-8')).hexdigest() == password_hash

def create_user(name, email, password, birth_year, birth_month):
    """Create a new user account"""
    try:
        password_hash = hash_password(password)
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, email, password_hash, birth_year, birth_month)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, email, password_hash, birth_year, birth_month))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None  # Email already exists
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def authenticate_user(email, password):
    """Authenticate user by email and password"""
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, email, password_hash, birth_year, birth_month
                FROM users WHERE email = ?
            ''', (email,))
            user = cursor.fetchone()
            
            if user and verify_password(password, user[3]):
                return {
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'birth_year': user[4],
                    'birth_month': user[5]
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
                SELECT id, name, email, birth_year, birth_month
                FROM users WHERE id = ?
            ''', (user_id,))
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'birth_year': user[3],
                    'birth_month': user[4]
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
    session.clear()
    flash('You have been logged out.', 'info')
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
    except Exception as e:
        print(f"Error getting user stats: {e}")
        user_stats = {'total_quizzes': 0, 'average_score': 0, 'total_words': 0, 'total_correct': 0}
    
    return render_template('profile.html', user=user, stats=user_stats)

@app.route('/')
def index():
    """Main page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user_name=session.get('user_name'))

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
            
            # Store quiz configuration in session
            session['quiz_config'] = {
                'grades': grades,
                'word_type': word_type,
                'selected_words': selected_words,
                'current_word_index': 0,
                'correct_answers': [],
                'incorrect_answers': [],
                'start_time': datetime.now().isoformat()
            }
            
            return redirect(url_for('quiz'))
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    return render_template('setup.html')

@app.route('/quiz')
@login_required
def quiz():
    """Quiz page"""
    if 'quiz_config' not in session:
        return redirect(url_for('setup'))
    
    config = session['quiz_config']
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
    if 'quiz_config' not in session:
        return jsonify({'error': 'No active quiz session'}), 400
    
    config = session['quiz_config']
    current_index = config['current_word_index']
    
    if current_index >= len(config['selected_words']):
        return jsonify({'error': 'Quiz already completed'}), 400
    
    current_word = config['selected_words'][current_index]
    user_answer = request.json.get('answer', '').strip().lower()
    
    # Check answer
    is_correct = user_answer == current_word.lower()
    
    if is_correct:
        config['correct_answers'].append(current_word)
    else:
        config['incorrect_answers'].append({
            'word': current_word,
            'user_answer': user_answer,
            'correct_answer': current_word
        })
    
    # Move to next word
    config['current_word_index'] += 1
    session['quiz_config'] = config
    
    # Check if quiz is complete
    is_complete = config['current_word_index'] >= len(config['selected_words'])
    
    if is_complete:
        # Save session data
        save_session_data(
            session.get('session_id', 'anonymous'),
            config['grades'],
            config['word_type'],
            len(config['selected_words']),
            len(config['correct_answers']),
            len(config['incorrect_answers']),
            [item['word'] for item in config['incorrect_answers']]
        )
    
    response_data = {
        'correct': is_correct,
        'correct_answer': current_word,
        'definition': word_dictionary[current_word]['definition'],
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
    if 'quiz_config' not in session:
        return redirect(url_for('setup'))
    
    config = session['quiz_config']
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
                         grades=config['grades'])

@app.route('/statistics')
@login_required
def statistics():
    """Statistics page"""
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get recent sessions
            recent_sessions = conn.execute('''
                SELECT * FROM sessions 
                ORDER BY created_at DESC 
                LIMIT 20
            ''').fetchall()
            
            # Get overall statistics
            overall_stats = conn.execute('''
                SELECT 
                    COUNT(*) as total_sessions,
                    AVG(percentage) as avg_percentage,
                    SUM(total_words) as total_words_attempted,
                    SUM(correct_count) as total_correct
                FROM sessions
            ''').fetchone()
            
        return render_template('statistics.html',
                             recent_sessions=recent_sessions,
                             overall_stats=overall_stats)
    except Exception as e:
        return render_template('statistics.html',
                             recent_sessions=[],
                             overall_stats=None,
                             error=str(e))

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
        
        # Debug logging
        print(f"API DEBUG: grades={grades}, word_type={word_type}")
        
        available_words = build_word_pool(grades, word_type)
        
        print(f"API DEBUG: Found {len(available_words)} words")
        
        return jsonify({
            'count': len(available_words),
            'words': available_words[:50] if len(available_words) > 50 else available_words
        })
    except Exception as e:
        print(f"API ERROR: {e}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    init_db()
    print("Initializing web spelling quiz...")
    print(f"Word dictionary loaded: {len(word_dictionary)} words")
    app.run(debug=True, host='0.0.0.0', port=5557)