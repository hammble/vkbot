import json
import time

from json_utils.json_files import MUTE_FILE

def remove_mute_entry(peer_id, user_id):
    with open(MUTE_FILE, "r") as file:
        lines = file.readlines()

    with open(MUTE_FILE, "w") as file:
        for line in lines:
            mute_entry = json.loads(line)
            if mute_entry["peer_id"] == peer_id and mute_entry["sender_id"] == user_id:
                continue  # Пропускаем запись для удаления
            file.write(line)


def mute_save(peer_id, sender_id, text):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    with open(MUTE_FILE, "a") as file:
        mute_entry = {
            "peer_id": peer_id,
            "sender_id": sender_id,
            "text": text,
            "timestamp": timestamp
        }
        json.dump(mute_entry, file)
        file.write("\n")

def get_mute(peer_id):
    mutes = []
    with open(MUTE_FILE, "r") as file:
        for line in file:
            mute_entry = json.loads(line)
            if mute_entry["peer_id"] == peer_id:
                mutes.append(mute_entry)
    return mutes