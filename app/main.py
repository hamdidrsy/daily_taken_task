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

    @app.route('/')
    def home():
        return '''
        <h1>TaskTycoon - Şirket Kurma Oyunu</h1>
        <p>API Endpointleri:</p>
        <ul>
            <li>GET /api/state - Şirket durumunu görüntüle</li>
            <li>POST /api/task - Görev yap</li>
            <li>POST /api/day/end - Günü bitir</li>
        </ul>
        <p>Örnek kullanım:</p>
        <pre>curl http://127.0.0.1:5000/api/state</pre>
        '''

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

    @app.route('/api/day/end', methods=['POST'])
    def end_day():
        state = load_state()
        departments = state['departments']
        
        # Gün sonu giderleri (maaş/işletme maliyetleri)
        base_upkeep = 50  # Temel işletme maliyeti
        total_upkeep = (base_upkeep + 
                       50 * departments['engLevel'] + 
                       40 * departments['rndLevel'] + 
                       30 * departments['hrLevel'] + 
                       60 * departments['salesLevel'])
        
        state['cash'] -= total_upkeep
        
        # Araştırma etkisi: her 10 research → reputation +1
        research_bonus = int(state['research'] / 10)
        state['reputation'] += research_bonus
        
        # Level kontrolü ve atlama
        current_level = state.get('level', 1)
        level_up_cost = 50 * current_level
        
        if state['xp'] >= level_up_cost:
            state['xp'] -= level_up_cost
            new_level = current_level + 1
            state['level'] = new_level
            
            # Level atladığında energy boost
            energy_bonus = 10
            state['maxEnergy'] += energy_bonus
            state['energy'] = min(state['maxEnergy'], state['energy'] + energy_bonus)
        
        # Gün sonu energy reset (kısmi yenileme)
        energy_restore = int(state['maxEnergy'] * 0.3)  # %30 yenileme
        state['energy'] = min(state['maxEnergy'], state['energy'] + energy_restore)
        
        # Gün sayacını artır
        state['day'] += 1
        
        # İstatistikler
        day_summary = {
            'previous_day': state['day'] - 1,
            'upkeep_cost': total_upkeep,
            'research_bonus': research_bonus,
            'energy_restored': energy_restore,
            'level_up': state.get('level', 1) > current_level
        }
        
        save_state(state)
        return jsonify({
            'state': state,
            'day_summary': day_summary
        })

    # Uygulama başlatılırken state dosyası oluşturulsun
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    if not os.path.exists(STATE_PATH):
        save_state(get_default_state())

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
