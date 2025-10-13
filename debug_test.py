#!/usr/bin/env python3
"""
Debug test script to check the build_word_pool function
"""

import sys
import os

# Add the current directory to Python path to import word_lists
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from word_lists import word_dictionary

def build_word_pool(grades, word_type):
    """Build word pool based on grade levels and word type"""
    print(f"DEBUG: build_word_pool called with grades={grades}, word_type={word_type}")
    sight_words = []
    non_sight_words = []
    
    # Collect words from selected grade levels using unified dictionary
    for word, data in word_dictionary.items():
        # Check if word appears in any of the selected grade levels
        if any(grade in data["grade_levels"] for grade in grades):
            if data["sight_word"]:
                sight_words.append(word)
            else:
                non_sight_words.append(word)
    
    print(f"DEBUG: Found {len(sight_words)} sight words, {len(non_sight_words)} non-sight words")
    
    # Remove duplicates (though they shouldn't exist in the new format)
    sight_words = list(set(sight_words))
    non_sight_words = list(set(non_sight_words))
    
    # Build final word pool based on word type
    if word_type == 's':  # sight words only
        result = sight_words
    elif word_type == 'o':  # non sight words only
        result = non_sight_words
    elif word_type == 'f':  # 50/50 mix
        min_count = min(len(sight_words), len(non_sight_words))
        if min_count < 5:
            # If we don't have enough of one type, return all available
            result = sight_words + non_sight_words
        else:
            # Take equal amounts from each
            import random
            result = random.sample(sight_words, min_count) + random.sample(non_sight_words, min_count)
    elif word_type == 'r':  # random mix
        result = sight_words + non_sight_words
    else:
        result = []
    
    print(f"DEBUG: Final word pool size: {len(result)}")
    return result

if __name__ == '__main__':
    print(f"Total words in dictionary: {len(word_dictionary)}")
    
    # Test different scenarios
    test_cases = [
        ([1], 'r'),      # Grade 1, random
        ([1], 's'),      # Grade 1, sight words only
        ([1], 'o'),      # Grade 1, non-sight words only
        ([1, 2], 'r'),   # Grades 1-2, random
        ([3, 4, 5], 'r'), # Grades 3-5, random
    ]
    
    for grades, word_type in test_cases:
        print(f"\n--- Testing grades={grades}, word_type={word_type} ---")
        words = build_word_pool(grades, word_type)
        print(f"Result: {len(words)} words available")
        if len(words) > 0:
            print(f"Sample words: {words[:5]}")
        else:
            print("NO WORDS FOUND!")