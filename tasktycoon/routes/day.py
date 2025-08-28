from flask import Blueprint, jsonify
from ..services.state_service import load_state, save_state
from ..services.economic_service import EconomicSystem

day_bp = Blueprint('day', __name__)

@day_bp.route('/api/day/end', methods=['POST'])
def end_day():
    state = load_state()
    
    # Snapshot cash before end-of-day processing (represents cash before daily costs applied)
    starting_cash = state.get('cash', 0)

    # Calculate economic costs using new system
    daily_costs = EconomicSystem.calculate_daily_costs(state)
    total_cost = daily_costs['total_cost']
    
    # Apply daily costs
    state['cash'] -= total_cost
    
    # Calculate financial health
    financial_health = EconomicSystem.get_financial_health(state)
    
    # Bankruptcy check
    if state['cash'] < 0:
        bankruptcy_penalty = abs(state['cash']) * 0.1  # 10% penalty for going negative
        state['cash'] = max(-1000, state['cash'])  # Minimum debt limit
        state['reputation'] -= 5  # Reputation hit
        bankruptcy_message = f"DİKKAT: Nakit eksi! {bankruptcy_penalty:.0f} TL ceza, -5 İtibar"
    else:
        bankruptcy_message = ""

    # Research bonus to reputation
    research_bonus = int(state['research'] / 10)
    state['reputation'] += research_bonus

    # Level up system
    current_level = state.get('level', 1)
    level_up_cost = 50 * current_level

    level_up_happened = False
    if state['xp'] >= level_up_cost:
        state['xp'] -= level_up_cost
        new_level = current_level + 1
        state['level'] = new_level
        level_up_happened = True
        
        # Level up benefits
        energy_bonus = 10
        state['maxEnergy'] += energy_bonus
        state['energy'] = min(state['maxEnergy'], state['energy'] + energy_bonus)

    # Energy restoration (based on company level and facilities)
    base_energy_restore = int(state['maxEnergy'] * 0.3)
    hr_bonus = state['departments'].get('hrLevel', 0) * 5  # HR improves work-life balance
    total_energy_restore = base_energy_restore + hr_bonus
    
    state['energy'] = min(state['maxEnergy'], state['energy'] + total_energy_restore)
    
    # Advance day
    state['day'] += 1

    # Day summary with detailed economic breakdown
    day_summary = {
        'previous_day': state['day'] - 1,
        'costs': {
            'base_cost': daily_costs['base_cost'],
            'department_costs': daily_costs['department_costs'],
            'employee_costs': daily_costs['employee_costs'],
            'total_cost': total_cost,
            'market_modifier': daily_costs['market_modifier']
        },
        'financial_health': financial_health,
        'research_bonus': research_bonus,
        'energy_restored': total_energy_restore,
        'level_up': level_up_happened,
        'bankruptcy_message': bankruptcy_message
    }

    # Add starting/ending cash snapshot so frontend can show income/expense/net
    ending_cash = state.get('cash', 0)
    day_summary['starting_cash'] = starting_cash
    day_summary['ending_cash'] = ending_cash
    day_summary['net_change'] = ending_cash - starting_cash

    # Günlük özet geçmişine ekle
    if 'dayHistory' not in state:
        state['dayHistory'] = []
    state['dayHistory'].append(day_summary)

    save_state(state)

    return jsonify({
        'success': True,
        'message': f"Gün {day_summary['previous_day']} tamamlandı! Toplam maliyet: {total_cost:.0f} TL",
        'state': state,
        'day_summary': day_summary
    })

@day_bp.route('/api/energy/restore', methods=['POST']) 
def restore_energy():
    """Restore energy during the day (costs money)"""
    state = load_state()
    
    # Energy restoration cost based on company level
    restore_cost = 50 * state.get('level', 1)
    
    if state['cash'] < restore_cost:
        return jsonify({
            'success': False,
            'error': f'Yetersiz nakit! Gerekli: {restore_cost} TL'
        }), 400
    
    # Restore 50% energy
    energy_restore = int(state['maxEnergy'] * 0.5)
    state['energy'] = min(state['maxEnergy'], state['energy'] + energy_restore)
    state['cash'] -= restore_cost
    
    save_state(state)
    
    return jsonify({
        'success': True,
        'message': f'Enerji yenilendi! +{energy_restore} Enerji, -{restore_cost} TL',
        'energy_restored': energy_restore,
        'cost': restore_cost,
        'state': state
    })

@day_bp.route('/api/economics/overview', methods=['GET'])
def economics_overview():
    """Get comprehensive economic overview"""
    state = load_state()
    
    # Daily costs breakdown
    daily_costs = EconomicSystem.calculate_daily_costs(state)
    
    # Financial health
    financial_health = EconomicSystem.get_financial_health(state)
    
    # Task economics preview
    task_preview = {}
    for task_type in ['work', 'research', 'network']:
        task_preview[task_type] = EconomicSystem.calculate_task_reward(task_type, state)
    
    # Employee efficiency
    employee_efficiency = []
    for emp in state['employees']:
        eff = EconomicSystem.calculate_employee_efficiency(emp, state)
        employee_efficiency.append({
            'name': emp['name'],
            'efficiency': eff
        })
    
    return jsonify({
        'daily_costs': daily_costs,
        'financial_health': financial_health,
        'task_economics': task_preview,
        'employee_efficiency': employee_efficiency,
        'market_day': state.get('day', 1)
    })
