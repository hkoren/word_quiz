import random
import os
import time
import subprocess
import json
import hashlib
import requests
import base64
import warnings
import logging
import sys
from datetime import datetime, timedelta


# Import word lists from separate module

print(f"Loading word list...",end='')
from word_lists import word_dictionary
print(f"{len(word_dictionary)} words loaded")

# More aggressive stderr suppression for Google Cloud warnings
import tempfile

# Create a temporary file to redirect stderr during Google Cloud operations
_devnull = open(os.devnull, 'w')

# Comprehensive Google Cloud and gRPC message suppression
os.environ['GRPC_VERBOSITY'] = 'NONE'
os.environ['GRPC_TRACE'] = ''
os.environ['GOOGLE_CLOUD_LOGGING_ENABLED'] = 'false'
os.environ['GLOG_minloglevel'] = '3'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Suppress pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Suppress warnings
warnings.filterwarnings('ignore')

# Suppress Google Cloud logging warnings
logging.getLogger('google').setLevel(logging.CRITICAL)
logging.getLogger('grpc').setLevel(logging.CRITICAL)
logging.getLogger('absl').setLevel(logging.CRITICAL)

import pygame

# Pre-import Google Cloud modules
try:
    from google.cloud import texttospeech
    from google.oauth2 import service_account
except:
    pass

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Global variable to store authentication token
_auth_token = None
_use_google_tts = True  # Set to False to use espeak instead

def _get_oauth_token():
    """Get OAuth token using the credentials from voiceAPI.json"""
    global _auth_token
    
    if _auth_token is None:
        try:
            with open('voiceAPI.json', 'r') as f:
                credentials = json.load(f)["installed"]
            
            # For simplicity in this demo, we'll create a basic implementation
            # In production, you'd want proper OAuth2 flow with refresh tokens
            print("Note: This implementation uses a simplified approach.")
            print("For production use, implement proper OAuth2 flow with refresh tokens.")
            
            # Since we have OAuth2 client credentials, we'll use a different approach
            # We'll try to use a simple API key approach instead
            project_id = credentials.get("project_id", "spellng-quiz")
            
            # For now, we'll store the project ID for potential future use
            _auth_token = project_id
            
        except Exception as e:
            print(f"Failed to get OAuth token: {e}")
            _auth_token = False
    
    return _auth_token if _auth_token is not False else None

def _generate_audio_filename(text):
    """Generate a consistent filename for the given text"""
    # Create a hash of the text for consistent filenames
    text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
    # Clean the text for use in filename (keep only alphanumeric and some special chars)
    clean_text = ''.join(c for c in text if c.isalnum() or c in ' -_').strip()
    # Limit length and replace spaces with underscores
    clean_text = clean_text[:30].replace(' ', '_')
    return f"{clean_text}_{text_hash}.wav"

def _parse_speech_components(text):
    """Parse text into cacheable components, keeping multi-word phrases together except letter sequences"""
    import re
    
    # Handle letter sequences like "c, a, t" - split into individual letters for maximum reuse
    letter_pattern = r'\b[a-zA-Z](?:\s*[, ]\s*[a-zA-Z])+\b'
    if re.search(letter_pattern, text):
        components = []
        parts = re.split(f'({letter_pattern})', text)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            if re.match(letter_pattern, part):
                # Split letter sequence into individual letters for caching
                letters = re.findall(r'[a-zA-Z]', part)
                components.extend(letters)
            else:
                # Recursively parse non-letter parts
                components.extend(_parse_speech_components(part))
        
        return components
    
    # For non-letter sequences, keep the entire phrase together as a single component
    # This preserves natural speech for phrases like:
    # "Welcome to the Spelling Quiz Game!"
    # "Keep practicing to improve your spelling!"
    # "Your score: 5 out of 10"
    # "Incorrect. The correct spelling is:"
    return [text]

def _should_cache_component(component):
    """Determine if a component should be cached (individual words and letters should be)"""
    # Always cache individual letters
    if len(component) == 1 and component.isalpha():
        return True
    
    # Always cache individual words (for reuse across different phrases)
    if component.isalpha() and ' ' not in component:
        return True
    
    # Cache common punctuation
    if component in '.,!?:':
        return True
    
    # Cache short phrases and numbers
    if len(component) <= 20:
        return True
    
    # Don't cache very long phrases - they're less likely to be reused
    return True

