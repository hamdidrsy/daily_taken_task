from flask import Blueprint, request, jsonify
from ..services.state_service import load_state, save_state
from ..services.economic_service import EconomicSystem

department_bp = Blueprint('department', __name__)

@department_bp.route('/api/department/<dept_type>/upgrade', methods=['POST'])
def upgrade_department(dept_type):
    """Upgrade department using new economic system"""
    valid_departments = ['engLevel', 'rndLevel', 'hrLevel', 'salesLevel']
    
    if dept_type not in valid_departments:
        return jsonify({'success': False, 'error': 'Geçersiz departman tipi'}), 400

    state = load_state()
    current_level = state['departments'].get(dept_type, 0)
    
    # Calculate upgrade cost using economic system
    upgrade_cost = EconomicSystem.calculate_upgrade_cost(dept_type, current_level)
    
    if upgrade_cost is None:
        return jsonify({'success': False, 'error': 'Maliyet hesaplanamadı'}), 400
    
    # Check if department needs to be unlocked first
    if current_level == 0:
        setup_cost = EconomicSystem.DEPARTMENT_COSTS[dept_type]['setup']
        total_cost = setup_cost
        action = 'açıldı'
    else:
        total_cost = upgrade_cost
        action = f'seviye {current_level + 1}\'e yükseltildi'
    
    # Check cash availability
    if state['cash'] < total_cost:
        return jsonify({
            'success': False, 
            'error': f'Yetersiz nakit! Gerekli: {total_cost:.0f} TL, Mevcut: {state["cash"]:.0f} TL'
        }), 400

    # Apply upgrade
    state['cash'] -= total_cost
    state['departments'][dept_type] += 1
    new_level = state['departments'][dept_type]
    
    # Calculate benefits of upgrade
    benefits = _calculate_department_benefits(dept_type, new_level)
    
    save_state(state)
    
    return jsonify({
        'success': True,
        'message': f'{dept_type} departmanı {action}! Maliyet: {total_cost:.0f} TL',
        'department': dept_type,
        'new_level': new_level,
        'cost': total_cost,
        'benefits': benefits,
        'state': state
    })

@department_bp.route('/api/department/<dept_type>/cost', methods=['GET'])
def get_upgrade_cost(dept_type):
    """Get upgrade cost for a department"""
    valid_departments = ['engLevel', 'rndLevel', 'hrLevel', 'salesLevel']
    
    if dept_type not in valid_departments:
        return jsonify({'error': 'Geçersiz departman tipi'}), 400
        
    state = load_state()
    current_level = state['departments'].get(dept_type, 0)
    
    if current_level == 0:
        # Department not unlocked yet
        setup_cost = EconomicSystem.DEPARTMENT_COSTS[dept_type]['setup']
        cost = setup_cost
        action = 'unlock'
    else:
        # Department upgrade
        cost = EconomicSystem.calculate_upgrade_cost(dept_type, current_level)
        action = 'upgrade'
    
    benefits = _calculate_department_benefits(dept_type, current_level + 1)
    
    return jsonify({
        'department': dept_type,
        'current_level': current_level,
        'cost': cost,
        'action': action,
        'benefits': benefits,
        'can_afford': state['cash'] >= cost
    })

@department_bp.route('/api/departments/overview', methods=['GET'])
def departments_overview():
    """Get comprehensive departments overview"""
    state = load_state()
    overview = {}
    
    for dept_type in ['engLevel', 'rndLevel', 'hrLevel', 'salesLevel']:
        current_level = state['departments'].get(dept_type, 0)
        
        if current_level == 0:
            cost = EconomicSystem.DEPARTMENT_COSTS[dept_type]['setup']
            action = 'unlock'
        else:
            cost = EconomicSystem.calculate_upgrade_cost(dept_type, current_level)
            action = 'upgrade'
        
        overview[dept_type] = {
            'current_level': current_level,
            'upgrade_cost': cost,
            'action': action,
            'daily_cost': EconomicSystem.DEPARTMENT_COSTS[dept_type]['daily'] * max(1, current_level),
            'benefits': _calculate_department_benefits(dept_type, current_level + 1),
            'can_afford': state['cash'] >= cost
        }
    
    return jsonify(overview)

def _calculate_department_benefits(dept_type, level):
    """Calculate benefits of having department at specific level"""
    benefits = {}
    
    if dept_type == 'engLevel':
        benefits = {
            'work_bonus': f"+{(level * 25):.0f}% iş görevi kazancı",
            'efficiency': f"Teknik verimlilik seviye {level}",
            'description': "Yazılım geliştirme ve teknik projeler"
        }
    elif dept_type == 'rndLevel':
        benefits = {
            'research_bonus': f"+{(level * 30):.0f}% araştırma verimliliği", 
            'breakthrough_chance': f"+{(level * 10):.0f}% teknoloji atılımı şansı",
            'description': "Araştırma ve geliştirme projeleri"
        }
    elif dept_type == 'hrLevel':
        benefits = {
            'employee_limit': f"Maksimum {level * 3 + 2} çalışan",
            'energy_bonus': f"+{level * 5} günlük enerji yenileme",
            'description': "İnsan kaynakları ve çalışan yönetimi"
        }
    elif dept_type == 'salesLevel':
        benefits = {
            'network_bonus': f"+{(level * 20):.0f}% networking kazancı",
            'client_chance': f"+{(level * 20):.0f}% yeni müşteri şansı",
            'description': "Satış ve müşteri ilişkileri"
        }
    
    return benefits
