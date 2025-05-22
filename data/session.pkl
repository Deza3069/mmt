# utils/session_manager.py

import pickle
import os

SESSION_FILE = "data/session.pkl"

def save_session(data):
    with open(SESSION_FILE, "wb") as f:
        pickle.dump(data, f)

def load_session():
    if not os.path.exists(SESSION_FILE):
        return {}
    with open(SESSION_FILE, "rb") as f:
        return pickle.load(f)

def update_user_session(user_id, new_data):
    session = load_session()
    session[str(user_id)] = new_data
    save_session(session)

def get_user_session(user_id):
    session = load_session()
    return session.get(str(user_id), {})
