# Utils Directory

This directory contains utility scripts and test files for the Word Quiz application.

## Test Files

- `test_*.py` - Various test scripts for different components:
  - `test_google_tts.py` - Test Google TTS integration
  - `test_component_caching.py` - Test component-based caching system
  - `test_speech_caching.py` - Test speech generation and caching
  - `test_efficient_caching.py` - Test efficient caching strategies
  - `test_letter_caching.py` - Test individual letter caching
  - `test_phrase_preservation.py` - Test phrase preservation logic
  - And many more...

## Utility Scripts

- `analyze_cache.py` - Analyze cache efficiency and statistics
- `debug_caching.py` - Debug caching functionality
- `demo_selective_caching.py` - Demonstrate selective caching features

## Usage

Run any utility from the main directory:

```bash
# From the main word_quiz directory
python3 utils/analyze_cache.py
python3 utils/test_google_tts.py
```

## Note

These files are development and testing utilities. The main application functionality is in the parent directory's `word_quiz.py` and `word_lists.py` files.