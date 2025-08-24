from flask import Blueprint, request, jsonify
from ..services.state_service import load_state, save_state, get_default_state

manage_bp = Blueprint('manage', __name__)

@manage_bp.route('/api/save', methods=['POST'])
def manual_save():
    state = request.get_json()
    if not state:
        return jsonify({'error': 'State JSON body gereklidir'}), 400
    save_state(state)
    return jsonify({'message': 'State kaydedildi', 'state': state})

@manage_bp.route('/api/load', methods=['GET'])
def manual_load():
    state = load_state()
    return jsonify({'message': 'State yüklendi', 'state': state})

@manage_bp.route('/api/reset', methods=['POST'])
def manual_reset():
    default_state = get_default_state()
    save_state(default_state)
    return jsonify({'message': 'State sıfırlandı', 'state': default_state})
