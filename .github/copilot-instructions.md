# Copilot Instructions for AI Coding Agents

## Project Overview
- This is a simple spelling quiz game implemented in Python (`word_quiz.py`).
- The game uses text-to-speech (pyttsx3) to pronounce words and pygame to play a buzzer sound for incorrect answers.
- The quiz selects 10 random words from a hardcoded list and prompts the user to spell each one.

## Key Files
- `word_quiz.py`: Main application logic. Contains word list, quiz loop, TTS setup, and buzzer sound integration.
- `buzzer.wav`: Sound file played for incorrect answers (must be present in the root directory).

## Architecture & Data Flow
- The game runs in a single process, with all logic in `word_quiz.py`.
- No external configuration or modularization; all settings and data are hardcoded.
- User interaction is via the terminal (input/output).
- TTS engine is initialized at startup; American English voice is preferred if available.
- Pygame mixer is used for sound playback. If `buzzer.wav` is missing, a warning is printed.

## Developer Workflows
- **Run the game:**
  ```bash
  python3 word_quiz.py
  ```
- **Dependencies:**
  - Install required packages:
    ```bash
    pip install pyttsx3 pygame
    ```
- **Debugging:**
  - If sound or TTS fails, check for missing dependencies or sound file.
  - The game prints diagnostic info about the selected TTS voice.

## Project-Specific Conventions
- All logic is in a single file; no modules or tests.
- Word list is hardcoded; to change, edit `word_list` in `word_quiz.py`.
- Buzzer sound path is fixed as `buzzer.wav` in the root directory.
- No support for configuration files, environment variables, or external data sources.

## Integration Points
- Relies on `pyttsx3` for TTS and `pygame` for sound.
- No network, database, or external service integration.

## Example Patterns
- To add new words, append to the `word_list` in `word_quiz.py`.
- To change the buzzer sound, replace `buzzer.wav`.

---
For questions or unclear sections, please ask for clarification or provide feedback to improve these instructions.