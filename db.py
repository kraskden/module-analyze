import json

USER_PATH = "res/users.json"

USER_PREFIX = "res/users"

def save_json(path, obj):
    with open(path, 'w+') as f:
        json.dump(obj, f)

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)