#!/usr/bin/env python3
"""
Test the new selective caching behavior - Google TTS cached, espeak not cached
"""

import sys
import os
import time

# Add the current directory to the path so we can import from word_quiz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_selective_caching():
    print("Testing selective caching behavior...")
    
    # Count files before test
    voice_files_dir = "voice_files"
    if os.path.exists(voice_files_dir):
        before_count = len([f for f in os.listdir(voice_files_dir) if f.endswith('.wav')])
    else:
        before_count = 0
    
    print(f"Files before test: {before_count}")
    
    # Import after counting to avoid import-time file generation
    from word_quiz import say, _try_google_cloud_tts
    
    # Test 1: Check if Google TTS is available
    test_audio = _try_google_cloud_tts("test")
    if test_audio:
        print("✅ Google TTS is available - files will be cached")
        
        # Test with a new phrase that should get cached
        test_phrase = "This phrase will be cached with Google TTS"
        print(f"\nTesting: '{test_phrase}'")
        
        start_time = time.time()
        result1 = say(test_phrase)
        time1 = time.time() - start_time
        print(f"   First call: {time1:.3f}s, result: {result1}")
        
        start_time = time.time()
        result2 = say(test_phrase)
        time2 = time.time() - start_time
        print(f"   Second call: {time2:.3f}s, result: {result2}")
        
        if time1 > time2 * 2:  # Should be significantly faster on second call
            print("   ✅ Caching working - second call much faster")
        else:
            print("   ⚠️ Caching may not be working as expected")
            
    else:
        print("⚠️ Google TTS not available - testing espeak direct mode")
        
        # Test with espeak direct (no caching)
        test_phrase = "This phrase will not be cached with espeak"
        print(f"\nTesting: '{test_phrase}'")
        
        start_time = time.time()
        result1 = say(test_phrase)
        time1 = time.time() - start_time
        print(f"   First call: {time1:.3f}s, result: {result1}")
        
        start_time = time.time()
        result2 = say(test_phrase)
        time2 = time.time() - start_time
        print(f"   Second call: {time2:.3f}s, result: {result2}")
        
        print("   ✅ Espeak direct mode - no caching expected")
    
    # Count files after test
    if os.path.exists(voice_files_dir):
        after_count = len([f for f in os.listdir(voice_files_dir) if f.endswith('.wav')])
    else:
        after_count = 0
    
    print(f"\nFiles after test: {after_count}")
    print(f"New files created: {after_count - before_count}")
    
    if test_audio and after_count > before_count:
        print("✅ New Google TTS file was cached")
    elif not test_audio and after_count == before_count:
        print("✅ No new files created with espeak (as expected)")
    
    return test_audio is not None

if __name__ == "__main__":
    google_tts_available = test_selective_caching()
    
    if google_tts_available:
        print("\n🎯 Google TTS is working with selective caching")
    else:
        print("\n🔄 Using espeak direct mode (no caching)")
    
    print("\nSelective caching test completed!")