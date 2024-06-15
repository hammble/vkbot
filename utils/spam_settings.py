import json

from json_utils.json_struc import spam_settings

def get_spam_setting(chat_id):
    return spam_settings.get(chat_id, True)

def save_settings_spam():
    with open("spam_settings.json", "w") as file:
        json.dump(spam_settings, file)

def load_settings_spam():
    default_spam_settings = {"spam": True}
    try:
        with open("spam_settings.json", "r") as file:
            spam_settings.update(json.load(file))
    except FileNotFoundError:
        spam_settings.update(default_spam_settings)

load_settings_spam()