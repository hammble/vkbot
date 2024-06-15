import json

def load_blocked_words(chat_id):
    try:
        with open(f"blocked_words_{chat_id}.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_blocked_words(chat_id, blocked_words):
    with open(f"blocked_words_{chat_id}.json", "w") as file:
        json.dump(blocked_words, file)