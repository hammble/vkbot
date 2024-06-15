import json

from json_utils.json_struc import audio_settings

def get_audio_setting(chat_id):
    return audio_settings.get(chat_id, False)


def save_settings_audio():
    with open("audio_settings.json", "w") as file:
        json.dump(audio_settings, file)


def load_settings_audio():
    default_audio_settings = {"audio": False}
    try:
        with open("audio_settings.json", "r") as file:
            audio_settings.update(json.load(file))
    except FileNotFoundError:
        audio_settings.update(default_audio_settings)


load_settings_audio()