def _synthesize_speech_google(text):
    """Use Google Cloud TTS API with component-based caching for maximum efficiency"""
    try:
        # Parse text into cacheable components
        components = _parse_speech_components(text)
        
        if len(components) == 1:
            # Single component - handle normally
            component = components[0]
            should_cache = _should_cache_component(component)
            
            if should_cache:
                # Generate filename for cached content
                filename = _generate_audio_filename(component)
                filepath = os.path.join('voice_files', filename)
                
                # Ensure voice_files directory exists
                os.makedirs('voice_files', exist_ok=True)
                
                # Check if cached file exists
                if os.path.exists(filepath):
                    return filepath
                
                # Generate and cache new file
                google_audio = _try_google_cloud_tts(component)
                if google_audio:
                    with open(filepath, 'wb') as f:
                        f.write(google_audio)
                    return filepath
            else:
                # Generate temporary file
                google_audio = _try_google_cloud_tts(component)
                if google_audio:
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                        temp_file.write(google_audio)
                        return temp_file.name
        else:
            # Multiple components - cache each individually and combine during playback
            component_files = []
            
            for component in components:
                should_cache = _should_cache_component(component)
                
                if should_cache:
                    filename = _generate_audio_filename(component)
                    filepath = os.path.join('voice_files', filename)
                    
                    # Ensure voice_files directory exists
                    os.makedirs('voice_files', exist_ok=True)
                    
                    if os.path.exists(filepath):
                        component_files.append(filepath)
                    else:
                        # Generate and cache component
                        google_audio = _try_google_cloud_tts(component)
                        if google_audio:
                            with open(filepath, 'wb') as f:
                                f.write(google_audio)
                            component_files.append(filepath)
                        else:
                            return None  # Failed to generate component
                else:
                    # Generate temporary file for non-cacheable component
                    google_audio = _try_google_cloud_tts(component)
                    if google_audio:
                        import tempfile
                        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                            temp_file.write(google_audio)
                            component_files.append(temp_file.name)
                    else:
                        return None  # Failed to generate component
            
            # Return list of component files for sequential playback
            return component_files
        
        # Google TTS not available - signal to use espeak
        return None
        
    except Exception as e:
        print(f"Speech synthesis failed: {e}")
        return None
    """Use Google Cloud TTS API to synthesize speech and save to file, or use espeak without caching"""
    try:
        # Generate filename
        filename = _generate_audio_filename(text)
        filepath = os.path.join('voice_files', filename)
        
        # Ensure voice_files directory exists
        os.makedirs('voice_files', exist_ok=True)
        
        # Try to use Google Cloud TTS API if properly configured
        google_audio = _try_google_cloud_tts(text)
        if google_audio:
            # For Google TTS, check if file already exists (caching enabled)
            if os.path.exists(filepath):
                return filepath
            
            # Generate new Google TTS file
            with open(filepath, 'wb') as f:
                f.write(google_audio)
            # Uncomment the line below for debugging TTS generation
            # print(f"Generated {filename} using Google Cloud TTS")
            return filepath
        
        # Fallback to espeak - NO CACHING (always regenerate)
        # Uncomment the line below for debugging TTS generation
        # print(f"Google TTS not available. Using espeak (no caching)")
        
        # For espeak, don't use cached files - always generate fresh
        # This ensures espeak files don't take up permanent storage space
        # and allows for real-time pronunciation adjustments
        return None  # Signal that we should use espeak directly without file caching
        
    except Exception as e:
        print(f"Speech synthesis failed: {e}")
        return None

