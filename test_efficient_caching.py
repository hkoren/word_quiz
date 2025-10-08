#!/usr/bin/env python3
"""
Test the new efficient caching system
"""

import sys
import os
import time

# Add the current directory to the path so we can import from word_quiz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_efficient_caching():
    print("Testing efficient caching system...")
    
    # Count files before test
    voice_files_dir = "voice_files"
    if os.path.exists(voice_files_dir):
        before_count = len([f for f in os.listdir(voice_files_dir) if f.endswith('.wav')])
        before_files = set(os.listdir(voice_files_dir))
    else:
        before_count = 0
        before_files = set()
    
    print(f"Files before test: {before_count}")
    
    # Import after counting
    from word_quiz import say, _should_cache_text
    
    # Test caching decisions
    print("\n--- Testing caching decisions ---")
    test_cases = [
        ("Correct!", True, "Common phrase"),
        ("spell", True, "Common phrase"),
        ("cat", False, "Individual word"),
        ("c, a, t", False, "Letter sequence"),
        ("Welcome to the Spelling Quiz Game!", True, "Long phrase"),
        ("Incorrect. cat is spelled: c, a, t", True, "Complex phrase"),
        ("Your score: 5 out of 10", True, "Long feedback"),
        ("a", False, "Single letter"),
        ("ess", False, "Single letter spelled out")
    ]
    
    for text, expected, description in test_cases:
        result = _should_cache_text(text)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{text}' -> Cache: {result} ({description})")
    
    # Test actual speech generation
    print("\n--- Testing speech generation ---")
    
    test_phrases = [
        "Correct!",  # Should be cached
        "cat",       # Should be temporary
        "spell dog", # Should be temporary  
        "Keep practicing to improve your spelling!",  # Should be cached
        "c, a, t"    # Should be temporary
    ]
    
    for phrase in test_phrases:
        print(f"\nTesting: '{phrase}'")
        should_cache = _should_cache_text(phrase)
        print(f"   Should cache: {should_cache}")
        
        start_time = time.time()
        result = say(phrase)
        elapsed = time.time() - start_time
        print(f"   Result: {result}, Time: {elapsed:.2f}s")
    
    # Count files after test
    if os.path.exists(voice_files_dir):
        after_count = len([f for f in os.listdir(voice_files_dir) if f.endswith('.wav')])
        after_files = set(os.listdir(voice_files_dir))
        new_files = after_files - before_files
    else:
        after_count = 0
        new_files = set()
    
    print(f"\n--- Results ---")
    print(f"Files before: {before_count}")
    print(f"Files after:  {after_count}")
    print(f"New files:    {after_count - before_count}")
    
    if new_files:
        print("New cached files:")
        for filename in sorted(new_files):
            filepath = os.path.join(voice_files_dir, filename)
            size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
            print(f"   {filename} ({size} bytes)")
    
    print("\n✅ Efficient caching test completed!")
    print("Expected: Only long phrases and common words should be cached")
    print("Individual words and letter sequences should use temporary files")

if __name__ == "__main__":
    test_efficient_caching()