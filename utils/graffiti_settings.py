import json

from json_utils.json_struc import graffiti_settings

def get_graffiti_setting(chat_id):
    return graffiti_settings.get(chat_id, False)


def save_settings_graffiti():
    with open("graffiti_settings.json", "w") as file:
        json.dump(graffiti_settings, file)


def load_settings_graffiti():
    default_graffiti_settings = {"graffiti": False}
    try:
        with open("graffiti_settings.json", "r") as file:
            graffiti_settings.update(json.load(file))
    except FileNotFoundError:
        graffiti_settings.update(default_graffiti_settings)


load_settings_graffiti()