#!/usr/bin/env python3
"""
Final test to verify all messages are clean
"""

import sys
import os

# Add the current directory to the path so we can import from word_quiz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from word_quiz import say

def test_final_clean():
    print("Final clean output test...")
    
    # Test multiple new phrases
    test_phrases = [
        "Clean output test number one",
        "Clean output test number two", 
        "Final verification phrase"
    ]
    
    for i, phrase in enumerate(test_phrases):
        print(f"\nTest {i+1}: '{phrase}'")
        result = say(phrase)
        print(f"   Result: {result}")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_final_clean()