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
    else:
        print("Buzzer sound file not found!")
    time.sleep(2)

# Function to quiz the user
def quiz_game():
    score = 0
    
    # Loop through 10 random words
    for _ in range(10):
        word = random.choice(word_list)
        engine.say(word)
        engine.runAndWait()  # Say the word out loud
        
        # Get the user's spelling attempt without showing the word
        user_input = input("Spell the word you just heard:\n").strip().lower()
        
        if user_input == word:
            score += 1
            print("Correct!\n")
        else:
            buzzer()  # Play buzzer sound
            print(f"Incorrect. The correct spelling is: {word}\n")
    
    # Display the final score
    print(f"Your score: {score} out of 10")

# Start the quiz
if __name__ == "__main__":
    print("Welcome to the Spelling Quiz Game!")
    quiz_game()
