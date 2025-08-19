from flask import Flask, jsonify
import os
import json


def create_app():
    app = Flask(__name__)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATE_PATH = os.path.join(BASE_DIR, '..', 'data', 'state.json')


    def get_default_state():
        return {
            "day": 1,
            "cash": 1000,
            "xp": 0,
            "energy": 100,
            "maxEnergy": 100,
            "research": 0,
            "reputation": 0,
            "departments": {
                "engLevel": 0,
                "rndLevel": 0,
                "hrLevel": 0,
                "salesLevel": 0
            }
        }

    def load_state():
        if not os.path.exists(STATE_PATH):
            save_state(get_default_state())
        with open(STATE_PATH, 'r') as f:
            return json.load(f)

    def save_state(state):
        with open(STATE_PATH, 'w') as f:
            json.dump(state, f, indent=2)

    @app.route('/api/state', methods=['GET'])
    def get_state():
        state = load_state()
        return jsonify(state)

    # Uygulama başlatılırken state dosyası oluşturulsun
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    if not os.path.exists(STATE_PATH):
        save_state(get_default_state())

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
