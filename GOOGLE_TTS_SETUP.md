# Google Text-to-Speech Setup Instructions

The updated `word_quiz.py` now supports Google Cloud Text-to-Speech API as an alternative to espeak. 

## ✅ Current Status - FULLY CONFIGURED AND WORKING!

**Google Cloud TTS is now active and working with the service account credentials in `voiceAPI.json`.**

✅ **Working Features:**
- ✅ Google Cloud Text-to-Speech API integration (ACTIVE)
- ✅ High-quality neural voice synthesis using `en-US-Standard-C`
- ✅ Audio file caching in `voice_files/` directory
- ✅ Automatic fallback to espeak if Google TTS fails
- ✅ Pygame-based audio playback
- ✅ Consistent filename generation with hashing

## Verification

You can verify Google TTS is working by running the quiz and looking for messages like:
```
Generated Welcome_to_the_Spelling_Quiz_G_30eef56168.wav using Google Cloud TTS
Generated spell_word_abc123def4.wav using Google Cloud TTS
```

Audio files generated with Google TTS are typically 50KB+ in size, while espeak files are usually smaller.

## Option 1: Using Espeak (Current Default)

The system currently works with espeak and generates cached audio files. No additional setup required.

## Option 2: Setting Up Google Cloud TTS

To use Google Cloud Text-to-Speech API instead of espeak:

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Text-to-Speech API

### Step 2: Create Service Account Credentials
1. Go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Give it a name like "word-quiz-tts"
4. Grant it the "Text-to-Speech API User" role
5. Create and download a JSON key file

### Step 3: Configure Credentials
Choose one of these options:

**Option A:** Replace `voiceAPI.json` with your service account key file
```bash
# Rename your downloaded service account key to voiceAPI.json
mv your-service-account-key.json voiceAPI.json
```

**Option B:** Use environment variable
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your-service-account-key.json"
```

**Option C:** Save as a specific filename
```bash
# Save your key as one of these names:
# - service-account-key.json
# - google-credentials.json
```

### Step 4: Install Google Cloud TTS Library
```bash
pip install google-cloud-texttospeech
```

### Step 5: Test the Setup
Run the quiz - it should now use Google Cloud TTS and show messages like:
```
Generated word_audio_filename.wav using Google Cloud TTS
```

## File Structure

```
word_quiz/
├── word_quiz.py              # Main quiz application
├── voiceAPI.json            # Current OAuth2 credentials (or replace with service account)
├── voice_files/             # Generated audio files cache
│   ├── spell_word1_hash.wav
│   ├── spell_word2_hash.wav
│   └── ...
├── buzzer.wav              # Error sound
└── test_tts.py             # TTS testing script
```

## How It Works

1. **Cache Check:** Before generating audio, the system checks if a file already exists for the given text
2. **Google TTS:** If configured, uses Google Cloud TTS API to generate high-quality audio
3. **Espeak Fallback:** If Google TTS fails or isn't configured, falls back to espeak
4. **File Storage:** Saves all generated audio files in `voice_files/` for future reuse
5. **Pygame Playback:** Uses pygame to play the audio files

## Benefits

- **High Quality Audio:** Google TTS provides natural-sounding voices
- **Offline Capability:** Cached files work without internet after first generation
- **Cost Effective:** Files are cached, so each word is only generated once
- **Fallback Support:** Always works with espeak if Google TTS is unavailable

## Current Implementation Notes

The current `voiceAPI.json` contains OAuth2 client credentials, which are different from service account credentials required for the Google Cloud TTS API. To use Google TTS, you'll need to obtain service account credentials as described above.