import json

from json_utils.json_struc import stick_settings

def get_stick_setting(chat_id):
    return stick_settings.get(chat_id, False)


def save_settings_stick():
    with open("stick_settings.json", "w") as file:
        json.dump(stick_settings, file)


def load_settings_stick():
    default_stick_settings = {"stick": False}
    try:
        with open("stick_settings.json", "r") as file:
            stick_settings.update(json.load(file))
    except FileNotFoundError:
        stick_settings.update(default_stick_settings)


load_settings_stick()