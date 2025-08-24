from flask import Blueprint, jsonify
from ..services.state_service import load_state, save_state

day_bp = Blueprint('day', __name__)

@day_bp.route('/api/day/end', methods=['POST'])
def end_day():
    state = load_state()
    departments = state['departments']

    base_upkeep = 50
    total_upkeep = (base_upkeep +
                   50 * departments['engLevel'] +
                   40 * departments['rndLevel'] +
                   30 * departments['hrLevel'] +
                   60 * departments['salesLevel'])

    state['cash'] -= total_upkeep

    research_bonus = int(state['research'] / 10)
    state['reputation'] += research_bonus

    current_level = state.get('level', 1)
    level_up_cost = 50 * current_level

    if state['xp'] >= level_up_cost:
        state['xp'] -= level_up_cost
        new_level = current_level + 1
        state['level'] = new_level
        energy_bonus = 10
        state['maxEnergy'] += energy_bonus
        state['energy'] = min(state['maxEnergy'], state['energy'] + energy_bonus)

    energy_restore = int(state['maxEnergy'] * 0.3)
    state['energy'] = min(state['maxEnergy'], state['energy'] + energy_restore)
    state['day'] += 1

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
