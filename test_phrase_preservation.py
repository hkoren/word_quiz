#!/usr/bin/env python3
"""Test the updated caching that keeps multi-word phrases together"""

import os
import sys
import time
import re

def _parse_speech_components(text):
    """Parse text into cacheable components, keeping multi-word phrases together except letter sequences"""
    import re
    
    # Handle letter sequences like "c, a, t" - split into individual letters for maximum reuse
    letter_pattern = r'\b[a-zA-Z](?:\s*,\s*[a-zA-Z])+\b'
    if re.search(letter_pattern, text):
        components = []
        parts = re.split(f'({letter_pattern})', text)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            if re.match(letter_pattern, part):
                # Split letter sequence into individual letters for caching
                letters = re.findall(r'[a-zA-Z]', part)
                components.extend(letters)
            else:
                # Recursively parse non-letter parts
                components.extend(_parse_speech_components(part))
        
        return components
    
    # For non-letter sequences, keep the entire phrase together as a single component
    # This preserves natural speech for phrases like:
    # "Welcome to the Spelling Quiz Game!"
    # "Keep practicing to improve your spelling!"
    # "Your score: 5 out of 10"
    # "Incorrect. The correct spelling is:"
    return [text]

def test_phrase_preservation():
    """Test that multi-word phrases stay together"""
    print("--- Testing multi-word phrase preservation ---")
    
    test_cases = [
        # Multi-word phrases - should stay together as single components
        "Welcome to the Spelling Quiz Game!",
        "Keep practicing to improve your spelling!",
        "Your score: 5 out of 10",
        "Incorrect. The correct spelling is:",
        "Excellent work! You're a spelling star!",
        "Perfect score! You're a spelling champion!",
        "Good job! You're getting better at spelling.",
        
        # Single words - should stay as single components
        "spell",
        "cat",
        "Correct!",
        "Incorrect.",
        
        # Letter sequences - should split into individual letters
        "c, a, t",
        "s, p, e, l, l",
        "d, o, g",
        "t, e, m, p, e, r, a, t, u, r, e",
        
        # Mixed cases with letter sequences
        "Incorrect. cat is spelled: c, a, t",
        "spell dog as d, o, g",
        "The word temperature is spelled: t, e, m, p, e, r, a, t, u, r, e"
    ]
    
    for text in test_cases:
        components = _parse_speech_components(text)
        print(f"   '{text}'")
        print(f"      -> {components}")
        print()

def test_caching_efficiency():
    """Test the caching efficiency of the new approach"""
    print("--- Testing caching efficiency ---")
    
    # Test phrases that should be cached as single units
    phrases = [
        "Welcome to the Spelling Quiz Game!",
        "Keep practicing to improve your spelling!",
        "Your score: 5 out of 10",
        "Excellent work! You're a spelling star!"
    ]
    
    # Test letter sequences that should use individual letter caching
    letter_sequences = [
        "c, a, t",
        "d, o, g", 
        "r, a, t",
        "c, a, r"
    ]
    
    print("Multi-word phrases (cached as complete units):")
    for phrase in phrases:
        components = _parse_speech_components(phrase)
        print(f"   '{phrase}' -> {len(components)} component(s)")
        print(f"      Components: {components}")
    
    print("\nLetter sequences (use individual letter cache):")
    all_letters = set()
    for sequence in letter_sequences:
        components = _parse_speech_components(sequence)
        letters = set(components)
        new_letters = letters - all_letters
        reused_letters = letters & all_letters
        
        print(f"   '{sequence}' -> {len(components)} letters")
        if new_letters:
            print(f"      New letters: {sorted(new_letters)}")
        if reused_letters:
            print(f"      Reused letters: {sorted(reused_letters)}")
        
        all_letters.update(letters)
    
    print(f"\nTotal unique letters needed: {len(all_letters)}")
    print(f"Letters: {sorted(all_letters)}")

if __name__ == "__main__":
    print("Testing updated component parsing with phrase preservation...")
    print()
    
    test_phrase_preservation()
    test_caching_efficiency()
    
    print("✅ Updated parsing test completed!")
    print("\nKey improvements:")
    print("- Multi-word phrases stay together as single cached components")
    print("- Letter sequences still split into individual letters for maximum reuse")
    print("- Natural speech preserved for longer phrases")
    print("- Efficient caching for both phrases and individual letters")