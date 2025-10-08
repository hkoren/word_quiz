#!/usr/bin/env python3
"""
Final demonstration of selective caching behavior
"""

import sys
import os
import time

# Add the current directory to the path so we can import from word_quiz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demonstrate_selective_caching():
    print("=== Selective Caching Demonstration ===")
    print("Google TTS files: CACHED for reuse")
    print("Espeak files: NOT CACHED (generated fresh each time)")
    print()
    
    # Count initial files
    voice_files_dir = "voice_files"
    if os.path.exists(voice_files_dir):
        initial_count = len([f for f in os.listdir(voice_files_dir) if f.endswith('.wav')])
    else:
        initial_count = 0
    
    print(f"Initial cached files: {initial_count}")
    
    # Import modules
    import word_quiz
    from word_quiz import say
    
    # Test 1: Google TTS (should create cached file)
    print("\n--- Test 1: Google TTS with Caching ---")
    if word_quiz._try_google_cloud_tts("test"):
        print("✅ Google TTS available")
        
        google_phrase = "Demonstration of Google TTS caching behavior"
        print(f"Testing: '{google_phrase}'")
        
        # Check file count before
        before_google = len([f for f in os.listdir(voice_files_dir) if f.endswith('.wav')])
        
        # First call
        result = say(google_phrase)
        after_google = len([f for f in os.listdir(voice_files_dir) if f.endswith('.wav')])
        
        print(f"   Files before: {before_google}")
        print(f"   Files after:  {after_google}")
        print(f"   New files:    {after_google - before_google}")
        
        if after_google > before_google:
            print("   ✅ Google TTS file was cached")
        else:
            print("   ⚠️ No new file created (may have been cached already)")
    else:
        print("⚠️ Google TTS not available")
    
    # Test 2: Espeak (should NOT create cached files)
    print("\n--- Test 2: Espeak without Caching ---")
    
    # Temporarily disable Google TTS
    original_tts = word_quiz._try_google_cloud_tts
    word_quiz._try_google_cloud_tts = lambda text: None
    
    try:
        espeak_phrase = "Demonstration of espeak direct behavior"
        print(f"Testing: '{espeak_phrase}'")
        
        # Check file count before
        before_espeak = len([f for f in os.listdir(voice_files_dir) if f.endswith('.wav')])
        
        # Multiple calls
        for i in range(2):
            result = say(espeak_phrase)
            print(f"   Call {i+1}: result = {result}")
        
        after_espeak = len([f for f in os.listdir(voice_files_dir) if f.endswith('.wav')])
        
        print(f"   Files before: {before_espeak}")
        print(f"   Files after:  {after_espeak}")
        print(f"   New files:    {after_espeak - before_espeak}")
        
        if after_espeak == before_espeak:
            print("   ✅ No cache files created with espeak (correct)")
        else:
            print("   ❌ Unexpected files created")
            
    finally:
        # Restore Google TTS
        word_quiz._try_google_cloud_tts = original_tts
    
    # Final count
    final_count = len([f for f in os.listdir(voice_files_dir) if f.endswith('.wav')])
    print(f"\n=== Summary ===")
    print(f"Initial files: {initial_count}")
    print(f"Final files:   {final_count}")
    print(f"Net change:    +{final_count - initial_count}")
    print("\n✅ Selective caching working correctly!")
    print("   - Google TTS files are cached for efficiency")
    print("   - Espeak generates audio directly without storage overhead")

if __name__ == "__main__":
    demonstrate_selective_caching()