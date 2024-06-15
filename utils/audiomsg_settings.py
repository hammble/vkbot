import json

from json_utils.json_struc import audio_message_settings

def get_audio_message_setting(chat_id):
    return audio_message_settings.get(chat_id, False)


def save_settings_audio_message():
    with open("audio_message_settings.json", "w") as file:
        json.dump(audio_message_settings, file)


def load_settings_audio_message():
    default_audio_message_settings = {"audio_message": False}
    try:
        with open("audio_message_settings.json", "r") as file:
            audio_message_settings.update(json.load(file))
    except FileNotFoundError:
        audio_message_settings.update(default_audio_message_settings)


load_settings_audio_message()