def _try_google_cloud_tts(text):
    """Try to use Google Cloud TTS API with service account credentials"""
    try:
        # Check if we have service account credentials
        service_account_path = None
        
        # Look for service account file in common locations
        possible_paths = [
            'service-account-key.json',
            'google-credentials.json',
            os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '')
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                service_account_path = path
                break
        
        if not service_account_path:
            # Try to create service account from voiceAPI.json if it's the right format
            with open('voiceAPI.json', 'r') as f:
                creds = json.load(f)
            
            # Check if this looks like a service account file
            if isinstance(creds, dict) and creds.get('type') == 'service_account':
                service_account_path = 'voiceAPI.json'
            else:
                return None  # OAuth2 credentials, not service account
        
        # Try to use Google Cloud TTS
        try:
            # Suppress stderr at file descriptor level during API calls
            import sys
            old_stderr_fd = os.dup(2)  # Save stderr file descriptor
            devnull_fd = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull_fd, 2)  # Redirect stderr to devnull
            
            try:
                # Modules are already imported at module level
                # Load service account credentials
                credentials = service_account.Credentials.from_service_account_file(service_account_path)
                client = texttospeech.TextToSpeechClient(credentials=credentials)
                
                # Set up the synthesis request
                synthesis_input = texttospeech.SynthesisInput(text=text)
                
                # Configure voice settings (US English, standard voice)
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
                    name="en-US-Standard-C"  # Standard female voice
                )
                
                # Configure audio format
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                    sample_rate_hertz=24000
                )
                
                # Perform the text-to-speech request
                response = client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                
                return response.audio_content
                
            finally:
                # Always restore stderr
                os.dup2(old_stderr_fd, 2)
                os.close(old_stderr_fd)
                os.close(devnull_fd)
                
        except ImportError:
            # Google Cloud TTS library not available - silent fallback
            return None
        except Exception as e:
            # Google Cloud TTS API call failed - silent fallback  
            return None
            
    except Exception as e:
        # Error setting up Google Cloud TTS - silent fallback
        return None

def _play_audio_file(filepath):
    """Play audio file using pygame"""
    try:
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        
        # Wait for playback to complete
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        
        return 0  # Success
    except Exception as e:
        print(f"Failed to play audio file {filepath}: {e}")
        return 1  # Error

def play_sound_effect(filename):
    """Play a sound effect file"""
    try:
        if os.path.exists(filename):
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
        else:
            print(f"Sound file not found: {filename}")
    except Exception as e:
        print(f"Failed to play sound effect {filename}: {e}")

def compare_spellings(correct_word, user_input):
    """Compare correct spelling with user input and return highlighted version"""
    if not user_input:
        return correct_word.upper() if correct_word else ""
    if not correct_word:
        return ""
    
    correct = correct_word.lower()
    user = user_input.lower()
    
    # Use dynamic programming to find optimal alignment
    def find_alignment(s1, s2):
        """Find the best alignment between correct word and user input"""
        m, n = len(s1), len(s2)
        
        # DP table: dp[i][j] = minimum edit distance between s1[:i] and s2[:j]
        dp = [[float('inf')] * (n + 1) for _ in range(m + 1)]
        
        # Base cases
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        # Fill the DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]  # Match - no cost
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],      # Delete from s1 (missing char)
                        dp[i][j-1],      # Insert to s1 (extra char in user input)
                        dp[i-1][j-1]     # Substitute
                    )
        
        # Backtrack to find the alignment
        alignment = []
        i, j = m, n
        
        while i > 0 or j > 0:
            if i > 0 and j > 0 and s1[i-1] == s2[j-1]:
                # Match
                alignment.append((s1[i-1], True))
                i -= 1
                j -= 1
            elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 1:
                # Substitution - mark as incorrect
                alignment.append((s1[i-1], False))
                i -= 1
                j -= 1
            elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
                # Deletion - character missing from user input
                alignment.append((s1[i-1], False))
                i -= 1
            else:
                # Insertion - extra character in user input, skip it
                j -= 1
        
        return list(reversed(alignment))
    
    # Get the alignment
    alignment = find_alignment(correct, user)
    
    # Build the highlighted result
    highlighted = ""
    for char, is_correct in alignment:
        if is_correct:
            highlighted += char.lower()  # Correct characters in lowercase
        else:
            highlighted += char.upper()  # Incorrect/missing characters in uppercase
    
    return highlighted

