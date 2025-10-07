import random
import os
import time
import subprocess

def say(text: str, pitch: int=70) -> int:
    # Use espeak to convert text to speech.
    return subprocess.run(['espeak', f'-p {pitch}', text]).returncode

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

def spellitout(word):
    # Replace 's' characters with 'ess' for better pronunciation
    spelled_letters = []
    for letter in word:
        if letter.lower() == 's':
            spelled_letters.append('ess')
        else:
            spelled_letters.append(letter)
    return ", ".join(spelled_letters)

def printandsay(text, refresh=False):
    print(text)
    return say(text, refresh)

# Function to quiz the user
def quiz_game():
    score = 0
    incorrect_words = []  # List to store incorrectly spelled words
    
    # Select 10 unique random words from the word list
    selected_words = random.sample(word_list, 10)
    
    # Loop through the selected words
    for word in selected_words:
        time.sleep(0.2)
        say("spell " + word)
        
        # Get the user's spelling attempt without showing the word
        while True:
            user_input = input("Spell the word you just heard (or type '?' to hear it again):\n").strip().lower()
            
            if user_input == "?":
                say( word)
                continue
            else:
                break
        
        if user_input == word:
            score += 1
            engine = printandsay("Correct!\n")

        else:
            incorrect_words.append(word)  # Add to incorrect words list
            print(f"Incorrect. The correct spelling is: {word}\n")
            
            say("Incorrect. " + word + " is spelled: " +spellitout(word))  # audio feedback
        
    
    # Display the final score
    printandsay(f"Your score: {score} out of 10")
    if score < 5:
        printandsay("Keep practicing to improve your spelling!")
    elif score >= 5 and score < 8:
        printandsay("Good job! You're getting better at spelling.")
    elif score == 8 or score == 9:
        printandsay("Excellent work! You're a spelling star!")
    else:
        printandsay("Perfect score! You're a spelling champion!")
    
    # Display incorrectly spelled words if any
    if incorrect_words:
        print("\nPlease work on spelling these words:")
        for word in incorrect_words:
            print(f"  - {word}")

# Start the quiz
if __name__ == "__main__":
    printandsay("Welcome to the Spelling Quiz Game!", refresh=False)
    quiz_game()
