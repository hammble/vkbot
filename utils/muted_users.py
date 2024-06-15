import json

from json_utils.json_files import MUTED_USERS_FILE

def load_muted_users():
    try:
        with open(MUTED_USERS_FILE, 'r') as file:
            muted_users = json.load(file)
    except FileNotFoundError:
        muted_users = []
    return muted_users

def save_muted_users(muted_users):
    with open(MUTED_USERS_FILE, 'w') as file:
        json.dump(muted_users, file)

muted_users = load_muted_users()