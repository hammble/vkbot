import json

from json_utils.json_files import BLOCKED_USERS_FILE

def load_blocked_users():
    try:
        with open(BLOCKED_USERS_FILE, 'r') as file:
            blocked_users = json.load(file)
    except FileNotFoundError:
        blocked_users = []
    return blocked_users


def save_blocked_users(blocked_users):
    with open(BLOCKED_USERS_FILE, 'w') as file:
        json.dump(blocked_users, file)


blocked_users = load_blocked_users()