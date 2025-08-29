from flask import Blueprint, jsonify, request
from ..services.state_service import load_state
from ..services.economic_service import EconomicSystem
import json

dashboard_bp = Blueprint('dashboard', __name__)

# Kullanıcı başarımlarını döndüren endpoint
@dashboard_bp.route('/api/achievements', methods=['GET'])
def get_achievements():
    state = load_state()
    ach = state.get('achievements', {})
    unlocked = set(ach.get('unlocked', []))
    all_achs = ach.get('all', [])
    # Her başarım için unlocked bilgisini ekle
    ach_list = []
    for a in all_achs:
        ach_list.append({
            'id': a['id'],
            'name': a['name'],
            'desc': a['desc'],
            'unlocked': a['id'] in unlocked
        })
    return jsonify({
        'success': True,
        'achievements': ach_list
    })

@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get comprehensive dashboard statistics with economic analysis"""
    try:
        state = load_state()
        
        # Calculate economic health
        economic_system = EconomicSystem()
        financial_health = economic_system.get_financial_health(state)
        daily_costs = economic_system.calculate_daily_costs(state)
        
        # Department statistics
        department_stats = {}
        total_department_value = 0
        
        for dept in ['engLevel', 'rndLevel', 'hrLevel', 'salesLevel']:
            level = state['departments'].get(dept, 0)
            dept_value = 0
            
            if level > 0:
                setup_cost = EconomicSystem.DEPARTMENT_COSTS[dept]['setup']
                upgrade_costs = sum(EconomicSystem.calculate_upgrade_cost(dept, i) 
                                  for i in range(max(0, level-1)))
                dept_value = setup_cost + upgrade_costs
            
            department_stats[dept] = {
                'level': level,
                'value': dept_value,
                'daily_cost': EconomicSystem.DEPARTMENT_COSTS[dept]['daily'] * max(1, level),
                'status': 'active' if level > 0 else 'locked'
            }
            total_department_value += dept_value
        
        # Employee statistics
        employee_stats = {
            'total_employees': len(state.get('employees', [])),
            'max_employees': _calculate_max_employees(state),
            'total_salaries': sum(emp.get('salary', 500) for emp in state.get('employees', [])),
            'efficiency_bonus': _calculate_team_efficiency(state)
        }
        
        # Financial overview
        financial_overview = {
            'current_cash': state['cash'],
            'daily_income_potential': _estimate_daily_income(state),
            'daily_expenses': daily_costs['total_cost'],
            'net_daily_flow': _estimate_daily_income(state) - daily_costs['total_cost'],
            'financial_health': financial_health,
            'runway_days': financial_health.get('runway_days', 0)
        }
        
        # Task performance
        task_performance = {
            'completed_tasks': state.get('completedTasks', 0),
            'success_rate': _calculate_success_rate(state),
            'average_reward': _calculate_average_reward(state),
            'breakthrough_count': state.get('breakthroughs', 0)
        }
        
        # Company valuation
        company_valuation = {
            'total_assets': state['cash'] + total_department_value,
            'department_value': total_department_value,
            'liquid_assets': state['cash'],
            'growth_rate': _calculate_growth_rate(state)
        }
        
        return jsonify({
            'success': True,
            'financial_overview': financial_overview,
            'department_stats': department_stats,
            'employee_stats': employee_stats,
            'task_performance': task_performance,
            'company_valuation': company_valuation,
            'daily_costs_breakdown': daily_costs,
            'game_stats': {
                'current_day': state.get('currentDay', 1),
                'energy': state.get('energy', 100),
                'max_energy': state.get('maxEnergy', 100),
                'experience': state.get('experience', 0)
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Dashboard hatası: {str(e)}',
            'error_type': type(e).__name__
        }), 500

@dashboard_bp.route('/api/dashboard/predictions', methods=['GET'])
def get_predictions():
    """Get financial predictions and recommendations"""
    try:
        state = load_state()
        economic_system = EconomicSystem()
        
        # Calculate predictions for next 7 days
        predictions = []
        current_cash = state['cash']
        
        for day in range(1, 8):
            daily_costs = economic_system.calculate_daily_costs(state)['total_cost']
            estimated_income = _estimate_daily_income(state)
            net_flow = estimated_income - daily_costs
            current_cash += net_flow
            
            predictions.append({
                'day': day,
                'estimated_cash': max(0, current_cash),
                'income': estimated_income,
                'expenses': daily_costs,
                'net_flow': net_flow,
                'status': 'healthy' if current_cash > daily_costs * 3 else 'warning' if current_cash > 0 else 'critical'
            })
        
        # Generate recommendations
        recommendations = _generate_recommendations(state, predictions)
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'recommendations': recommendations
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Predictions hatası: {str(e)}',
            'error_type': type(e).__name__
        }), 500

def _calculate_max_employees(state):
    """Calculate maximum employees based on HR level"""
    hr_level = state['departments'].get('hrLevel', 0)
    return hr_level * 3 + 2 if hr_level > 0 else 2

def _calculate_team_efficiency(state):
    """Calculate team efficiency bonus"""
    employees = state.get('employees', [])
    if not employees:
        return 0
    
    total_efficiency = sum(emp.get('efficiency', 50) for emp in employees)
    avg_efficiency = total_efficiency / len(employees)
    return (avg_efficiency - 50) / 100  # Convert to bonus percentage

def _estimate_daily_income(state):
    """Estimate potential daily income based on current stats"""
    base_income = 100  # Base daily income potential
    
    # Department bonuses
    eng_bonus = state['departments'].get('engLevel', 0) * 50
    sales_bonus = state['departments'].get('salesLevel', 0) * 75
    
    # Employee bonus
    employee_count = len(state.get('employees', []))
    employee_bonus = employee_count * 25
    
    return base_income + eng_bonus + sales_bonus + employee_bonus

def _calculate_success_rate(state):
    """Calculate overall task success rate"""
    completed = state.get('completedTasks', 0)
    failed = state.get('failedTasks', 0)
    
    if completed + failed == 0:
        return 100
    
    return (completed / (completed + failed)) * 100

def _calculate_average_reward(state):
    """Calculate average task reward"""
    task_history = state.get('taskHistory', [])
    if not task_history:
        return 0
    
    total_rewards = sum(task.get('reward', 0) for task in task_history)
    return total_rewards / len(task_history)

def _calculate_growth_rate(state):
    """Calculate company growth rate based on recent performance"""
    # This would ideally use historical data
    # For now, estimate based on current capabilities
    department_count = sum(1 for dept in ['engLevel', 'rndLevel', 'hrLevel', 'salesLevel'] 
                          if state['departments'].get(dept, 0) > 0)
    employee_count = len(state.get('employees', []))
    
    return min(100, (department_count * 20) + (employee_count * 5))

def _generate_recommendations(state, predictions):
    """Generate actionable recommendations based on financial analysis"""
    recommendations = []
    
    # Check cash flow
    critical_days = [p for p in predictions if p['status'] == 'critical']
    if critical_days:
        recommendations.append({
            'type': 'warning',
            'title': 'Nakit Akışı Uyarısı',
            'message': f'{len(critical_days)} gün içinde nakit tükenebilir. Acil gelir gerekli!',
            'action': 'Yüksek ödüllü görevlere odaklan'
        })
    
    # Check department investments
    locked_departments = [dept for dept in ['engLevel', 'rndLevel', 'hrLevel', 'salesLevel'] 
                         if state['departments'].get(dept, 0) == 0]
    if locked_departments and state['cash'] > 1000:
        recommendations.append({
            'type': 'investment',
            'title': 'Departman Yatırımı',
            'message': f'{len(locked_departments)} departman henüz açılmamış. Yatırım fırsatı!',
            'action': 'Departman açmayı düşün'
        })
    
    # Check employee efficiency
    employees = state.get('employees', [])
    if employees:
        avg_efficiency = sum(emp.get('efficiency', 50) for emp in employees) / len(employees)
        if avg_efficiency < 60:
            recommendations.append({
                'type': 'optimization',
                'title': 'Çalışan Verimliliği',
                'message': 'Çalışan verimliliği düşük. Eğitim düşün.',
                'action': 'Çalışanları eğit veya yenilerini işe al'
            })
    
    return recommendations


# Simple history endpoint to fetch last N day summaries
@dashboard_bp.route('/api/history', methods=['GET'])
def get_history():
    try:
        n = int(request.args.get('n', 7))
    except Exception:
        n = 7

    state = load_state()
    history = state.get('dayHistory', []) or []

    # Return the last n entries (most recent last)
    recent = history[-n:]

    return jsonify({
        'success': True,
        'count': len(recent),
        'history': recent
    })
