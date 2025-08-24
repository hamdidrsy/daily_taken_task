from flask import Blueprint, request, jsonify
from ..services.state_service import load_state, save_state

department_bp = Blueprint('department', __name__)

@department_bp.route('/api/department/unlock', methods=['POST'])
def unlock_department():
    data = request.get_json()
    department = data.get('department')
    valid_departments = ['eng', 'rnd', 'hr', 'sales']
    if department not in valid_departments:
        return jsonify({'error': 'Geçersiz departman tipi'}), 400

    state = load_state()
    departments = state['departments']
    dept_key = f"{department}Level"

    if departments[dept_key] > 0:
        return jsonify({'error': 'Departman zaten açık'}), 400

    unlock_costs = {
        'eng': 0,
        'rnd': 500,
        'hr': 300,
        'sales': 400
    }
    cost = unlock_costs[department]
    if state['cash'] < cost:
        return jsonify({'error': 'Yetersiz nakit'}), 400

    state['cash'] -= cost
    departments[dept_key] = 1
    save_state(state)
    return jsonify({
        'message': f'{department} departmanı açıldı',
        'cost': cost,
        'state': state
    })

@department_bp.route('/api/department/levelup', methods=['POST'])
def levelup_department():
    data = request.get_json()
    department = data.get('department')
    valid_departments = ['eng', 'rnd', 'hr', 'sales']
    if department not in valid_departments:
        return jsonify({'error': 'Geçersiz departman tipi'}), 400

    state = load_state()
    departments = state['departments']
    dept_key = f"{department}Level"
    current_level = departments[dept_key]

    if current_level == 0:
        return jsonify({'error': 'Departman henüz açılmamış'}), 400

    new_level = current_level + 1
    cost = 200 * new_level
    if state['cash'] < cost:
        return jsonify({'error': 'Yetersiz nakit'}), 400

    state['cash'] -= cost
    departments[dept_key] = new_level
    save_state(state)
    return jsonify({
        'message': f'{department} departmanı seviye {new_level}\'e yükseltildi',
        'cost': cost,
        'new_level': new_level,
        'state': state
    })
