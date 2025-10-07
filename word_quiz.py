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

sight_word_dictionary = {
    1:["after", "again", "an", "any", "as",
    "ask", "by", "could", "every", "fly",
    "from", "give", "going", "had", "has",
    "her", "him", "his", "how", "just",
    "know", "let", "live", "may", "of",
    "old", "once", "open", "over", "put",
    "round", "some", "stop", "take", "thank",
    "them", "then", "think", "walk", "were",
    "when"],
    2:["always", "around", "because", "been", "before",
    "best", "both", "buy", "call", "cold",
    "does", "don’t", "fast", "first", "five",
    "found", "gave", "goes", "green", "its",
    "made", "many", "off", "or", "pull",
    "read", "right", "sing", "sit", "sleep",
    "tell", "their", "these", "those", "upon",
    "us", "use", "very", "wash", "which",
    "why", "wish", "work", "would", "write",
    "your", "again", "always", "because", "been"],
    3:["about", "better", "bring", "carry", "clean",
    "cut", "done", "draw", "drink", "eight",
    "fall", "far", "full", "got", "grow",
    "hold", "hot", "hurt", "if", "keep",
    "kind", "laugh", "light", "long", "much",
    "myself", "never", "only", "own", "pick",
    "seven", "shall", "show", "six", "small",
    "start", "ten", "today", "together", "try",
    "warm"],
    4:["area", "ago", "box", "became", "certain",
    "color", "continue", "correct", "course", "decided",
    "dog", "dry", "ever", "fact", "finally",
    "fish", "friends", "green", "half", "heart",
    "horse", "hundred", "knew", "listen", "mouth",
    "music", "open", "order", "passed", "piece",
    "plan", "poor", "products", "remember", "room",
    "rock", "shown", "six", "slowly", "stay",
    "street", "strong", "surface", "system", "tail",
    "teacher", "team", "term", "themselves", "wait"],
    5:["afternoon", "amount", "am", "bill", "broken",
    "building", "busy", "carefully", "circle", "clothes",
    "cold", "company", "condition", "corner", "cover",
    "describe", "diagram", "direction", "energy", "engine",
    "experiment", "express", "field", "figure", "fraction",
    "increase", "instrument", "invented", "kill", "middle",
    "moment", "object", "perhaps", "position", "president",
    "problem", "quarter", "receive", "region", "repeat",
    "section", "sense", "serve", "solution", "special",
    "syllables", "temperature", "thousand", "village", "weight",
    "written", "wrong"],
    6: ["addition", "agree", "allow", "alphabet", "amaze",
    "angle", "appear", "apple", "arrive", "axis",
    "base", "belong", "broad", "building", "captain",
    "cent", "column", "compound", "continent", "control",
    "cool", "cost", "decide", "design", "different",
    "division", "dollar", "entire", "equal", "event",
    "exact", "expect", "explain", "famous", "fig",
    "forward", "fresh", "guess", "hat", "heavy",
    "include", "industry", "level", "material", "modern",
    "nation", "noun", "object", "paint", "pair",
    "paragraph", "planet", "plural", "poem", "police",
    "power", "produce", "properties", "protect", "provide",
    "raise", "represent", "root", "select", "separate",
    "sharp", "silent", "similar", "solution", "space",
    "straw", "symbol", "syllable", "system", "temperature",
    "though", "tiny", "triangle", "underline", "valley",
    "view", "visit", "wide", "wild", "wire",
    "worth", "written"],
    7: ["accurate", "active", "actual", "additional", "adjective",
    "affect", "allowance", "angle", "announced", "annual",
    "arrangement", "audience", "average", "balance", "barely",
    "beyond", "border", "capital", "century", "character",
    "circumference", "citizen", "community", "compare", "complete",
    "compound", "conclude", "connected", "consider", "contain",
    "continent", "contrast", "control", "coordinate", "current",
    "definition", "describe", "determine", "difference", "direction",
    "distance", "diverse", "energy", "equation", "evidence",
    "example", "examine", "factor", "figure", "fraction",
    "function"],
    8: ["ability", "absence", "accept", "account", "achievement",
    "active", "addition", "adventure", "ambitious", "analyze",
    "announce", "approach", "arrange", "article", "atmosphere",
    "attention", "audience", "available", "behavior", "beneath",
    "benefit", "calculate", "cause", "challenge", "citizen",
    "collect", "combine", "communicate", "compare", "complex",
    "conclusion", "connection", "consequence", "constant", "construct",
    "context", "contrast", "contribute", "creative", "culture",
    "debate", "decade", "declare", "demonstrate", "describe",
    "develop", "difference", "direction", "discover", "discussion"],
    9: ["abstract", "analyze", "approach", "argument", "assume",
    "category", "circumstance", "clarify", "coherent", "complexity",
    "component", "concept", "conclusion", "consequence", "construct",
    "contrast", "criteria", "data", "define", "derive",
    "dimension", "distinguish", "evaluate", "evidence", "factor",
    "function", "identify", "impact", "imply", "indicate",
    "interpret", "issue", "logical", "method", "occur",
    "perspective", "policy", "principle", "process", "reaction",
    "relevant", "research", "respond", "role", "section",
    "significant", "source", "structure", "theory", "variable"],
    10: ["analyze", "anticipate", "approximate", "articulate", "assess",
    "assume", "cite", "coincide", "compare", "compose",
    "concentrate", "conclude", "contrast", "correspond", "criteria",
    "debate", "deduce", "demonstrate", "derive", "determine",
    "differentiate", "distribute", "emphasize", "evaluate", "examine",
    "exceed", "explicit", "formulate", "hypothesis", "illustrate",
    "imply", "infer", "integrate", "interpret", "investigate",
    "justify", "maintain", "modify", "outcome", "parameter",
    "predict", "process", "proportion", "qualitative", "quantitative",
    "relevant", "research", "significance", "theory", "valid"]}

