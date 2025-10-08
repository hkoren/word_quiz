#!/usr/bin/env python3
"""Comprehensive demonstration of the component caching efficiency"""

import os

def analyze_cache_efficiency():
    """Analyze the efficiency of the current cache"""
    print("=== COMPONENT CACHING EFFICIENCY ANALYSIS ===\n")
    
    try:
        # Count different types of files in voice_files
        voice_files = os.listdir('voice_files')
        wav_files = [f for f in voice_files if f.endswith('.wav')]
        
        # Categorize files
        individual_letters = [f for f in wav_files if len(f.split('_')[0]) == 1 and f.split('_')[0].isalpha()]
        individual_words = [f for f in wav_files if len(f.split('_')[0]) > 1 and f.split('_')[0].isalpha()]
        phrases = [f for f in wav_files if not f.split('_')[0].isalpha() or ' ' in f.split('_')[0]]
        
        print(f"📁 Total cached files: {len(wav_files)}")
        print(f"🔤 Individual letters: {len(individual_letters)}")
        print(f"📝 Individual words: {len(individual_words)}")
        print(f"💬 Phrases: {len(phrases)}")
        print()
        
        # Show individual letters cached
        if individual_letters:
            letters_cached = sorted([f.split('_')[0] for f in individual_letters])
            print(f"🔤 Letters cached: {', '.join(letters_cached)}")
            print(f"   These {len(letters_cached)} letters can spell ANY word!")
            print()
        
        # Calculate efficiency for common spelling words
        common_words = ['cat', 'dog', 'rat', 'car', 'art', 'tar', 'bat', 'hat', 'mat', 'pat']
        total_letters_if_cached_separately = sum(len(word) for word in common_words)
        unique_letters_needed = len(set(''.join(common_words)))
        
        print("📊 EFFICIENCY DEMONSTRATION:")
        print(f"   To spell these 10 common words: {', '.join(common_words)}")
        print(f"   Traditional approach: {total_letters_if_cached_separately} separate cached letter sequences")
        print(f"   Component approach: {unique_letters_needed} individual letters")
        print(f"   💡 Efficiency gain: {total_letters_if_cached_separately - unique_letters_needed} fewer files!")
        print(f"   📈 Space savings: {((total_letters_if_cached_separately - unique_letters_needed) / total_letters_if_cached_separately) * 100:.1f}%")
        print()
        
        # Show file sizes
        total_size = 0
        for filename in wav_files:
            filepath = os.path.join('voice_files', filename)
            size = os.path.getsize(filepath)
            total_size += size
        
        print(f"💾 Total cache size: {total_size / 1024:.1f} KB")
        print(f"📁 Average file size: {total_size / len(wav_files) / 1024:.1f} KB")
        print()
        
        print("✅ KEY BENEFITS:")
        print("  • Individual letters (a, c, t, etc.) cached once, reused everywhere")
        print("  • Punctuation stays with words (Correct!, Incorrect.)")
        print("  • Letter sequences (c, a, t) use cached individual letters")
        print("  • Massive reduction in cache bloat")
        print("  • Natural speech through sequential component playback")
        
    except Exception as e:
        print(f"Error analyzing cache: {e}")

if __name__ == "__main__":
    analyze_cache_efficiency()