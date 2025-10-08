#!/usr/bin/env python3
"""
Test that espeak files are NOT cached by temporarily disabling Google TTS
"""

import sys
import os

# Add the current directory to the path so we can import from word_quiz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_espeak_no_caching():
    print("Testing that espeak files are NOT cached...")
    
    # Count files before test
    voice_files_dir = "voice_files"
    if os.path.exists(voice_files_dir):
        before_count = len([f for f in os.listdir(voice_files_dir) if f.endswith('.wav')])
        before_files = set(os.listdir(voice_files_dir))
    else:
        before_count = 0
        before_files = set()
    
    print(f"Files before test: {before_count}")
    
    # Import the module
    import word_quiz
    
    # Temporarily disable Google TTS to force espeak usage
    original_use_google_tts = word_quiz._use_google_tts
    word_quiz._use_google_tts = False
    
    # Also make sure the TTS function returns None to force espeak
    original_tts_func = word_quiz._try_google_cloud_tts
    word_quiz._try_google_cloud_tts = lambda text: None
    
    try:
        print("Google TTS temporarily disabled - forcing espeak usage")
        
        # Test with espeak (should not create cache files)
        test_phrase = "This phrase should use espeak without caching"
        print(f"\nTesting: '{test_phrase}'")
        
        # Multiple calls to see if files are created
        for i in range(3):
            result = word_quiz.say(test_phrase)
            print(f"   Call {i+1}: result = {result}")
        
        # Count files after test
        if os.path.exists(voice_files_dir):
            after_count = len([f for f in os.listdir(voice_files_dir) if f.endswith('.wav')])
            after_files = set(os.listdir(voice_files_dir))
        else:
            after_count = 0
            after_files = set()
        
        print(f"\nFiles after test: {after_count}")
        print(f"New files created: {after_count - before_count}")
        
        if after_count == before_count:
            print("✅ No cache files created with espeak (correct behavior)")
        else:
            new_files = after_files - before_files
            print(f"❌ Unexpected files created: {new_files}")
            
    finally:
        # Restore original settings
        word_quiz._use_google_tts = original_use_google_tts
        word_quiz._try_google_cloud_tts = original_tts_func
        print("\nGoogle TTS settings restored")

if __name__ == "__main__":
    test_espeak_no_caching()