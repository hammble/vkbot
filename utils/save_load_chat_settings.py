import json

def save_chat_settings_to_file():
    """Сохраняет настройки чата в файл."""
    with open("chat_settings.json", "w") as file:
        json.dump(chat_settings, file)


def load_chat_settings_once():
    """Загружает настройки чата из файла один раз при запуске бота."""
    global chat_settings, chat_settings_loaded
    if not chat_settings_loaded: 
        try:
            with open("chat_settings.json", "r") as file:
                chat_settings = json.load(file)
        except FileNotFoundError:
            chat_settings = {}  
        chat_settings_loaded = True 


def load_chat_settings_from_file():
    """Загружает настройки чата из файла."""
    global chat_settings
    try:
        with open("chat_settings.json", "r") as file:
            chat_settings = json.load(file)
    except FileNotFoundError:
        chat_settings = {}  


load_chat_settings_from_file() 
load_chat_settings_once()