import json
import os

CHAT_FILE = "chat_history.json"

def load_chat():
    """Load chat history from JSON file"""
    if not os.path.exists(CHAT_FILE):
        return []

    try:
        with open(CHAT_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []


def save_chat(history):
    """Save chat history to JSON file"""
    with open(CHAT_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)