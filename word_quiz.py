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

def _synthesize_speech_google(text):
    """Use Google Cloud TTS API to synthesize speech and save to file"""
    try:
        # Generate filename
        filename = _generate_audio_filename(text)
        filepath = os.path.join('voice_files', filename)
        
        # Check if file already exists
        if os.path.exists(filepath):
            return filepath
        
        # Ensure voice_files directory exists
        os.makedirs('voice_files', exist_ok=True)
        
        # Try to use Google Cloud TTS API if properly configured
        google_audio = _try_google_cloud_tts(text)
        if google_audio:
            with open(filepath, 'wb') as f:
                f.write(google_audio)
            # Uncomment the line below for debugging TTS generation
            # print(f"Generated {filename} using Google Cloud TTS")
            return filepath
        
        # Fallback to espeak if Google TTS fails
        # Uncomment the line below for debugging TTS generation
        # print(f"Google TTS not available. Using espeak to generate {filename}")
        
        # Use espeak to generate the audio file as a fallback
        result = subprocess.run([
            'espeak', 
            text, 
            '-w', filepath,  # Write to file
            '-s', '150',     # Speed
            '-p', '50'       # Pitch
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(filepath):
            return filepath
        else:
            print(f"Failed to generate audio file: {result.stderr}")
            return None
        
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

def say(text: str, pitch: int=70) -> int:
    """Convert text to speech using cached audio files (preferred) or espeak fallback."""
    global _use_google_tts
    
    if _use_google_tts:
        # Try to use cached/generated audio files first
        audio_file = _synthesize_speech_google(text)
        if audio_file:
            return _play_audio_file(audio_file)
        else:
            print("Audio file generation failed, falling back to espeak")
            _use_google_tts = False  # Disable for subsequent calls
    
    # Fallback to espeak
    return subprocess.run(['espeak', f'-p {pitch}', text]).returncode

# List of words to be used for the quiz
word_list = [
    "adventure", "bicycle", "calendar", "delicious", "elephant", "fierce", 
    "gentle", "hurricane", "island", "journey", "knowledge", "library", 
    "mountain", "nervous", "ocean", "puzzle", "question", "robot", "school", 
    "thunder", "umbrella", "vacation", "window", "yellow", "zookeeper", "athlete", 
    "brave", "celebrate", "dictionary", "excited", "favorite", "guitar", "holiday", 
    "ingredient", "jealous", "kindness", "letter", "melody", "nature", "ocean", 
    "peaceful", "quarter", "rainbow", "surprise", "trust", "unusual", "victory", 
    "wonder", "xylophone", "youthful"
]

sight_word_dictionary = {
    1:["after", "again", "an", "any", "as",
    "ask", "by", "could", "every", "fly",
    "from", "give", "going", "had", "has",
    "her", "him", "his", "how", "just",
    "know", "let", "live", "may", "of",
    "old", "once", "open", "over", "put",
    "round", "some", "stop", "take", "thank",
    "them", "then", "think", "walk", "were",
    "when"],
    2:["always", "around", "because", "been", "before",
    "best", "both", "buy", "call", "cold",
    "does", "don’t", "fast", "first", "five",
    "found", "gave", "goes", "green", "its",
    "made", "many", "off", "or", "pull",
    "read", "right", "sing", "sit", "sleep",
    "tell", "their", "these", "those", "upon",
    "us", "use", "very", "wash", "which",
    "why", "wish", "work", "would", "write",
    "your", "again", "always", "because", "been"],
    3:["about", "better", "bring", "carry", "clean",
    "cut", "done", "draw", "drink", "eight",
    "fall", "far", "full", "got", "grow",
    "hold", "hot", "hurt", "if", "keep",
    "kind", "laugh", "light", "long", "much",
    "myself", "never", "only", "own", "pick",
    "seven", "shall", "show", "six", "small",
    "start", "ten", "today", "together", "try",
    "warm"],
    4:["area", "ago", "box", "became", "certain",
    "color", "continue", "correct", "course", "decided",
    "dog", "dry", "ever", "fact", "finally",
    "fish", "friends", "green", "half", "heart",
    "horse", "hundred", "knew", "listen", "mouth",
    "music", "open", "order", "passed", "piece",
    "plan", "poor", "products", "remember", "room",
    "rock", "shown", "six", "slowly", "stay",
    "street", "strong", "surface", "system", "tail",
    "teacher", "team", "term", "themselves", "wait"],
    5:["afternoon", "amount", "am", "bill", "broken",
    "building", "busy", "carefully", "circle", "clothes",
    "cold", "company", "condition", "corner", "cover",
    "describe", "diagram", "direction", "energy", "engine",
    "experiment", "express", "field", "figure", "fraction",
    "increase", "instrument", "invented", "kill", "middle",
    "moment", "object", "perhaps", "position", "president",
    "problem", "quarter", "receive", "region", "repeat",
    "section", "sense", "serve", "solution", "special",
    "syllables", "temperature", "thousand", "village", "weight",
    "written", "wrong"],
    6: ["addition", "agree", "allow", "alphabet", "amaze",
    "angle", "appear", "apple", "arrive", "axis",
    "base", "belong", "broad", "building", "captain",
    "cent", "column", "compound", "continent", "control",
    "cool", "cost", "decide", "design", "different",
    "division", "dollar", "entire", "equal", "event",
    "exact", "expect", "explain", "famous", "fig",
    "forward", "fresh", "guess", "hat", "heavy",
    "include", "industry", "level", "material", "modern",
    "nation", "noun", "object", "paint", "pair",
    "paragraph", "planet", "plural", "poem", "police",
    "power", "produce", "properties", "protect", "provide",
    "raise", "represent", "root", "select", "separate",
    "sharp", "silent", "similar", "solution", "space",
    "straw", "symbol", "syllable", "system", "temperature",
    "though", "tiny", "triangle", "underline", "valley",
    "view", "visit", "wide", "wild", "wire",
    "worth", "written"],
    7: ["accurate", "active", "actual", "additional", "adjective",
    "affect", "allowance", "angle", "announced", "annual",
    "arrangement", "audience", "average", "balance", "barely",
    "beyond", "border", "capital", "century", "character",
    "circumference", "citizen", "community", "compare", "complete",
    "compound", "conclude", "connected", "consider", "contain",
    "continent", "contrast", "control", "coordinate", "current",
    "definition", "describe", "determine", "difference", "direction",
    "distance", "diverse", "energy", "equation", "evidence",
    "example", "examine", "factor", "figure", "fraction",
    "function"],
    8: ["ability", "absence", "accept", "account", "achievement",
    "active", "addition", "adventure", "ambitious", "analyze",
    "announce", "approach", "arrange", "article", "atmosphere",
    "attention", "audience", "available", "behavior", "beneath",
    "benefit", "calculate", "cause", "challenge", "citizen",
    "collect", "combine", "communicate", "compare", "complex",
    "conclusion", "connection", "consequence", "constant", "construct",
    "context", "contrast", "contribute", "creative", "culture",
    "debate", "decade", "declare", "demonstrate", "describe",
    "develop", "difference", "direction", "discover", "discussion"],
    9: ["abstract", "analyze", "approach", "argument", "assume",
    "category", "circumstance", "clarify", "coherent", "complexity",
    "component", "concept", "conclusion", "consequence", "construct",
    "contrast", "criteria", "data", "define", "derive",
    "dimension", "distinguish", "evaluate", "evidence", "factor",
    "function", "identify", "impact", "imply", "indicate",
    "interpret", "issue", "logical", "method", "occur",
    "perspective", "policy", "principle", "process", "reaction",
    "relevant", "research", "respond", "role", "section",
    "significant", "source", "structure", "theory", "variable"],
    10: ["analyze", "anticipate", "approximate", "articulate", "assess",
    "assume", "cite", "coincide", "compare", "compose",
    "concentrate", "conclude", "contrast", "correspond", "criteria",
    "debate", "deduce", "demonstrate", "derive", "determine",
    "differentiate", "distribute", "emphasize", "evaluate", "examine",
    "exceed", "explicit", "formulate", "hypothesis", "illustrate",
    "imply", "infer", "integrate", "interpret", "investigate",
    "justify", "maintain", "modify", "outcome", "parameter",
    "predict", "process", "proportion", "qualitative", "quantitative",
    "relevant", "research", "significance", "theory", "valid"]}

non_sight_word_dictionary = {
    1:["cat", "dog", "sun", "hat", "bed",
    "fish", "run", "top", "man", "pen",
    "red", "big", "cup", "pig", "log",
    "bag", "box", "jam", "milk", "rain",
    "boat", "tree", "corn", "cake", "blue",
    "jump", "sand", "rock", "shell", "grass",
    "snow", "light", "hand", "foot", "bell",
    "ring", "toy", "farm", "moon", "bird",
    "apple", "duck", "frog", "shoe", "farm",
    "king", "leaf", "nest", "star", "wagon"],
    2:["apple", "basket", "bright", "candy", "circle",
    "climb", "corner", "cotton", "dishes", "doctor",
    "dragon", "family", "farmer", "feather", "forest",
    "happy", "happen", "heavy", "hilltop", "honey",
    "jumping", "kitten", "ladder", "little", "market",
    "middle", "morning", "music", "openly", "painted",
    "paper", "pencil", "present", "rabbit", "riding",
    "school", "shadow", "silver", "smile", "snowy",
    "spider", "spring", "summer", "teacher", "thunder",
    "tiger", "turtle", "window", "winter", "yellow"],
    3:["afternoon", "almost", "animal", "basketball", "beautiful",
    "birthday", "bottle", "brother", "butterfly", "camera",
    "captain", "careful", "cheerful", "children", "climate",
    "cloudy", "country", "decided", "delicious", "different",
    "elephant", "excited", "family", "favorite", "forgotten",
    "friendly", "garden", "goldfish", "happen", "important",
    "inside", "jungle", "library", "mountain", "neighbor",
    "outside", "painter", "parade", "planet", "pocket",
    "question", "remember", "snowflake", "special", "station",
    "stronger", "summer", "teacher", "weather", "window"],
    4:["adventure", "apartment", "argument", "attention", "balance",
    "believe", "calendar", "careless", "category", "celebrate",
    "comfortable", "community", "consider", "curious", "decimal",
    "delicious", "direction", "discover", "education", "electric",
    "energy", "enormous", "favorite", "fraction", "freedom",
    "gentle", "history", "imagine", "important", "include",
    "library", "measurement", "memory", "minute", "mountain",
    "necessary", "neighbor", "pattern", "population", "position",
    "practice", "president", "promise", "purpose", "question",
    "sentence", "sincere", "special", "village", "weather"],
    5:["accurate", "active", "adventure", "ancient", "apology",
    "argument", "attention", "average", "behavior", "biology",
    "calculate", "career", "challenge", "character", "chemical",
    "colony", "communicate", "community", "compare", "complete",
    "comprehend", "conclusion", "conductor", "consider", "continent",
    "contrast", "creative", "curiosity", "decade", "decision",
    "democracy", "develop", "distance", "enormous", "equation",
    "excellent", "familiar", "fortunate", "function", "geography",
    "government", "grammar", "history", "imagination", "influence",
    "language", "measurement", "memory", "organism", "paragraph"],
    6:["abundant", "accurately", "adaptation", "ambition", "analysis",
    "ancestor", "apparent", "approach", "atmosphere", "attribute",
    "barrier", "beneficial", "calculate", "campaign", "category",
    "civilization", "collapse", "colony", "communicate", "competition",
    "conclusion", "consequence", "construct", "contrast", "convert",
    "critical", "culture", "declare", "determine", "develop",
    "discovery", "diversity", "efficient", "environment", "equation",
    "evidence", "experiment", "expression", "formation", "function",
    "gravity", "heritage", "importance", "independent", "influence",
    "molecule", "narrative", "perspective", "reaction", "tremendous"],
    7:["achievement", "adaptation", "advantage", "ambiguous", "analyze",
    "apparatus", "application", "argumentative", "artificial", "assumption",
    "atmosphere", "behavioral", "calculation", "capability", "category",
    "chronological", "circumstance", "collaboration", "colleague", "complexity",
    "component", "comprehensive", "consequence", "constellation", "contamination",
    "criteria", "data", "debate", "decision", "demonstration",
    "destination", "developed", "discipline", "distribute", "efficient",
    "elaborate", "elementary", "environmental", "essential", "evaluate",
    "evolution", "foundation", "hypothesis", "illustration", "influence",
    "interpretation", "literature", "magnitude", "phenomenon", "significance"],
    8:["adaptation", "advantageous", "agriculture", "analysis", "anticipate",
    "apparatus", "approximate", "architecture", "argumentative", "articulate",
    "assertive", "association", "attribute", "authentic", "biological",
    "circumstance", "collaboration", "commitment", "component", "comprehensive",
    "conceptual", "conservation", "consideration", "contamination", "cooperation",
    "correspondence", "definition", "description", "distribution", "efficiency",
    "elaboration", "environmental", "evaluation", "exaggeration", "explanation",
    "foundation", "hypothesis", "illustration", "independent", "influence",
    "interpretation", "justification", "measurement", "methodology", "organization",
    "perspective", "phenomenon", "preparation", "significance", "theoretical"],
    9:["acknowledge", "adaptation", "advocate", "aesthetic", "ambiguous",
    "analyze", "anomaly", "antagonist", "approximate", "articulate",
    "assertion", "assumption", "authenticity", "bias", "brevity",
    "chronological", "coincidence", "compromise", "connotation", "correlation",
    "credibility", "deduction", "demonstration", "depict", "discrepancy",
    "distortion", "elaboration", "empirical", "epiphany", "evaluate",
    "exposition", "figurative", "foreshadow", "hypothesis", "illustrate",
    "implication", "inference", "integrate", "intuition", "irony",
    "juxtaposition", "metaphor", "notion", "objective", "paradox",
    "preliminary", "rationale", "redundant", "symbolism", "transition"],
    10:["aberration", "abstracted", "acquisition", "adversity", "allegory",
    "allusion", "analytical", "anecdote", "antithesis", "arbitrary",
    "assertive", "belligerent", "benevolent", "camaraderie", "catalyst",
    "chronology", "cohesive", "compliance", "condone", "connotation",
    "convergence", "credibility", "decipher", "delineate", "denotation",
    "detrimental", "dichotomy", "discernment", "eloquence", "empirical",
    "ephemeral", "erroneous", "fallacy", "feasible", "fundamental",
    "hierarchy", "ideology", "imperative", "incessant", "inevitable",
    "meticulous", "negligible", "objective", "omniscient", "paradoxical",
    "peripheral", "pertinent", "plausible", "precursor", "synthesis"]}

def spellitout(word):
    # Replace 's' characters with 'ess' for better pronunciation
    spelled_letters = []
    for letter in word:
        if letter.lower() == 's':
            spelled_letters.append('ess')
        else:
            spelled_letters.append(letter)
    return ", ".join(spelled_letters)

def printandsay(text, refresh=False):
    print(text)
    return say(text, refresh)

def get_grade_levels():
    """Get grade levels from user input"""
    while True:
        try:
            grade_input = input("What grade levels do you want? (Enter comma-separated numbers 1-10, e.g., '1,2,3'): ").strip()
            grades = [int(g.strip()) for g in grade_input.split(',')]
            
            # Validate grade levels
            valid_grades = [g for g in grades if 1 <= g <= 10]
            if not valid_grades:
                print("Please enter valid grade levels between 1 and 10.")
                continue
            if len(valid_grades) != len(grades):
                print("Some invalid grades were ignored. Using:", valid_grades)
            
            return valid_grades
        except ValueError:
            print("Please enter valid numbers separated by commas.")

def get_word_type():
    """Get word type preference from user"""
    while True:
        word_type = input("What type of words do you want?\n"
                         "o: non sight words\n"
                         "s: sight words\n"
                         "f: 50/50 mix of sight words and non sight words\n"
                         "r: random mix of sight words and non sight words\n"
                         "Enter your choice: ").strip().lower()
        
        if word_type in ['o', 's', 'f', 'r']:
            return word_type
        else:
            print("Please enter 'o', 's', 'f', or 'r'.")

def build_word_pool(grades, word_type):
    """Build word pool based on grade levels and word type"""
    sight_words = []
    non_sight_words = []
    
    # Collect words from selected grade levels
    for grade in grades:
        if grade in sight_word_dictionary:
            sight_words.extend(sight_word_dictionary[grade])
        if grade in non_sight_word_dictionary:
            non_sight_words.extend(non_sight_word_dictionary[grade])
    
    # Remove duplicates
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

# Function to quiz the user
def quiz_game():
    # Get user preferences
    grades = get_grade_levels()
    word_type = get_word_type()
    
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
    for word in selected_words:
        time.sleep(0.2)
        say("spell " + word)
        
        # Get the user's spelling attempt without showing the word
        while True:
            user_input = input("Spell the word you just heard (or type '?' to hear it again):\n").strip().lower()
            
            if user_input == "?":
                say( word)
                continue
            else:
                break
        
        if user_input == word:
            score += 1
            engine = printandsay("Correct!\n")

        else:
            incorrect_words.append(word)  # Add to incorrect words list
            print(f"Incorrect. The correct spelling is: {word}\n")
            
            say("Incorrect. " + word + " is spelled: " +spellitout(word))  # audio feedback
        
    
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
            print(f"  - {word}")

# Start the quiz
if __name__ == "__main__":
    printandsay("Welcome to the Spelling Quiz Game!", refresh=False)
    quiz_game()
