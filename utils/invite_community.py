import json

from json_utils.json_struc import invite_settings

def get_invite_community_setting(chat_id):
    return invite_settings.get(chat_id, True)

def save_settings():
    with open("invite_settings.json", "w") as file:
        json.dump(invite_settings, file)

def load_settings():
    default_settings = {"invite_community": False}
    try:
        with open("invite_settings.json", "r") as file:
            invite_settings.update(json.load(file))
    except FileNotFoundError:
        invite_settings.update(default_settings)

load_settings()