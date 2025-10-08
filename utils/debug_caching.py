#!/usr/bin/env python3
"""
Debug the caching behavior
"""

import sys
import os

# Add the current directory to the path so we can import from word_quiz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from word_quiz import _synthesize_speech_google, _generate_audio_filename

def debug_caching():
    print("Debugging caching behavior...")
    
    test_phrase = "Debug caching test phrase"
    
    # Check what filename would be generated
    filename = _generate_audio_filename(test_phrase)
    filepath = os.path.join('voice_files', filename)
    
    print(f"Test phrase: '{test_phrase}'")
    print(f"Generated filename: {filename}")
    print(f"Full path: {filepath}")
    print(f"File exists before call: {os.path.exists(filepath)}")
    
    # First call
    print("\n--- First call ---")
    result1 = _synthesize_speech_google(test_phrase)
    print(f"Result: {result1}")
    print(f"File exists after first call: {os.path.exists(filepath)}")
    
    # Second call
    print("\n--- Second call ---")
    result2 = _synthesize_speech_google(test_phrase)
    print(f"Result: {result2}")
    print(f"File exists after second call: {os.path.exists(filepath)}")
    
    # Check if they're the same
    if result1 == result2 and result1 == filepath:
        print("✅ Caching working correctly")
    else:
        print("❌ Caching issue detected")

if __name__ == "__main__":
    debug_caching()