import os
import json
from ..config import STATE_PATH

def get_default_state():
    return {
        "day": 0,
        "currentDay": 0,
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
        "employees": [],
        "completedTasks": 0,
        "failedTasks": 0,
        "breakthroughs": 0,
        "taskHistory": [],
        "dayHistory": []
    }

def load_state():
    if not os.path.exists(STATE_PATH):
        save_state(get_default_state())
    with open(STATE_PATH, 'r') as f:
        state = json.load(f)
        # Geriye dönük uyumluluk için dayHistory yoksa ekle
        if 'dayHistory' not in state:
            state['dayHistory'] = []
        return state

def save_state(state):
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)
