#!/usr/bin/env python3
"""
Test with a completely new phrase to verify message suppression
"""

import sys
import os

# Add the current directory to the path so we can import from word_quiz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from word_quiz import say

def test_clean_output():
    print("Testing clean output with new phrase...")
    
    # Use a phrase that definitely doesn't exist yet
    test_phrase = "This is a brand new test phrase for clean output verification"
    
    print(f"Testing phrase: '{test_phrase}'")
    result = say(test_phrase)
    print(f"Result: {result}")
    print("Test completed - check for any unwanted messages above")

if __name__ == "__main__":
    test_clean_output()