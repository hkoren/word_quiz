#!/usr/bin/env python3
"""
Cache Words Utility

This script pre-generates and caches all words from word_lists.py using Google TTS API.
After running this script, all future calls to say() for these words will use cached files
for much faster performance.
"""

import os
import sys
import time

# Set testing mode to prevent main quiz from running
os.environ['TESTING_MODE'] = '1'

# Add parent directory to path to import main modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import word_quiz
    from word_lists import word_list, sight_word_dictionary, non_sight_word_dictionary
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this script from the correct directory.")
    sys.exit(1)

def collect_all_words():
    """Collect all unique words from all word lists"""
    all_words = set()
    
    # Add words from the main word_list
    all_words.update(word_list)
    
    # Add words from sight_word_dictionary
    for grade_words in sight_word_dictionary.values():
        all_words.update(grade_words)
    
    # Add words from non_sight_word_dictionary  
    for grade_words in non_sight_word_dictionary.values():
        all_words.update(grade_words)
    
    return sorted(all_words)

def collect_all_letters():
    """Collect all unique letters that appear in the word lists"""
    all_letters = set()
    all_words = collect_all_words()
    
    for word in all_words:
        for letter in word.lower():
            if letter.isalpha():
                all_letters.add(letter)
    
    return sorted(all_letters)

def count_cached_files():
    """Count existing cached files"""
    voice_files_dir = os.path.join(os.path.dirname(__file__), '..', 'voice_files')
    try:
        return len([f for f in os.listdir(voice_files_dir) if f.endswith('.wav')])
    except FileNotFoundError:
        return 0

def cache_words_and_letters(words, letters, verbose=False):
    """Cache all words and letters using Google TTS"""
    total_items = len(words) + len(letters)
    cached_count = 0
    skipped_count = 0
    
    if verbose:
        print(f"Caching {len(words)} words and {len(letters)} letters...")
    
    # Cache individual letters first (they're used most frequently)
    if verbose:
        print("\n=== Caching Individual Letters ===")
    
    for i, letter in enumerate(letters, 1):
        if verbose:
            print(f"  {i:2d}/{len(letters)}: Caching letter '{letter}'", end="")
        
        # Check if already cached
        filename = word_quiz._generate_audio_filename(letter)
        voice_files_dir = os.path.join(os.path.dirname(__file__), '..', 'voice_files')
        filepath = os.path.join(voice_files_dir, filename)
        
        if os.path.exists(filepath):
            if verbose:
                print(" (already cached)")
            skipped_count += 1
        else:
            # Generate and cache
            result = word_quiz.say(letter)
            if result == 0:
                cached_count += 1
                if verbose:
                    print(" ✅")
            else:
                if verbose:
                    print(" ❌")
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.1)
    
    # Cache words
    if verbose:
        print(f"\n=== Caching {len(words)} Words ===")
    
    for i, word in enumerate(words, 1):
        if verbose:
            print(f"  {i:3d}/{len(words)}: Caching '{word}'", end="")
        
        # Check if already cached
        filename = word_quiz._generate_audio_filename(word)
        voice_files_dir = os.path.join(os.path.dirname(__file__), '..', 'voice_files')
        filepath = os.path.join(voice_files_dir, filename)
        
        if os.path.exists(filepath):
            if verbose:
                print(" (already cached)")
            skipped_count += 1
        else:
            # Generate and cache
            result = word_quiz.say(word)
            if result == 0:
                cached_count += 1
                if verbose:
                    print(" ✅")
            else:
                if verbose:
                    print(" ❌")
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.1)
    
    return cached_count, skipped_count

def cache_common_phrases(verbose=False):
    """Cache common phrases used in the quiz"""
    common_phrases = [
        "Correct!",
        "Incorrect.",
        "spell",
        "Welcome to the Spelling Quiz Game!",
        "Keep practicing to improve your spelling!",
        "Good job! You're getting better at spelling.",
        "Excellent work! You're a spelling star!",
        "Perfect score! You're a spelling champion!",
        "Your score:",
        "out of",
        "is spelled:"
    ]
    
    cached_count = 0
    skipped_count = 0
    
    if verbose:
        print(f"\n=== Caching {len(common_phrases)} Common Phrases ===")
    
    for i, phrase in enumerate(common_phrases, 1):
        if verbose:
            print(f"  {i:2d}/{len(common_phrases)}: Caching '{phrase}'", end="")
        
        # Check if already cached
        filename = word_quiz._generate_audio_filename(phrase)
        voice_files_dir = os.path.join(os.path.dirname(__file__), '..', 'voice_files')
        filepath = os.path.join(voice_files_dir, filename)
        
        if os.path.exists(filepath):
            if verbose:
                print(" (already cached)")
            skipped_count += 1
        else:
            # Generate and cache
            result = word_quiz.say(phrase)
            if result == 0:
                cached_count += 1
                if verbose:
                    print(" ✅")
            else:
                if verbose:
                    print(" ❌")
        
        # Small delay
        time.sleep(0.1)
    
    return cached_count, skipped_count

def main():
    """Main caching function"""
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    
    if verbose:
        print("=== Word Quiz Cache Generator ===")
        print("Pre-caching all words and letters for optimal performance...\n")
    
    # Count files before
    files_before = count_cached_files()
    if verbose:
        print(f"Cached files before: {files_before}")
    
    # Collect all words and letters
    all_words = collect_all_words()
    all_letters = collect_all_letters()
    
    if verbose:
        print(f"Found {len(all_words)} unique words")
        print(f"Found {len(all_letters)} unique letters")
    
    # Cache everything
    start_time = time.time()
    
    # Cache words and letters
    words_cached, words_skipped = cache_words_and_letters(all_words, all_letters, verbose)
    
    # Cache common phrases
    phrases_cached, phrases_skipped = cache_common_phrases(verbose)
    
    # Summary
    files_after = count_cached_files()
    elapsed_time = time.time() - start_time
    total_cached = words_cached + phrases_cached
    total_skipped = words_skipped + phrases_skipped
    
    if verbose:
        print(f"\n=== Caching Complete ===")
        print(f"Files before: {files_before}")
        print(f"Files after:  {files_after}")
        print(f"New files:    {files_after - files_before}")
        print(f"Total cached: {total_cached}")
        print(f"Already cached: {total_skipped}")
        print(f"Time elapsed: {elapsed_time:.1f} seconds")
        print(f"\n✅ All words and letters are now cached!")
        print("Future quiz sessions will have much faster speech generation.")
    else:
        # Silent mode - just show summary
        print(f"Cached {total_cached} new items, {total_skipped} already cached. Total files: {files_after}")

if __name__ == "__main__":
    main()