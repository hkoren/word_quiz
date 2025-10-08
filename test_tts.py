#!/usr/bin/env python3
"""
Simple test script to verify the TTS caching functionality
"""

import sys
import os
import time

# Add the current directory to the path so we can import from word_quiz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from word_quiz import say

def test_caching():
    print("Testing TTS caching functionality...")
    
    # Test 1: Generate a new audio file
    print("\n1. Testing first call (should generate new file):")
    start_time = time.time()
    result = say("Hello world")
    duration1 = time.time() - start_time
    print(f"   First call took {duration1:.3f} seconds, return code: {result}")
    
    # Test 2: Use cached file (should be faster)
    print("\n2. Testing second call (should use cached file):")
    start_time = time.time()
    result = say("Hello world")
    duration2 = time.time() - start_time
    print(f"   Second call took {duration2:.3f} seconds, return code: {result}")
    
    # Test 3: Different text (should generate new file)
    print("\n3. Testing different text (should generate new file):")
    start_time = time.time()
    result = say("Goodbye world")
    duration3 = time.time() - start_time
    print(f"   Third call took {duration3:.3f} seconds, return code: {result}")
    
    print(f"\nCaching effectiveness: Second call was {duration1/duration2:.1f}x faster than first call")
    
    # List the generated files
    print("\nGenerated files in voice_files directory:")
    voice_files_dir = "voice_files"
    if os.path.exists(voice_files_dir):
        for file in os.listdir(voice_files_dir):
            if file.endswith('.wav'):
                filepath = os.path.join(voice_files_dir, file)
                size = os.path.getsize(filepath)
                print(f"   {file} ({size} bytes)")

if __name__ == "__main__":
    test_caching()