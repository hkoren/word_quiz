#!/usr/bin/env python3
"""
Test Google TTS with a new phrase to confirm it's working
"""

import sys
import os

# Add the current directory to the path so we can import from word_quiz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from word_quiz import say

def test_new_phrase():
    print("Testing Google TTS with a new phrase...")
    
    # Use a phrase that definitely doesn't exist yet
    test_phrase = "Google Cloud Text to Speech is now working perfectly"
    
    print(f"Testing phrase: '{test_phrase}'")
    result = say(test_phrase)
    print(f"Result: {result}")
    
    # Check if the file was created
    import hashlib
    text_hash = hashlib.md5(test_phrase.encode()).hexdigest()[:10]
    clean_text = ''.join(c for c in test_phrase if c.isalnum() or c in ' -_').strip()
    clean_text = clean_text[:30].replace(' ', '_')
    expected_filename = f"{clean_text}_{text_hash}.wav"
    
    filepath = os.path.join('voice_files', expected_filename)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✅ Audio file created: {expected_filename} ({size} bytes)")
        
        # Google TTS files are typically larger than espeak files
        if size > 50000:  # 50KB threshold
            print("✅ File size suggests Google TTS was used")
        else:
            print("⚠️  File size suggests espeak was used")
    else:
        print("❌ No audio file was created")

if __name__ == "__main__":
    test_new_phrase()