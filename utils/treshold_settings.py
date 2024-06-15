from json_utils.json_struc import chat_settings

def get_message_threshold_setting(chat_id):
    """Получает настройку медленного режима для указанного чата."""
    return chat_settings.get(chat_id, {}).get("message_threshold",0)  # Возвращаем значение по умолчанию, если настройка не найдена


def set_message_threshold_setting(chat_id, threshold):
    """Устанавливает настройку медленного режима для указанного чата."""
    if chat_id not in chat_settings:
        chat_settings[chat_id] = {"message_threshold": threshold, "last_message_time": 0}
    else:
        chat_settings[chat_id]["message_threshold"] = threshold
        chat_settings[chat_id]["last_message_time"] = 0