# Mini event tanımları
import random

MINI_EVENTS = [
    {
        "id": "bonus_cash",
        "name": "Beklenmedik Nakit Girişi",
        "desc": "Şirketinize beklenmedik bir nakit girişi oldu!",
        "effect": {"cash": 2000}
    },
    {
        "id": "tax_audit",
        "name": "Vergi Denetimi",
        "desc": "Vergi denetimi sonucu ceza ödediniz.",
        "effect": {"cash": -1500}
    },
    {
        "id": "employee_sick",
        "name": "Çalışan Hastalandı",
        "desc": "Bir çalışan hastalandı, verimlilik düştü.",
        "effect": {"energy": -10}
    },
    {
        "id": "viral_marketing",
        "name": "Viral Pazarlama",
        "desc": "Viral bir kampanya ile satışlar arttı!",
        "effect": {"cash": 1000, "energy": -5}
    },
    {
        "id": "equipment_break",
        "name": "Ekipman Arızası",
        "desc": "Bazı ekipmanlar arızalandı, tamir masrafı oluştu.",
        "effect": {"cash": -800}
    },
]

def apply_random_event(state):
    event = random.choice(MINI_EVENTS)
    # Etkiyi uygula
    effect = event.get("effect", {})
    for k, v in effect.items():
        if k in state and isinstance(state[k], (int, float)):
            state[k] += v
        elif k == "energy":
            state["energy"] = max(0, state.get("energy", 0) + v)
        elif k == "cash":
            state["cash"] = max(0, state.get("cash", 0) + v)
    # Olayı döndür
    return {"id": event["id"], "name": event["name"], "desc": event["desc"], "effect": effect}
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
            "unlocked": {},  # {"ach_id": "2025-09-01T12:34:56"}
            "all": [
                {"id": "first_day", "name": "İlk Günü Bitir", "desc": "İlk günü tamamla", "condition": {"day": 1}},
                {"id": "first_employee", "name": "İlk Çalışan", "desc": "İlk çalışanı işe al", "condition": {"employee_count": 1}},
                {"id": "first_department", "name": "İlk Departman", "desc": "İlk departmanı aç", "condition": {"department_count": 1}},
                {"id": "cash_5000", "name": "5000 TL Biriktir", "desc": "Kasada 5000 TL'ye ulaş", "condition": {"cash": 5000}},
                {"id": "ten_tasks", "name": "10 Görev Tamamla", "desc": "10 görev tamamla", "condition": {"completedTasks": 10}},
                {"id": "cash_10000", "name": "10.000 TL Biriktir", "desc": "Kasada 10.000 TL'ye ulaş", "condition": {"cash": 10000}},
                {"id": "five_departments", "name": "5 Departman Aç", "desc": "Toplam 5 departman aç", "condition": {"department_count": 5}},
                {"id": "twenty_employees", "name": "20 Çalışan", "desc": "Toplam 20 çalışanı işe al", "condition": {"employee_count": 20}},
                {"id": "thirty_days", "name": "30 Gün Hayatta Kal", "desc": "30 gün boyunca şirketi yönet", "condition": {"day": 30}}
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
        # Geriye dönük uyumluluk: unlocked eski tipte ise dönüştür
        if isinstance(state['achievements'].get('unlocked', None), list):
            # Eski unlocked: ["id1", "id2"] -> {"id1": "", "id2": ""}
            state['achievements']['unlocked'] = {k: "" for k in state['achievements']['unlocked']}
        return state

def save_state(state):
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)
