#!/usr/bin/env python3
"""Test the actual speech generation with component caching"""

import os
import sys
import time

# Add the current directory to the path and import the main module
sys.path.insert(0, '.')

# Set environment variable to prevent the main script from running
os.environ['TESTING_MODE'] = '1'

# Now import specific functions we need
def import_word_quiz_functions():
    """Import functions from word_quiz.py without running main"""
    import word_quiz
    return word_quiz._parse_speech_components, word_quiz.say, word_quiz._should_cache_component

# Get the functions
try:
    _parse_speech_components, say, _should_cache_component = import_word_quiz_functions()
except:
    print("Could not import word_quiz functions. Testing parsing only.")
    _parse_speech_components = None
    say = None
    _should_cache_component = None

def count_files(directory):
    """Count wav files in a directory"""
    try:
        return len([f for f in os.listdir(directory) if f.endswith('.wav')])
    except FileNotFoundError:
        return 0

def test_actual_speech_generation():
    """Test speech generation with the component caching system"""
    if not say:
        print("Speech functions not available, skipping speech test")
        return
        
    print("--- Testing actual speech generation with component caching ---")
    
    # Count files before
    files_before = count_files('voice_files')
    print(f"Files before test: {files_before}")
    
    # Test cases that should demonstrate efficient letter caching
    test_phrases = [
        "spell cat",           # Should cache: "spell", "cat"
        "c, a, t",            # Should cache individual letters: "c", "a", "t"
        "spell dog",          # Should reuse "spell", cache "dog"  
        "d, o, g",            # Should cache: "d", "o", "g"
        "Correct!",           # Should cache: "Correct!"
        "spell rat",          # Should reuse "spell", cache "rat"
        "r, a, t",            # Should reuse "r", "a", "t" (all already cached)
    ]
    
    print("\nGenerating speech...")
    for phrase in test_phrases:
        print(f"   Testing: '{phrase}'")
        components = _parse_speech_components(phrase)
        print(f"      Components: {components}")
        
        start_time = time.time()
        result = say(phrase)
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

def test_letter_efficiency():
    """Demonstrate the efficiency of letter caching"""
    if not _parse_speech_components:
        print("Parsing function not available")
        return
        
    print("\n--- Testing letter caching efficiency ---")
    
    # Simulate spelling multiple words that share letters
    words_to_spell = ["cat", "car", "art", "tar", "rat"]
    all_letters_needed = set()
    
    for word in words_to_spell:
        letter_sequence = f"{', '.join(word)}"
        components = _parse_speech_components(letter_sequence)
        letters_in_word = set(components)
        
        new_letters = letters_in_word - all_letters_needed
        reused_letters = letters_in_word & all_letters_needed
        
        print(f"   Spelling '{word}' as '{letter_sequence}':")
        print(f"      Components: {components}")
        if new_letters:
            print(f"      New letters to cache: {sorted(new_letters)}")
        if reused_letters:
            print(f"      Reused cached letters: {sorted(reused_letters)}")
        
        all_letters_needed.update(letters_in_word)
    
    print(f"\n   Total unique letters needed: {len(all_letters_needed)}")
    print(f"   Letters: {sorted(all_letters_needed)}")
    print(f"   Efficiency: Instead of caching {sum(len(word) for word in words_to_spell)} individual word spellings,")
    print(f"   we only need to cache {len(all_letters_needed)} individual letters!")

if __name__ == "__main__":
    print("Testing component caching with actual speech generation...")
    
    test_letter_efficiency()
    test_actual_speech_generation()
    
    print(f"\n✅ Component caching test completed!")
    print("Benefits:")
    print("- Individual letters cached once and reused across all spellings")
    print("- Punctuation stays attached to words for natural speech")
    print("- Massive cache efficiency for spelling applications")
    print("- Sequential playback of cached components creates natural speech")