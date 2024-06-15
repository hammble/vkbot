import json

from json_utils.json_struc import kickall_settings

def get_kickall_setting(chat_id):
    return kickall_settings.get(chat_id, True)

def save_settings_kickall():
    with open("kickall_settings.json", "w") as file:
        json.dump(kickall_settings, file)

def load_settings_kickall():
    default_kickall_settings = {"kickall": True}
    try:
        with open("kickall_settings.json", "r") as file:
            kickall_settings.update(json.load(file))
    except FileNotFoundError:
        kickall_settings.update(default_kickall_settings)

load_settings_kickall()