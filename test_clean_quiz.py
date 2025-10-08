#!/usr/bin/env python3
"""
Comprehensive test of the cleaned up word quiz
"""

import sys
import os
import subprocess

def test_clean_quiz():
    print("Testing cleaned up word quiz...")
    
    # Test the quiz startup and first few interactions
    process = subprocess.Popen(
        ['python3', 'word_quiz.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd='/Users/henrykoren/Documents/Code/word_quiz/word_quiz'
    )
    
    # Send input for grade level and word type
    input_data = "1\ns\n"
    stdout, stderr = process.communicate(input=input_data, timeout=10)
    
    print("STDOUT:")
    print(stdout[:500] + "..." if len(stdout) > 500 else stdout)
    
    print("\nSTDERR:")
    if stderr.strip():
        print(f"Warning messages found: {len(stderr.splitlines())} lines")
        # Show just the first few characters to see what's there
        print(stderr[:200] + "..." if len(stderr) > 200 else stderr)
    else:
        print("✅ No error messages - clean output!")

if __name__ == "__main__":
    test_clean_quiz()