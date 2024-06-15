import json

from json_utils.json_struc import doc_settings

def get_doc_setting(chat_id):
    return doc_settings.get(chat_id, False)


def save_settings_doc():
    with open("doc_settings.json", "w") as file:
        json.dump(doc_settings, file)


def load_settings_doc():
    default_doc_settings = {"doc": False}
    try:
        with open("doc_settings.json", "r") as file:
            doc_settings.update(json.load(file))
    except FileNotFoundError:
        doc_settings.update(default_doc_settings)


load_settings_doc()