from flask import Blueprint, request, jsonify
from ..services.state_service import load_state, save_state
from ..services.economic_service import EconomicSystem
import random

task_bp = Blueprint('task', __name__)

@task_bp.route('/api/task', methods=['POST'])
def execute_task():
    data = request.get_json()
    task_type = data.get('task_type')

    if task_type not in ['work', 'research', 'network']:
        return jsonify({'success': False, 'error': 'Geçersiz görev tipi'}), 400

    state = load_state()
    
    # Calculate task economics
    task_economics = EconomicSystem.calculate_task_reward(task_type, state)
    
    if not task_economics:
        return jsonify({'success': False, 'error': 'Görev hesaplaması başarısız'}), 400
    
    # Check energy requirement
    energy_cost = task_economics['energy_cost']
    if state['energy'] < energy_cost:
        return jsonify({
            'success': False, 
            'error': f'Yetersiz enerji! Gerekli: {energy_cost}, Mevcut: {state["energy"]}'
        }), 400

    # Execute task based on type
    message = ""
    
    if task_type == 'work':
        reward = task_economics['final_reward']
        state['cash'] += reward
        state['xp'] += task_economics['xp_reward']
        message = f"Çalışma tamamlandı! +{reward:.0f} TL, +{task_economics['xp_reward']} XP kazandınız!"
        
    elif task_type == 'research':
        research_points = EconomicSystem.TASK_ECONOMICS['research']['research_points']
        dept_level = state['departments'].get('rndLevel', 0)
        final_research = research_points * (1 + dept_level * 0.3)
        
        state['research'] += final_research
        state['xp'] += task_economics['xp_reward']
        
        # Breakthrough chance
        breakthrough_chance = EconomicSystem.TASK_ECONOMICS['research']['breakthrough_chance']
        if random.random() < breakthrough_chance * (1 + dept_level * 0.1):
            breakthrough_bonus = random.randint(50, 150)
            state['cash'] += breakthrough_bonus
            message = f"Araştırma tamamlandı! +{final_research:.1f} Research, +{task_economics['xp_reward']} XP. BREAKTHROUGH! +{breakthrough_bonus} TL patent geliri!"
        else:
            message = f"Araştırma tamamlandı! +{final_research:.1f} Research, +{task_economics['xp_reward']} XP kazandınız!"
            
    elif task_type == 'network':
        reward = task_economics['final_reward']
        reputation_gain = EconomicSystem.TASK_ECONOMICS['network']['reputation_gain']
        
        state['cash'] += reward
        state['reputation'] += reputation_gain
        state['xp'] += task_economics['xp_reward']
        
        # Client acquisition chance
        client_chance = EconomicSystem.TASK_ECONOMICS['network']['client_chance']
        sales_level = state['departments'].get('salesLevel', 0)
        
        if random.random() < client_chance * (1 + sales_level * 0.2):
            client_bonus = random.randint(200, 500)
            state['cash'] += client_bonus
            message = f"Networking tamamlandı! +{reward:.0f} TL, +{reputation_gain} İtibar, +{task_economics['xp_reward']} XP. YENİ MÜŞTERİ! +{client_bonus} TL proje geliri!"
        else:
            message = f"Networking tamamlandı! +{reward:.0f} TL, +{reputation_gain} İtibar, +{task_economics['xp_reward']} XP kazandınız!"

    # Apply energy cost
    state['energy'] -= energy_cost
    state['energy'] = max(0, state['energy'])
    
    # Update task history
    state['completedTasks'] = state.get('completedTasks', 0) + 1
    
    # Add to task history
    task_record = {
        'type': task_type,
        'reward': task_economics.get('final_reward', 0),
        'day': state.get('currentDay', state.get('day', 1)),
        'timestamp': state.get('completedTasks', 0)
    }
    if 'taskHistory' not in state:
        state['taskHistory'] = []
    state['taskHistory'].append(task_record)
    
    # Calculate efficiency bonuses from employees
    total_efficiency_bonus = 0
    for employee in state['employees']:
        efficiency = EconomicSystem.calculate_employee_efficiency(employee, state)
        total_efficiency_bonus += efficiency['total_efficiency'] - 1.0
    
    if total_efficiency_bonus > 0:
        efficiency_cash_bonus = int(state.get('cash', 0) * 0.01 * total_efficiency_bonus)
        if efficiency_cash_bonus > 0:
            state['cash'] += efficiency_cash_bonus
            message += f" [Çalışan verimliliği: +{efficiency_cash_bonus} TL]"

    save_state(state)
    
    return jsonify({
        'success': True,
        'message': message,
        'task_economics': task_economics,
        'state': state
    })

@task_bp.route('/api/task/economics/<task_type>', methods=['GET'])
def get_task_economics(task_type):
    """Get economic analysis for a specific task type"""
    state = load_state()
    economics = EconomicSystem.calculate_task_reward(task_type, state)
    
    if not economics:
        return jsonify({'error': 'Geçersiz görev tipi'}), 400
        
    return jsonify(economics)
