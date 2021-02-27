import requests
import db

BASE_URL = "https://tankirating.org/api"


def load_api_resource(uri, db_path): 
    data = requests.get(f'{BASE_URL}/{uri}').json()
    db.save_json(db_path, data)
    return data