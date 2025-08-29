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
        "dayHistory": [],
        "achievements": {
            "unlocked": [],
            "all": [
                {"id": "first_day", "name": "İlk Günü Bitir", "desc": "İlk günü tamamla", "condition": {"day": 1}},
                {"id": "first_employee", "name": "İlk Çalışan", "desc": "İlk çalışanı işe al", "condition": {"employee_count": 1}},
                {"id": "first_department", "name": "İlk Departman", "desc": "İlk departmanı aç", "condition": {"department_count": 1}},
                {"id": "cash_5000", "name": "5000 TL Biriktir", "desc": "Kasada 5000 TL'ye ulaş", "condition": {"cash": 5000}},
                {"id": "ten_tasks", "name": "10 Görev Tamamla", "desc": "10 görev tamamla", "condition": {"completedTasks": 10}}
            ]
        }
    }

def load_state():
    if not os.path.exists(STATE_PATH):
        save_state(get_default_state())
    with open(STATE_PATH, 'r') as f:
        state = json.load(f)
        # Geriye dönük uyumluluk için dayHistory yoksa ekle
        if 'dayHistory' not in state:
            state['dayHistory'] = []
        # Geriye dönük uyumluluk için achievements yoksa ekle
        if 'achievements' not in state:
            state['achievements'] = get_default_state()['achievements']
        return state

def save_state(state):
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)
