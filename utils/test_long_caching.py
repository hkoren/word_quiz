#!/usr/bin/env python3
"""
Test caching with longer phrases where timing difference should be more obvious
"""

import sys
import os
import time

# Add the current directory to the path so we can import from word_quiz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from word_quiz import say

def test_long_phrase_caching():
    print("Testing caching with longer phrases...")
    
    # Use a longer phrase where Google TTS generation time should be more noticeable
    long_phrase = "This is a significantly longer phrase that should take more time to generate with Google Text-to-Speech API on the first call, but should be much faster on subsequent calls when loaded from the cached file in the voice files directory."
    
    print(f"Testing phrase length: {len(long_phrase)} characters")
    
    # First call - should generate new file
    print("\n--- First call (should generate) ---")
    start_time = time.time()
    result1 = say(long_phrase)
    time1 = time.time() - start_time
    print(f"Time: {time1:.3f}s, Result: {result1}")
    
    # Second call - should use cached file
    print("\n--- Second call (should use cache) ---")
    start_time = time.time()
    result2 = say(long_phrase)
    time2 = time.time() - start_time
    print(f"Time: {time2:.3f}s, Result: {result2}")
    
    # Third call - should use cached file
    print("\n--- Third call (should use cache) ---")
    start_time = time.time()
    result3 = say(long_phrase)
    time3 = time.time() - start_time
    print(f"Time: {time3:.3f}s, Result: {result3}")
    
    # Analysis
    print(f"\nTiming Analysis:")
    print(f"First call:  {time1:.3f}s")
    print(f"Second call: {time2:.3f}s")
    print(f"Third call:  {time3:.3f}s")
    
    if time1 > time2 and time1 > time3:
        speedup = time1 / min(time2, time3)
        print(f"✅ Caching working! Speedup: {speedup:.1f}x")
    else:
        print("⚠️ Timing difference not as expected")
    
    return time1, time2, time3

if __name__ == "__main__":
    test_long_phrase_caching()