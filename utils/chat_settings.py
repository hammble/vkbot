import json

def load_chat_settings_from_file():
    global chat_settings
    try:
        with open("chat_settings.json", "r") as file:
            chat_settings = json.load(file)
    except FileNotFoundError:
        chat_settings = {}

def save_chat_settings_to_file():
    with open("chat_settings.json", "w") as file:
        json.dump(chat_settings, file)