def say(text: str, pitch: int=70) -> int:
    """Convert text to speech using component-based Google TTS caching, or espeak without caching."""
    global _use_google_tts
    
    if _use_google_tts:
        # Try to use component-based Google TTS with smart caching
        audio_result = _synthesize_speech_google(text)
        if audio_result:
            if isinstance(audio_result, list):
                # Multiple component files - play them sequentially
                for audio_file in audio_result:
                    result = _play_audio_file(audio_file)
                    if result != 0:
                        return result
                    
                    # Add small pause between components for natural speech
                    import time
                    time.sleep(0.1)
                
                # Clean up temporary files
                for audio_file in audio_result:
                    if audio_file.startswith('/tmp') or 'tmp' in audio_file:
                        try:
                            os.unlink(audio_file)
                        except:
                            pass
                
                return 0  # Success
            else:
                # Single file - play it
                result = _play_audio_file(audio_result)
                
                # Clean up temporary files (non-cached files)
                if audio_result.startswith('/tmp') or 'tmp' in audio_result:
                    try:
                        os.unlink(audio_result)
                    except:
                        pass
                
                return result
        else:
            # Google TTS not available - use espeak directly without caching
            print(f"Google TTS failed for: '{text}' - falling back to espeak")
            pass
    else:
        print("Google TTS disabled - using espeak")
    
    # Use espeak directly (no file caching)
    return subprocess.run(['espeak', f'-p {pitch}', text]).returncode

# Function to spell out a word with commas
def spellitout(word):
    return " ".join(word)

def printandsay(text, refresh=False):
    print(text)
    return say(text, refresh)

