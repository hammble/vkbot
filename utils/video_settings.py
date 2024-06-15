import json

from json_utils.json_struc import video_settings

def get_video_setting(chat_id):
    return video_settings.get(chat_id, False)

def save_settings_video():
    with open("video_settings.json", "w") as file:
        json.dump(video_settings, file)

def load_settings_video():
    default_video_settings = {"video": False}
    try:
        with open("video_settings.json", "r") as file:
            video_settings.update(json.load(file))
    except FileNotFoundError:
        video_settings.update(default_video_settings)


load_settings_video()