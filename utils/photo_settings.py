import json

from json_utils.json_struc import photo_settings

def get_photo_setting(chat_id):
    return photo_settings.get(chat_id, False)


def save_settings_photo():
    with open("photo_settings.json", "w") as file:
        json.dump(photo_settings, file)


def load_settings_photo():
    default_photo_settings = {"photo": False}
    try:
        with open("photo_settings.json", "r") as file:
            photo_settings.update(json.load(file))
    except FileNotFoundError:
        photo_settings.update(default_photo_settings)


load_settings_photo()