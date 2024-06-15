import json

from json_utils.json_struc import ruletka_settings

def get_ruletka_setting(chat_id):
    return ruletka_settings.get(chat_id, True)

def save_settings_ruletka():
    with open("ruletka_settings.json", "w") as file:
        json.dump(ruletka_settings, file)

def load_settings_ruletka():
    default_ruletka_settings = {"rultka": True}
    try:
        with open("ruletka_settings.json", "r") as file:
            ruletka_settings.update(json.load(file))
    except FileNotFoundError:
        ruletka_settings.update(default_ruletka_settings)

load_settings_ruletka()