from flask import Flask, jsonify, request
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

    @app.route('/api/task', methods=['POST'])
    def execute_task():
        data = request.get_json()
        task_type = data.get('task')
        
        if task_type not in ['kod_yaz', 'arastir', 'dinlen', 'satis_gorusmesi']:
            return jsonify({'error': 'Geçersiz görev tipi'}), 400
        
        state = load_state()
        departments = state['departments']
        
        # Görev kuralları
        if task_type == 'kod_yaz':
            energy_cost = 12
            if state['energy'] < energy_cost:
                return jsonify({'error': 'Yetersiz enerji'}), 400
            
            state['cash'] += 5 * (1 + departments['engLevel'])
            state['xp'] += 4
            state['energy'] -= energy_cost
            
        elif task_type == 'arastir':
            energy_cost = 10
            if state['energy'] < energy_cost:
                return jsonify({'error': 'Yetersiz enerji'}), 400
            
            state['research'] += 2 * (1 + departments['rndLevel'] * 0.5)
            state['xp'] += 3
            state['energy'] -= energy_cost
            
        elif task_type == 'dinlen':
            energy_restore = 25
            state['energy'] = min(state['maxEnergy'], state['energy'] + energy_restore)
            
        elif task_type == 'satis_gorusmesi':
            energy_cost = 15
            if state['energy'] < energy_cost:
                return jsonify({'error': 'Yetersiz enerji'}), 400
            
            state['cash'] += 20 * (1 + departments['salesLevel'] * 0.6 + state['reputation'] * 0.02)
            state['reputation'] += 1
            state['energy'] -= energy_cost
        
        # Enerji sıfırın altına düşmesin
        state['energy'] = max(0, state['energy'])
        
        save_state(state)
        return jsonify(state)

    # Uygulama başlatılırken state dosyası oluşturulsun
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    if not os.path.exists(STATE_PATH):
        save_state(get_default_state())

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
