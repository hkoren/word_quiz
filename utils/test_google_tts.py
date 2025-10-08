#!/usr/bin/env python3
"""
Test script to verify Google Cloud TTS is working with the updated service account credentials
"""

import sys
import os
import json

# Add the current directory to the path so we can import from word_quiz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_credentials():
    """Test if voiceAPI.json contains valid service account credentials"""
    try:
        with open('voiceAPI.json', 'r') as f:
            creds = json.load(f)
        
        print("Checking voiceAPI.json credentials...")
        
        required_fields = [
            'type', 'project_id', 'private_key_id', 'private_key', 
            'client_email', 'client_id', 'auth_uri', 'token_uri'
        ]
        
        missing_fields = [field for field in required_fields if field not in creds]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        if creds.get('type') != 'service_account':
            print(f"❌ Wrong credential type: {creds.get('type')} (expected: service_account)")
            return False
        
        print("✅ voiceAPI.json contains valid service account credentials")
        print(f"   Project ID: {creds['project_id']}")
        print(f"   Client Email: {creds['client_email']}")
        return True
        
    except FileNotFoundError:
        print("❌ voiceAPI.json not found")
        return False
    except json.JSONDecodeError:
        print("❌ voiceAPI.json is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading voiceAPI.json: {e}")
        return False

def test_google_tts_directly():
    """Test Google Cloud TTS directly"""
    try:
        from google.cloud import texttospeech
        from google.oauth2 import service_account
        
        print("\nTesting Google Cloud TTS directly...")
        
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file('voiceAPI.json')
        client = texttospeech.TextToSpeechClient(credentials=credentials)
        
        # Test synthesis
        synthesis_input = texttospeech.SynthesisInput(text="Hello, this is a test.")
        
        # Try different voice configurations to find one that works
        voice_configs = [
            {
                "name": "en-US-Standard-C",
                "language_code": "en-US",
                "ssml_gender": texttospeech.SsmlVoiceGender.FEMALE
            },
            {
                "name": "en-US-Standard-B",
                "language_code": "en-US", 
                "ssml_gender": texttospeech.SsmlVoiceGender.MALE
            },
            {
                "name": "en-US-Wavenet-C",
                "language_code": "en-US",
                "ssml_gender": texttospeech.SsmlVoiceGender.FEMALE
            }
        ]
        
        for i, voice_config in enumerate(voice_configs):
            try:
                voice = texttospeech.VoiceSelectionParams(**voice_config)
                
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                    sample_rate_hertz=24000
                )
                
                response = client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                
                print(f"✅ Voice configuration {i+1} works: {voice_config['name']}")
                print(f"   Audio data size: {len(response.audio_content)} bytes")
                return voice_config, response.audio_content
                
            except Exception as e:
                print(f"❌ Voice configuration {i+1} failed: {e}")
                continue
        
        print("❌ All voice configurations failed")
        return None, None
        
    except ImportError:
        print("❌ Google Cloud TTS library not installed")
        return None, None
    except Exception as e:
        print(f"❌ Error setting up Google Cloud TTS: {e}")
        return None, None

def test_word_quiz_integration():
    """Test the word quiz TTS integration"""
    try:
        from word_quiz import say, _try_google_cloud_tts
        
        print("\nTesting word quiz TTS integration...")
        
        # Test the internal Google TTS function
        audio_data = _try_google_cloud_tts("Testing word quiz integration")
        if audio_data:
            print(f"✅ _try_google_cloud_tts works: {len(audio_data)} bytes")
        else:
            print("❌ _try_google_cloud_tts failed")
        
        # Test the full say function
        print("\nTesting full say() function...")
        result = say("This is a complete test")
        print(f"   say() result: {result}")
        
    except Exception as e:
        print(f"❌ Error testing word quiz integration: {e}")

if __name__ == "__main__":
    print("Google Cloud TTS Configuration Test")
    print("=" * 50)
    
    # Test 1: Check credentials
    if not test_credentials():
        exit(1)
    
    # Test 2: Test Google TTS directly
    working_voice, audio_data = test_google_tts_directly()
    
    # Test 3: Test integration
    test_word_quiz_integration()
    
    print("\n" + "=" * 50)
    if working_voice and audio_data:
        print("✅ Google Cloud TTS is working!")
        print(f"   Recommended voice: {working_voice['name']}")
    else:
        print("❌ Google Cloud TTS needs configuration")