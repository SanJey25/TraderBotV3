import json
import os

PROFILE_FILE = "data/profiles.json"
ITEMS_FILE = "data/items.json"

def init_files():
    os.makedirs("data", exist_ok=True)
    os.makedirs("images", exist_ok=True)
    for file, default in [(PROFILE_FILE, {}), (ITEMS_FILE, [])]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump(default, f)

def load_profiles():
    if not os.path.exists(PROFILE_FILE):
        init_files()
    with open(PROFILE_FILE, "r") as f:
        return json.load(f)

def save_profiles(profiles):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profiles, f, indent=2)

def load_items():
    if not os.path.exists(ITEMS_FILE):
        init_files()
    with open(ITEMS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_items(items):
    with open(ITEMS_FILE, "w") as f:
        json.dump(items, f, indent=2)
