#!/usr/bin/env python3
"""
Quick test to verify the quiz functionality with a few words
"""

import sys
import os

# Add the current directory to the path so we can import from word_quiz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from word_quiz import say, spellitout

def test_quiz_functions():
    print("Testing quiz-specific functions...")
    
    # Test the say function with quiz-like phrases
    test_phrases = [
        "spell cat",
        "spell dog", 
        "Correct!",
        "Incorrect. The correct spelling is: elephant"
    ]
    
    for phrase in test_phrases:
        print(f"\nTesting: '{phrase}'")
        result = say(phrase)
        print(f"   Result: {result}")
    
    # Test the spellitout function
    print(f"\nTesting spellitout function:")
    print(f"   spellitout('cats') = '{spellitout('cats')}'")
    print(f"   spellitout('success') = '{spellitout('success')}'")
    
    # Show voice files directory
    print(f"\nVoice files generated:")
    voice_files_dir = "voice_files"
    if os.path.exists(voice_files_dir):
        files = [f for f in os.listdir(voice_files_dir) if f.endswith('.wav')]
        for file in sorted(files):
            print(f"   {file}")

if __name__ == "__main__":
    test_quiz_functions()