def load_defaults():
    """Load default settings from defaults.json"""
    try:
        if os.path.exists('defaults.json'):
            with open('defaults.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading defaults: {e}")
    
    # Return default values if file doesn't exist or can't be read
    return {
        'grade_levels': [3, 4, 5],
        'word_type': 'r'
    }

def save_defaults(grade_levels, word_type):
    """Save default settings to defaults.json"""
    try:
        defaults = {
            'grade_levels': grade_levels,
            'word_type': word_type
        }
        with open('defaults.json', 'w') as f:
            json.dump(defaults, f, indent=2)
    except Exception as e:
        print(f"Error saving defaults: {e}")

def get_grade_levels():
    """Get grade levels from user input"""
    defaults = load_defaults()
    default_grades = defaults['grade_levels']
    default_str = ','.join(str(g) for g in default_grades)
    
    while True:
        try:
            grade_input = input(f"What grade levels do you want? (Enter 'k' for kindergarten or numbers 1-12, e.g., 'k,1,2' or '9,10,11,12') [enter for {default_str}]: ").strip()
            
            # If user just hits enter, use defaults
            if not grade_input:
                return default_grades
            
            grades = []
            for g in grade_input.split(','):
                g = g.strip().lower()
                if g == 'k':
                    grades.append('k')
                else:
                    try:
                        grade_num = int(g)
                        if 1 <= grade_num <= 12:
                            grades.append(grade_num)
                        else:
                            print(f"Grade {grade_num} is out of range (valid: k, 1-12)")
                    except ValueError:
                        print(f"Invalid grade: '{g}' (valid: k, 1-12)")
            
            if not grades:
                print("Please enter valid grade levels (k for kindergarten, 1-12 for grades).")
                continue
            
            return grades
        except Exception as e:
            print("Please enter valid grade levels separated by commas (e.g., 'k,1,2' or '5,6,7').")

def get_word_type():
    """Get word type preference from user"""
    defaults = load_defaults()
    default_type = defaults['word_type']
    
    # Map word type codes to descriptions for the default display
    type_descriptions = {
        'o': 'non sight words',
        's': 'sight words', 
        'f': '50/50 mix',
        'r': 'random mix'
    }
    default_desc = type_descriptions.get(default_type, 'random mix')
    
    while True:
        word_type = input("What type of words do you want?\n"
                         "o: non sight words\n"
                         "s: sight words\n"
                         "f: 50/50 mix of sight words and non sight words\n"
                         "r: random mix of sight words and non sight words\n"
                         f"Enter your choice [enter for {default_type} ({default_desc})]: ").strip().lower()
        
        # If user just hits enter, use defaults
        if not word_type:
            return default_type
            
        if word_type in ['o', 's', 'f', 'r']:
            return word_type
        else:
            print("Please enter 'o', 's', 'f', or 'r'.")

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
        return sight_words
    elif word_type == 'o':  # non sight words only
        return non_sight_words
    elif word_type == 'f':  # 50/50 mix
        min_count = min(len(sight_words), len(non_sight_words))
        if min_count < 5:
            # If we don't have enough of one type, return all available
            return sight_words + non_sight_words
        else:
            # Take equal amounts from each
            return random.sample(sight_words, min_count) + random.sample(non_sight_words, min_count)
    elif word_type == 'r':  # random mix
        return sight_words + non_sight_words
    
    return []

def save_session_data(grades, word_type, correct_count, incorrect_count, incorrect_words):
    """Save quiz session data to sessions.json"""
    try:
        # Create session record
        session_data = {
            "date_time": datetime.now().isoformat(),
            "grades": grades,
            "word_type": word_type,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "incorrect_words": incorrect_words,
            "total_words": correct_count + incorrect_count
        }
        
        # Load existing sessions or create new list
        sessions_file = "sessions.json"
        if os.path.exists(sessions_file):
            with open(sessions_file, 'r') as f:
                sessions = json.load(f)
        else:
            sessions = []
        
        # Add new session
        sessions.append(session_data)
        
        # Save updated sessions
        with open(sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
        
        print(f"Session saved to {sessions_file}")
        
    except Exception as e:
        print(f"Failed to save session data: {e}")

def show_play_statistics():
    """Display comprehensive play statistics from sessions.json"""
    try:
        sessions_file = "sessions.json"
        if not os.path.exists(sessions_file):
            print("No session data available yet.")
            return
        
        with open(sessions_file, 'r') as f:
            sessions = json.load(f)
        
        if not sessions:
            print("No session data available yet.")
            return
        
        # Calculate date one week ago
        one_week_ago = datetime.now() - timedelta(days=7)
        
        # Initialize counters
        total_sessions = len(sessions)
        sessions_last_week = 0
        total_correct = 0
        total_words = 0
        correct_last_week = 0
        words_last_week = 0
        all_incorrect_words = []
        
        # Process each session
        for session in sessions:
            session_date = datetime.fromisoformat(session["date_time"])
            
            # Add to totals
            total_correct += session["correct_count"]
            total_words += session["total_words"]
            all_incorrect_words.extend(session["incorrect_words"])
            
            # Check if session is within last week
            if session_date >= one_week_ago:
                sessions_last_week += 1
                correct_last_week += session["correct_count"]
                words_last_week += session["total_words"]
        
        # Calculate percentages
        overall_percentage = (total_correct / total_words * 100) if total_words > 0 else 0
        week_percentage = (correct_last_week / words_last_week * 100) if words_last_week > 0 else 0
        
        # Count misspelled words and get top 10
        from collections import Counter
        misspelled_counter = Counter(all_incorrect_words)
        top_misspelled = misspelled_counter.most_common(10)
        
        # Display statistics
        print("\n" + "="*50)
        print("PLAY STATISTICS")
        print("="*50)
        print(f"Total sessions played: {total_sessions}")
        print(f"Sessions in last week: {sessions_last_week}")
        print()
        print(f"Total words spelled correctly: {total_correct} out of {total_words}")
        print(f"Words spelled correctly (last week): {correct_last_week} out of {words_last_week}")
        print()
        print(f"Overall accuracy: {overall_percentage:.1f}%")
        if words_last_week > 0:
            print(f"Last week accuracy: {week_percentage:.1f}%")
        else:
            print("Last week accuracy: No sessions in last week")
        print()
        
        if top_misspelled:
            print("TOP 10 MISSPELLED WORDS:")
            print("-" * 30)
            for i, (word, count) in enumerate(top_misspelled, 1):
                print(f"{i:2}. {word:<15} ({count} time{'s' if count != 1 else ''})")
        else:
            print("No misspelled words recorded!")
        
        print("="*50)
        
    except Exception as e:
        print(f"Failed to display statistics: {e}")

def run_single_quiz(grades, word_type):
    """Run a single quiz game with the given settings"""
    # Build word pool
    available_words = build_word_pool(grades, word_type)
    
    if len(available_words) < 10:
        print(f"Warning: Only {len(available_words)} words available. Using all of them.")
        selected_words = available_words
    else:
        # Select 10 unique random words from the available words
        selected_words = random.sample(available_words, 10)
    
    print(f"\nStarting quiz with {len(selected_words)} words from grade levels {grades}...")
    time.sleep(1)
    
    score = 0
    incorrect_words = []  # List to store incorrectly spelled words
    
    # Loop through the selected words
    for i, word in enumerate(selected_words, 1):
        time.sleep(0.2)
        
        # Get definition from the unified dictionary
        definition = word_dictionary.get(word, {}).get('definition', 'No definition available')
        
        print(f"\n{'='*50}")
        print(f"Word {i} of {len(selected_words)}")
        print(f"{'='*50}")
        print(f"Definition: {definition}")
        print("\nListen carefully to the word...")
        
        say("spell")
        say(word)
        
        # Get the user's spelling attempt without showing the word
        while True:
            user_input = input("Spell the word you just heard (or type '?' to hear it again):\n").strip().lower()
            
            if user_input == "?":
                print(f"\nReminder - Definition: {definition}")
                say(word)
                continue
            else:
                break
        
        if user_input == word:
            score += 1
            play_sound_effect("ding.wav")
            print("Correct!\n")

        else:
            incorrect_words.append(word)  # Add to incorrect words list
            play_sound_effect("buzzer.wav")
            print(f"Incorrect.    The correct spelling is: {word}")
            
            # Show spelling comparison with highlights
            correct_highlighted_spelling = compare_spellings(word, user_input)
            incorrect_highlighted_spelling = compare_spellings(user_input, word)
            print(f"      where you went wrong in CAPITAL: {correct_highlighted_spelling}")
            print(f"compared with your incorrect spelling: {incorrect_highlighted_spelling}")
            print("(lowercase = correct, UPPERCASE = incorrect/missing)\n")
            
            say(word)
            say(" is spelled: ")
            say(spellitout(word))  # audio feedback
        
    
    # Display the final score
    printandsay(f"Your score: {score} out of 10")
    if score < 5:
        printandsay("Keep practicing to improve your spelling!")
    elif score >= 5 and score < 8:
        printandsay("Good job! You're getting better at spelling.")
    elif score == 8 or score == 9:
        printandsay("Excellent work! You're a spelling star!")
    else:
        printandsay("Perfect score! You're a spelling champion!")
    
    # Display incorrectly spelled words if any
    if incorrect_words:
        print("\nPlease work on spelling these words:")
        for word in incorrect_words:
            definition = word_dictionary.get(word, {}).get('definition', 'No definition available')
            print(f"  - {word}: {definition}")
    
    # Save session data
    correct_count = score
    incorrect_count = len(incorrect_words)
    save_session_data(grades, word_type, correct_count, incorrect_count, incorrect_words)
    
    # Show play statistics
    show_play_statistics()

def ask_play_again():
    """Ask user if they want to play again, with setup option"""
    while True:
        choice = input("\nWould you like to play again?\n"
                      "y - Yes (same settings)\n"
                      "n - No (quit)\n"
                      "s - Setup (change settings)\n"
                      "Enter your choice: ").strip().lower()
        
        if choice in ['y', 'n', 's']:
            return choice
        else:
            print("Please enter 'y', 'n', or 's'.")

def main_game_loop():
    """Main game loop that handles play again functionality"""
    printandsay("Welcome to the Spelling Quiz Game!", refresh=False)
    
    # First game - always ask for setup
    grades = get_grade_levels()
    word_type = get_word_type()
    save_defaults(grades, word_type)
    
    while True:
        # Run the quiz game with current settings
        run_single_quiz(grades, word_type)
        
        # Ask if user wants to play again
        choice = ask_play_again()
        
        if choice == 'n':
            print("Thanks for playing! Goodbye!")
            break
        elif choice == 's':
            # Get new settings
            grades = get_grade_levels()
            word_type = get_word_type()
            save_defaults(grades, word_type)
        # If choice == 'y', continue with same settings

# Start the quiz
if __name__ == "__main__" and not os.environ.get('TESTING_MODE'):    
    main_game_loop()
