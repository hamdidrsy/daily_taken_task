from flask import Blueprint, jsonify
from ..services.state_service import load_state

state_bp = Blueprint('state', __name__)

@state_bp.route('/api/state', methods=['GET'])
def get_state():
    state = load_state()
    return jsonify(state)
