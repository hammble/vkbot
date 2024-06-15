import json

from json_utils.json_struc import close_settings

def get_close_setting(chat_id):
    return close_settings.get(chat_id, True)


def save_settings_close():
    with open("close_settings.json", "w") as file:
        json.dump(close_settings, file)


def load_settings_close():
    default_close_settings = {"close": True}
    try:
        with open("close_settings.json", "r") as file:
            close_settings.update(json.load(file))
    except FileNotFoundError:
        close_settings.update(default_close_settings)


load_settings_close()