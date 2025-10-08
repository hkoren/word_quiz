# Word Quiz

A spelling quiz game with text-to-speech capabilities using either Google Cloud Text-to-Speech or espeak as a fallback.

## Setting up

### Basic Dependencies
```bash
pip install pyttsx3 pygame
```

### Google Cloud Text-to-Speech Setup (Optional but Recommended)

For higher quality speech synthesis, you can set up Google Cloud TTS:

#### 1. Install Google Cloud TTS Library
```bash
pip install google-cloud-texttospeech
```

#### 2. Set up Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Text-to-Speech API:
   - Go to APIs & Services > Library
   - Search for "Text-to-Speech API"
   - Click on it and press "Enable"

#### 3. Create Service Account Credentials
1. Go to APIs & Services > Credentials
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details and click "Create"
4. Grant the service account the "Text-to-Speech User" role
5. Click "Done"
6. Click on the created service account
7. Go to the "Keys" tab
8. Click "Add Key" > "Create New Key" > "JSON"
9. Download the JSON file

#### 4. Configure Credentials
Save the downloaded JSON file as one of these names in your project directory:
- `service-account-key.json` (recommended)
- `google-credentials.json`
- Any filename, then set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to it

#### 5. Alternative: Use Environment Variable
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
```

### Fallback: espeak (Linux/macOS)
If Google TTS is not configured, the app will automatically fall back to espeak:

**macOS:**
```bash
brew install espeak
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install espeak
```

## Running

```bash
python word_quiz.py
```

The app will automatically detect and use Google TTS if properly configured, otherwise it will fall back to espeak.

## Features

- Customizable grade levels (1-10)
- Multiple word types: sight words, non-sight words, or mixed
- Audio pronunciation with "?" to repeat words
- Smart caching of Google TTS audio files
- Score tracking and study recommendations
