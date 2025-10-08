#!/usr/bin/env python3
"""Test actual speech generation with improved phrase preservation"""

import os
import sys
import time

# Set testing mode to prevent main quiz from running
os.environ['TESTING_MODE'] = '1'

# Import the speech functions
sys.path.insert(0, '.')
import word_quiz

def count_files(directory):
    """Count wav files in a directory"""
    try:
        return len([f for f in os.listdir(directory) if f.endswith('.wav')])
    except FileNotFoundError:
        return 0

def test_improved_speech_caching():
    """Test speech generation with improved phrase preservation"""
    print("--- Testing speech generation with phrase preservation ---")
    
    # Count files before
    files_before = count_files('voice_files')
    print(f"Files before test: {files_before}")
    
    # Test cases that demonstrate the improved behavior
    test_phrases = [
        # Multi-word phrases - should be cached as single units
        "Welcome to the Spelling Quiz Game!",
        "Keep practicing to improve your spelling!", 
        "Your score: 5 out of 10",
        "Excellent work! You're a spelling star!",
        
        # Single words - should be cached individually
        "spell",
        "cat", 
        "Correct!",
        
        # Letter sequences - should use individual letter caching
        "c, a, t",
        "d, o, g",
        
        # Mixed cases
        "Incorrect. cat is spelled: c, a, t"
    ]
    
    print("\nGenerating speech with improved parsing...")
    for phrase in test_phrases:
        print(f"   Testing: '{phrase}'")
        components = word_quiz._parse_speech_components(phrase)
        print(f"      Components: {components}")
        
        start_time = time.time()
        result = word_quiz.say(phrase)
        elapsed = time.time() - start_time
        print(f"      Result: {result}, Time: {elapsed:.2f}s")
        time.sleep(0.3)  # Small delay between tests
    
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
            
            print("New cached files:")
            for i, filename in enumerate(wav_files[:new_files]):
                filepath = os.path.join('voice_files', filename)
                size = os.path.getsize(filepath)
                print(f"   {filename} ({size} bytes)")
        except Exception as e:
            print(f"Error listing files: {e}")

def analyze_caching_behavior():
    """Analyze how different types of content are cached"""
    print("\n--- Analyzing caching behavior ---")
    
    test_cases = [
        ("Multi-word phrase", "Welcome to the Spelling Quiz Game!"),
        ("Single word", "spell"),
        ("Word with punctuation", "Correct!"),
        ("Letter sequence", "c, a, t"),
        ("Mixed content", "Incorrect. cat is spelled: c, a, t")
    ]
    
    for case_type, text in test_cases:
        components = word_quiz._parse_speech_components(text)
        print(f"   {case_type}: '{text}'")
        print(f"      -> {len(components)} component(s): {components}")

if __name__ == "__main__":
    print("Testing improved speech caching with phrase preservation...")
    
    analyze_caching_behavior()
    test_improved_speech_caching()
    
    print(f"\n✅ Improved speech caching test completed!")
    print("Key benefits:")
    print("- Multi-word phrases cached as natural-sounding complete units")
    print("- Letter sequences still use efficient individual letter caching")
    print("- Best of both worlds: natural speech + maximum efficiency")
    print("- Reduced cache fragmentation for common phrases")