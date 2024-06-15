import json

from json_utils.json_struc import close_chat_settings

def get_close_chat_setting(chat_id):
    return close_chat_settings.get(chat_id, False)


def save_close_chat():
    with open("close_chat.json", "w") as file:
        json.dump(close_chat_settings, file)


def load_close_chat_video():
    default_close_chat_settings = {"close_chat": False}
    try:
        with open("close_chat_settings.json", "r") as file:
            close_chat_settings.update(json.load(file))
    except FileNotFoundError:
        close_chat_settings.update(default_close_chat_settings)


load_close_chat_video()