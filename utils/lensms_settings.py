import json

def get_lensms_setting(chat_id):
    """Получает настройку длины сообщений для указанного чата."""
    return lensms_settings.get(chat_id, 4096)  # Возвращаем значение по умолчанию, если настройка не найдена


def set_lensms_setting(chat_id, length):
    """Устанавливает настройку длины сообщений для указанного чата."""
    lensms_settings[chat_id] = length


def save_lensms_settings():
    """Сохраняет настройки длины сообщений в файл."""
    with open("lensms_settings.json", "w") as file:
        json.dump(lensms_settings, file)


def load_lensms_settings_once():
    """Загружает настройки длины сообщений из файла один раз при запуске бота."""
    global lensms_settings, lensms_settings_loaded
    if not lensms_settings_loaded:  # Проверяем, были ли настройки уже загружены
        try:
            with open("lensms_settings.json", "r") as file:
                lensms_settings = json.load(file)
        except FileNotFoundError:
            lensms_settings = {"default": 4096}  # Создаем настройку по умолчанию, если файл не найден
        lensms_settings_loaded = True  # Устанавливаем флаг загрузки настроек


def load_lensms_settings():
    """Загружает настройки длины сообщений из файла."""
    global lensms_settings
    try:
        with open("lensms_settings.json", "r") as file:
            lensms_settings = json.load(file)
    except FileNotFoundError:
        lensms_settings = {"default": 4096}  # Создаем настройку по умолчанию, если файл не найден


load_lensms_settings() 
load_lensms_settings_once()