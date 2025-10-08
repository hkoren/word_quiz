#!/usr/bin/env python3
"""Test the component caching with individual letters and intact punctuation"""

import os
import sys
import time
import re

def _parse_speech_components(text):
    """Parse text into cacheable components, with individual letters cached independently"""
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
    
    # For other text, split into words but keep punctuation attached
    words = text.split()
    components = []
    
    for word in words:
        # Keep the word with its punctuation intact - don't separate punctuation
        components.append(word)
    
    return components if components else [text]

def test_component_parsing():
    """Test how text is parsed into components with punctuation intact"""
    print("--- Testing component parsing with intact punctuation ---")
    
    test_cases = [
        # Individual words with punctuation - should stay intact
        "spell cat",
        "Correct!",
        "Incorrect.",
        "Welcome to the Spelling Quiz Game!",
        
        # Letter sequences - should split into individual letters
        "c, a, t",
        "s, p, e, l, l",
        "d, o, g",
        
        # Mixed cases
        "Incorrect. cat is spelled: c, a, t",
        "spell dog as d, o, g",
        "Your score: 5 out of 10",
    ]
    
    for text in test_cases:
        components = _parse_speech_components(text)
        print(f"   '{text}'")
        print(f"      -> {components}")
        print()

def test_letter_reuse():
    """Test that individual letters can be reused across different words"""
    print("--- Testing letter reuse efficiency ---")
    
    # These test cases should demonstrate letter reuse
    test_cases = [
        "c, a, t",           # Should cache: c, a, t
        "c, a, r",           # Should reuse: c, a and cache: r  
        "a, r, t",           # Should reuse: a, r and cache: t (if not already cached)
        "t, a, r",           # Should reuse all: t, a, r
    ]
    
    all_letters_used = set()
    
    for text in test_cases:
        components = _parse_speech_components(text)
        print(f"   '{text}' -> {components}")
        
        letters_in_this = set(components)
        new_letters = letters_in_this - all_letters_used
        reused_letters = letters_in_this & all_letters_used
        
        if new_letters:
            print(f"      New letters to cache: {sorted(new_letters)}")
        if reused_letters:
            print(f"      Reused letters: {sorted(reused_letters)}")
        
        all_letters_used.update(letters_in_this)
        print()
    
    print(f"   Total unique letters cached: {sorted(all_letters_used)}")

if __name__ == "__main__":
    print("Testing component caching with individual letters...")
    
    test_component_parsing()
    test_letter_reuse()
    
    print("✅ Component caching test completed!")
    print("\nKey features:")
    print("- Individual letters (s, p, e, l, l) are cached independently")
    print("- Punctuation stays attached to words (Correct!, Incorrect.)")
    print("- Letter sequences are broken into reusable components")
    print("- Maximum cache efficiency through letter reuse")