import os
import json
from ..config import STATE_PATH

def get_default_state():
    return {
        "day": 1,
        "cash": 1000,
        "xp": 0,
        "level": 1,
        "energy": 100,
        "maxEnergy": 100,
        "research": 0,
        "reputation": 0,
        "departments": {
            "engLevel": 0,
            "rndLevel": 0,
            "hrLevel": 0,
            "salesLevel": 0
        },
        "employees": []
    }

def load_state():
    if not os.path.exists(STATE_PATH):
        save_state(get_default_state())
    with open(STATE_PATH, 'r') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)
