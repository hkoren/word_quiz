import random
import pyttsx3
import os
import pygame
import time

# List of words to be used for the quiz
word_list = [
    "adventure", "bicycle", "calendar", "delicious", "elephant", "fierce", 
    "gentle", "hurricane", "island", "journey", "knowledge", "library", 
    "mountain", "nervous", "ocean", "puzzle", "question", "robot", "school", 
    "thunder", "umbrella", "vacation", "window", "yellow", "zookeeper", "athlete", 
    "brave", "celebrate", "dictionary", "excited", "favorite", "guitar", "holiday", 
    "ingredient", "jealous", "kindness", "letter", "melody", "nature", "ocean", 
    "peaceful", "quarter", "rainbow", "surprise", "trust", "unusual", "victory", 
    "wonder", "xylophone", "youthful"
]

# Initialize text-to-speech engine
engine = pyttsx3.init()

# List available voices and set the voice to American English if available
voices = engine.getProperty('voices')

selected_voice = None
for voice in voices:
    if 'en-us' in voice.id.lower():  # American English voice
        selected_voice = voice
        break

if selected_voice:
    engine.setProperty('voice', selected_voice.id)
    print(f"Voice set to: {selected_voice.name}")
else:
    print("The American English voice is not available. Using default voice.")

# Initialize pygame mixer for sound
pygame.mixer.init()

# Function to play a buzzer sound (using pygame)
def buzzer():
    buzzer_sound = 'buzzer.wav'  # Path to your buzzer sound file
    
    # Check if the buzzer sound file exists
    if os.path.exists(buzzer_sound):
        sound = pygame.mixer.Sound(buzzer_sound)  # Load the sound
        sound.play()  # Play the sound
        # Wait for the sound to finish playing
        while pygame.mixer.get_busy():
            time.sleep(0.1)
        # Additional cleanup for older macOS versions
        pygame.mixer.stop()
        time.sleep(1.0)  # Longer pause to ensure audio system is free
    else:
        print("Buzzer sound file not found!")
        time.sleep(0.5)

# Function to play a buzzer sound (using pygame)
def ding():
    buzzer_sound = 'ding.wav'  # Path to your buzzer sound file
    
    # Check if the buzzer sound file exists
    if os.path.exists(buzzer_sound):
        sound = pygame.mixer.Sound(buzzer_sound)  # Load the sound
        sound.play()  # Play the sound
        # Wait for the sound to finish playing
        while pygame.mixer.get_busy():
            time.sleep(0.1)
        # Additional cleanup for older macOS versions
        pygame.mixer.stop()
        time.sleep(1.0)  # Longer pause to ensure audio system is free
    else:
        print("Buzzer sound file not found!")
        time.sleep(0.5)

# Function to quiz the user
def quiz_game():
    score = 0
    incorrect_words = []  # List to store incorrectly spelled words
    
    # Select 10 unique random words from the word list
    selected_words = random.sample(word_list, 10)
    
    # Loop through the selected words
    for word in selected_words:
        engine.say(word)
        engine.runAndWait()  # Say the word out loud
        
        # Get the user's spelling attempt without showing the word
        while True:
            user_input = input("Spell the word you just heard (or type '?' to hear it again):\n").strip().lower()
            
            if user_input == "?":
                engine.say(word)
                engine.runAndWait()  # Replay the word
                continue
            else:
                break
        
        if user_input == word:
            score += 1
            ding()  # Play ding sound
            print("Correct!\n")
        else:
            incorrect_words.append(word)  # Add to incorrect words list
            buzzer()  # Play buzzer sound
            print(f"Incorrect. The correct spelling is: {word}\n")
    
    # Display the final score
    print(f"Your score: {score} out of 10")
    
    # Display incorrectly spelled words if any
    if incorrect_words:
        print("\nPlease work on spelling these words:")
        for word in incorrect_words:
            print(f"  - {word}")

# Start the quiz
if __name__ == "__main__":
    print("Welcome to the Spelling Quiz Game!")
    quiz_game()
