#!/usr/bin/env python3
"""Test the new component-based caching system"""

import os
import sys
import time

# Import the word quiz functions
from word_quiz import _parse_speech_components, _should_cache_component, say

def test_component_parsing():
    """Test how text is parsed into components"""
    print("--- Testing component parsing ---")
    
    test_cases = [
        "spell cat",
        "c, a, t",
        "Incorrect. cat is spelled: c, a, t",
        "spell dog as d, o, g",
        "The word is temperature",
        "t, e, m, p, e, r, a, t, u, r, e"
    ]
    
    for text in test_cases:
        components = _parse_speech_components(text)
        print(f"   '{text}' -> {components}")

def test_caching_decisions():
    """Test which components should be cached"""
    print("\n--- Testing caching decisions ---")
    
    test_components = [
        "spell", "cat", "dog", "temperature",  # words
        "c", "a", "t", "d", "o", "g",  # letters
        "Incorrect", "Correct", ".",  # common words/punctuation
        "Welcome to the Spelling Quiz Game!"  # long phrase
    ]
    
    for component in test_components:
        should_cache = _should_cache_component(component)
        print(f"   '{component}' -> Cache: {should_cache}")

def count_files(directory):
    """Count files in a directory"""
    try:
        return len([f for f in os.listdir(directory) if f.endswith('.wav')])
    except FileNotFoundError:
        return 0

def test_component_speech():
    """Test actual speech generation with component caching"""
    print("\n--- Testing component-based speech ---")
    
    # Count files before
    files_before = count_files('voice_files')
    print(f"Files before test: {files_before}")
    
    # Test cases that should create individual cached components
    test_phrases = [
        "spell cat",           # Should cache: "spell", "cat"
        "c, a, t",            # Should cache: "c", "a", "t" 
        "spell dog",          # Should cache: "dog" (spell already cached)
        "d, o, g",            # Should cache: "d", "o", "g"
        "Incorrect",          # Should cache: "Incorrect"
        "temperature",        # Should cache: "temperature"
        "t, e, m, p, e, r, a, t, u, r, e"  # Should cache individual letters
    ]
    
    print("\nGenerating speech components...")
    for phrase in test_phrases:
        print(f"   Testing: '{phrase}'")
        start_time = time.time()
        result = say(phrase)
        elapsed = time.time() - start_time
        print(f"      Result: {result}, Time: {elapsed:.2f}s")
        time.sleep(0.5)  # Small delay between tests
    
    # Count files after
    files_after = count_files('voice_files')
    new_files = files_after - files_before
    
    print(f"\n--- Results ---")
    print(f"Files before: {files_before}")
    print(f"Files after:  {files_after}")
    print(f"New files:    {new_files}")
    
    # List new files
    if new_files > 0:
        try:
            all_files = os.listdir('voice_files')
            wav_files = [f for f in all_files if f.endswith('.wav')]
            wav_files.sort(key=lambda x: os.path.getmtime(os.path.join('voice_files', x)), reverse=True)
            
            print("New cached components:")
            for i, filename in enumerate(wav_files[:new_files]):
                filepath = os.path.join('voice_files', filename)
                size = os.path.getsize(filepath)
                print(f"   {filename} ({size} bytes)")
        except Exception as e:
            print(f"Error listing files: {e}")
    
    print(f"\n✅ Component caching test completed!")
    print("Expected behavior:")
    print("- Individual words like 'spell', 'cat', 'dog', 'temperature' should be cached")
    print("- Individual letters like 'c', 'a', 't', 'd', 'o', 'g' should be cached")
    print("- Complex phrases should be built from cached components")
    print("- Each unique word/letter should only be generated once")

if __name__ == "__main__":
    print("Testing component-based caching system...")
    
    test_component_parsing()
    test_caching_decisions() 
    test_component_speech()