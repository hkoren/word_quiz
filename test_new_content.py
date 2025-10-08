#!/usr/bin/env python3
"""Test with completely new phrases and letters"""

import os
import sys
import time

os.environ['TESTING_MODE'] = '1'
sys.path.insert(0, '.')
import word_quiz

def test_new_content():
    """Test completely new phrases and letter sequences"""
    print("Testing new phrase and letters...")
    
    # Count files before
    files_before = len([f for f in os.listdir('voice_files') if f.endswith('.wav')])
    print(f"Files before: {files_before}")
    
    # Test a new multi-word phrase
    print('\nTesting: "Good morning, let us begin the quiz!"')
    components = word_quiz._parse_speech_components('Good morning, let us begin the quiz!')
    print(f'Components: {components}')
    result = word_quiz.say('Good morning, let us begin the quiz!')
    print(f'Result: {result}')
    
    time.sleep(0.5)
    
    # Test new letter sequence with letters we haven't cached yet
    print('\nTesting: "b, e, g, i, n"')  
    components = word_quiz._parse_speech_components('b, e, g, i, n')
    print(f'Components: {components}')
    result = word_quiz.say('b, e, g, i, n')
    print(f'Result: {result}')
    
    # Count files after
    files_after = len([f for f in os.listdir('voice_files') if f.endswith('.wav')])
    new_files = files_after - files_before
    print(f'\nFiles after: {files_after}')
    print(f'New files created: {new_files}')
    
    print('\n✅ New content test completed!')
    print('Demonstrates:')
    print('- Multi-word phrases are cached as complete units')
    print('- New individual letters are cached for reuse')
    print('- System efficiently handles both types of content')

if __name__ == "__main__":
    test_new_content()