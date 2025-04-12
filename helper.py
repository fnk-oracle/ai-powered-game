# helper.py

import os
import json
from dotenv import load_dotenv, find_dotenv

# Load env vars from a .env file, usually in project root
def load_env():
    _ = load_dotenv(find_dotenv())

# Save a dictionary (e.g., world state) to a JSON file
def save_world(world, filename):
    with open(filename, 'w') as f:
        json.dump(world, f, indent=4)

# Load a dictionary from a JSON file
def load_world(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Get the Together API key from .env
def get_together_api_key():
    load_env()
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        raise ValueError("TOGETHER_API_KEY is missing from environment variables.")
    return api_key

def get_game_state(inventory=None):
    return {
        "inventory": inventory or {},
        "start": "You awaken in a mossy glade, birds chirping faintly above.",
        "world": "A sprawling realm of magic and ancient ruins.",
        "kingdom": "Elaria",
        "town": "Oakshade",
        "character": "A curious traveler seeking lost relics."
    }

def start_game(main_loop, verbose=False):
    print("Game started! Type your actions below (type 'quit' to exit):\n")
    history = []

    while True:
        user_input = input(">> ")

        if user_input.lower() in ['quit', 'exit']:
            print("Thanks for playing!")
            break

        response = main_loop(user_input, history)
        print(response)

        history.append((response, user_input))

def is_safe(text):
    """Check if the generated story output is safe to display."""
    banned_keywords = ['suicide', 'murder', 'kill', 'rape', 'torture']
    text_lower = text.lower()
    return not any(word in text_lower for word in banned_keywords)
