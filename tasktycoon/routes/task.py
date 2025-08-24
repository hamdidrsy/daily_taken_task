from flask import Blueprint, request, jsonify
from ..services.state_service import load_state, save_state

task_bp = Blueprint('task', __name__)

@task_bp.route('/api/task', methods=['POST'])
def execute_task():
    data = request.get_json()
    task_type = data.get('task')

    if task_type not in ['kod_yaz', 'arastir', 'dinlen', 'satis_gorusmesi']:
        return jsonify({'error': 'Geçersiz görev tipi'}), 400

    state = load_state()
    departments = state['departments']

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

    state['energy'] = max(0, state['energy'])
    save_state(state)
    return jsonify(state)
