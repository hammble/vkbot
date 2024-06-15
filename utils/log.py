import json
import time

from json_utils.json_files import LOG_FILE

def save_message(peer_id, sender_id, text):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    with open(LOG_FILE, "a") as file:
        log_entry = {
            "peer_id": peer_id,
            "sender_id": sender_id,
            "text": text,
            "timestamp": timestamp
        }
        json.dump(log_entry, file)
        file.write("\n")

def get_logs(peer_id):
    logs = []
    with open(LOG_FILE, "r") as file:
        for line in file:
            log_entry = json.loads(line)
            if log_entry["peer_id"] == peer_id:
                logs.append(log_entry)
    return logs