non_sight_word_dictionary = {
    1:["cat", "dog", "sun", "hat", "bed",
    "fish", "run", "top", "man", "pen",
    "red", "big", "cup", "pig", "log",
    "bag", "box", "jam", "milk", "rain",
    "boat", "tree", "corn", "cake", "blue",
    "jump", "sand", "rock", "shell", "grass",
    "snow", "light", "hand", "foot", "bell",
    "ring", "toy", "farm", "moon", "bird",
    "apple", "duck", "frog", "shoe", "farm",
    "king", "leaf", "nest", "star", "wagon"],
    2:["apple", "basket", "bright", "candy", "circle",
    "climb", "corner", "cotton", "dishes", "doctor",
    "dragon", "family", "farmer", "feather", "forest",
    "happy", "happen", "heavy", "hilltop", "honey",
    "jumping", "kitten", "ladder", "little", "market",
    "middle", "morning", "music", "openly", "painted",
    "paper", "pencil", "present", "rabbit", "riding",
    "school", "shadow", "silver", "smile", "snowy",
    "spider", "spring", "summer", "teacher", "thunder",
    "tiger", "turtle", "window", "winter", "yellow"],
    3:["afternoon", "almost", "animal", "basketball", "beautiful",
    "birthday", "bottle", "brother", "butterfly", "camera",
    "captain", "careful", "cheerful", "children", "climate",
    "cloudy", "country", "decided", "delicious", "different",
    "elephant", "excited", "family", "favorite", "forgotten",
    "friendly", "garden", "goldfish", "happen", "important",
    "inside", "jungle", "library", "mountain", "neighbor",
    "outside", "painter", "parade", "planet", "pocket",
    "question", "remember", "snowflake", "special", "station",
    "stronger", "summer", "teacher", "weather", "window"],
    4:["adventure", "apartment", "argument", "attention", "balance",
    "believe", "calendar", "careless", "category", "celebrate",
    "comfortable", "community", "consider", "curious", "decimal",
    "delicious", "direction", "discover", "education", "electric",
    "energy", "enormous", "favorite", "fraction", "freedom",
    "gentle", "history", "imagine", "important", "include",
    "library", "measurement", "memory", "minute", "mountain",
    "necessary", "neighbor", "pattern", "population", "position",
    "practice", "president", "promise", "purpose", "question",
    "sentence", "sincere", "special", "village", "weather"],
    5:["accurate", "active", "adventure", "ancient", "apology",
    "argument", "attention", "average", "behavior", "biology",
    "calculate", "career", "challenge", "character", "chemical",
    "colony", "communicate", "community", "compare", "complete",
    "comprehend", "conclusion", "conductor", "consider", "continent",
    "contrast", "creative", "curiosity", "decade", "decision",
    "democracy", "develop", "distance", "enormous", "equation",
    "excellent", "familiar", "fortunate", "function", "geography",
    "government", "grammar", "history", "imagination", "influence",
    "language", "measurement", "memory", "organism", "paragraph"],
    6:["abundant", "accurately", "adaptation", "ambition", "analysis",
    "ancestor", "apparent", "approach", "atmosphere", "attribute",
    "barrier", "beneficial", "calculate", "campaign", "category",
    "civilization", "collapse", "colony", "communicate", "competition",
    "conclusion", "consequence", "construct", "contrast", "convert",
    "critical", "culture", "declare", "determine", "develop",
    "discovery", "diversity", "efficient", "environment", "equation",
    "evidence", "experiment", "expression", "formation", "function",
    "gravity", "heritage", "importance", "independent", "influence",
    "molecule", "narrative", "perspective", "reaction", "tremendous"],
    7:["achievement", "adaptation", "advantage", "ambiguous", "analyze",
    "apparatus", "application", "argumentative", "artificial", "assumption",
    "atmosphere", "behavioral", "calculation", "capability", "category",
    "chronological", "circumstance", "collaboration", "colleague", "complexity",
    "component", "comprehensive", "consequence", "constellation", "contamination",
    "criteria", "data", "debate", "decision", "demonstration",
    "destination", "developed", "discipline", "distribute", "efficient",
    "elaborate", "elementary", "environmental", "essential", "evaluate",
    "evolution", "foundation", "hypothesis", "illustration", "influence",
    "interpretation", "literature", "magnitude", "phenomenon", "significance"],
    8:["adaptation", "advantageous", "agriculture", "analysis", "anticipate",
    "apparatus", "approximate", "architecture", "argumentative", "articulate",
    "assertive", "association", "attribute", "authentic", "biological",
    "circumstance", "collaboration", "commitment", "component", "comprehensive",
    "conceptual", "conservation", "consideration", "contamination", "cooperation",
    "correspondence", "definition", "description", "distribution", "efficiency",
    "elaboration", "environmental", "evaluation", "exaggeration", "explanation",
    "foundation", "hypothesis", "illustration", "independent", "influence",
    "interpretation", "justification", "measurement", "methodology", "organization",
    "perspective", "phenomenon", "preparation", "significance", "theoretical"],
    9:["acknowledge", "adaptation", "advocate", "aesthetic", "ambiguous",
    "analyze", "anomaly", "antagonist", "approximate", "articulate",
    "assertion", "assumption", "authenticity", "bias", "brevity",
    "chronological", "coincidence", "compromise", "connotation", "correlation",
    "credibility", "deduction", "demonstration", "depict", "discrepancy",
    "distortion", "elaboration", "empirical", "epiphany", "evaluate",
    "exposition", "figurative", "foreshadow", "hypothesis", "illustrate",
    "implication", "inference", "integrate", "intuition", "irony",
    "juxtaposition", "metaphor", "notion", "objective", "paradox",
    "preliminary", "rationale", "redundant", "symbolism", "transition"],
    10:["aberration", "abstracted", "acquisition", "adversity", "allegory",
    "allusion", "analytical", "anecdote", "antithesis", "arbitrary",
    "assertive", "belligerent", "benevolent", "camaraderie", "catalyst",
    "chronology", "cohesive", "compliance", "condone", "connotation",
    "convergence", "credibility", "decipher", "delineate", "denotation",
    "detrimental", "dichotomy", "discernment", "eloquence", "empirical",
    "ephemeral", "erroneous", "fallacy", "feasible", "fundamental",
    "hierarchy", "ideology", "imperative", "incessant", "inevitable",
    "meticulous", "negligible", "objective", "omniscient", "paradoxical",
    "peripheral", "pertinent", "plausible", "precursor", "synthesis"]}

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
