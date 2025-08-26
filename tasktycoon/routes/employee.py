from flask import Blueprint, request, jsonify
from ..services.state_service import load_state, save_state
from ..services.economic_service import EconomicSystem
import random
import uuid

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/api/employees/hire', methods=['POST'])
@employee_bp.route('/api/employee/hire', methods=['POST'])
def hire_employee():
    """Hire a new employee with economic system integration"""
    data = request.get_json()
    employee_type = data.get('type', 'general')
    
    state = load_state()
    
    # Check HR department level for employee limit
    hr_level = state['departments'].get('hrLevel', 0)
    if hr_level == 0:
        return jsonify({'success': False, 'error': 'İK departmanı açılmamış'}), 400
    
    # Calculate employee limits
    max_employees = hr_level * 3 + 2
    current_employees = len(state.get('employees', []))
    
    if current_employees >= max_employees:
        return jsonify({
            'success': False, 
            'error': f'Çalışan limiti aşıldı! Maksimum: {max_employees}'
        }), 400
    
    # Generate employee with economic system
    new_employee = _generate_employee(employee_type, state)
    
    # Calculate hiring cost
    hiring_cost = EconomicSystem.calculate_hiring_cost(employee_type, current_employees)
    
    if state['cash'] < hiring_cost:
        return jsonify({
            'success': False,
            'error': f'Yetersiz nakit! Gerekli: {hiring_cost:.0f} TL'
        }), 400
    
    # Apply hiring
    state['cash'] -= hiring_cost
    if 'employees' not in state:
        state['employees'] = []
    
    state['employees'].append(new_employee)
    save_state(state)
    
    return jsonify({
        'success': True,
        'message': f'{new_employee["name"]} işe alındı!',
        'employee': new_employee,
        'hiring_cost': hiring_cost,
        'state': state
    })

@employee_bp.route('/api/employee/<employee_id>/train', methods=['POST'])
def train_employee(employee_id):
    """Train employee to improve efficiency"""
    state = load_state()
    employees = state.get('employees', [])
    
    employee = next((emp for emp in employees if emp['id'] == employee_id), None)
    if not employee:
        return jsonify({'success': False, 'error': 'Çalışan bulunamadı'}), 404
    
    # Calculate training cost based on current efficiency
    current_efficiency = employee.get('efficiency', 50)
    training_cost = EconomicSystem.calculate_training_cost(current_efficiency)
    
    if state['cash'] < training_cost:
        return jsonify({
            'success': False,
            'error': f'Yetersiz nakit! Gerekli: {training_cost:.0f} TL'
        }), 400
    
    # Apply training
    state['cash'] -= training_cost
    
    # Efficiency improvement (5-15% boost, diminishing returns)
    efficiency_boost = random.randint(5, 15) * (1 - current_efficiency / 200)
    new_efficiency = min(100, current_efficiency + efficiency_boost)
    employee['efficiency'] = new_efficiency
    
    # Possible skill improvement
    if random.random() < 0.3:  # 30% chance for new skill
        available_skills = ['Yazılım', 'Tasarım', 'Analiz', 'Yönetim', 'Satış', 'Araştırma']
        current_skills = employee.get('skills', [])
        new_skills = [skill for skill in available_skills if skill not in current_skills]
        
        if new_skills:
            employee['skills'].append(random.choice(new_skills))
    
    save_state(state)
    
    return jsonify({
        'success': True,
        'message': f'{employee["name"]} eğitildi! Verimlilik: %{new_efficiency:.0f}',
        'employee': employee,
        'training_cost': training_cost,
        'efficiency_gain': efficiency_boost,
        'state': state
    })

@employee_bp.route('/api/employee/<employee_id>/fire', methods=['DELETE'])
def fire_employee(employee_id):
    """Fire an employee"""
    state = load_state()
    employees = state.get('employees', [])
    
    employee = next((emp for emp in employees if emp['id'] == employee_id), None)
    if not employee:
        return jsonify({'success': False, 'error': 'Çalışan bulunamadı'}), 404
    
    # Calculate severance pay
    salary = employee.get('salary', 500)
    severance_pay = salary * 0.5  # Half month severance
    
    # Remove employee and pay severance
    state['employees'] = [emp for emp in employees if emp['id'] != employee_id]
    state['cash'] -= severance_pay
    
    save_state(state)
    
    return jsonify({
        'success': True,
        'message': f'{employee["name"]} işten çıkarıldı',
        'severance_pay': severance_pay,
        'state': state
    })

@employee_bp.route('/api/employees/overview', methods=['GET'])
def employees_overview():
    """Get detailed employee overview"""
    state = load_state()
    employees = state.get('employees', [])
    
    # Calculate employee statistics
    total_salaries = sum(emp.get('salary', 500) for emp in employees)
    avg_efficiency = sum(emp.get('efficiency', 50) for emp in employees) / len(employees) if employees else 0
    
    # Department analysis
    hr_level = state['departments'].get('hrLevel', 0)
    max_employees = hr_level * 3 + 2 if hr_level > 0 else 0
    
    # Skill distribution
    all_skills = []
    for emp in employees:
        all_skills.extend(emp.get('skills', []))
    
    skill_counts = {}
    for skill in all_skills:
        skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    return jsonify({
        'success': True,
        'employees': employees,
        'statistics': {
            'total_employees': len(employees),
            'max_employees': max_employees,
            'total_salaries': total_salaries,
            'average_efficiency': avg_efficiency,
            'skill_distribution': skill_counts,
            'hiring_available': len(employees) < max_employees,
            'monthly_cost': total_salaries * 30  # Estimate monthly cost
        }
    })

@employee_bp.route('/api/employee/market', methods=['GET'])
def employee_market():
    """Get available employees for hiring"""
    state = load_state()
    current_employees = len(state.get('employees', []))
    
    # Generate 3-5 available candidates
    candidates = []
    for i in range(random.randint(3, 5)):
        employee_type = random.choice(['developer', 'designer', 'analyst', 'manager', 'sales'])
        candidate = _generate_employee(employee_type, state)
        
        # Add hiring cost
        candidate['hiring_cost'] = EconomicSystem.calculate_hiring_cost(employee_type, current_employees)
        candidates.append(candidate)
    
    return jsonify({
        'success': True,
        'candidates': candidates
    })

def _generate_employee(employee_type, state):
    """Generate a new employee with realistic stats"""
    # Name pools
    names = [
        'Ahmet Yılmaz', 'Ayşe Kaya', 'Mehmet Demir', 'Fatma Çelik', 'Mustafa Şahin',
        'Zeynep Öz', 'Ali Koç', 'Emine Arslan', 'Hüseyin Güler', 'Hatice Aydın',
        'İbrahim Özkan', 'Elif Polat', 'Murat Eren', 'Seda Tunç', 'Emre Balcı'
    ]
    
    # Base employee structure
    employee = {
        'id': str(uuid.uuid4()),
        'name': random.choice(names),
        'type': employee_type,
        'efficiency': random.randint(40, 80),
        'salary': 0,
        'skills': [],
        'experience': random.randint(1, 10),
        'hired_date': state.get('currentDay', 1)
    }
    
    # Type-specific adjustments
    if employee_type == 'developer':
        employee['skills'] = random.sample(['Python', 'JavaScript', 'React', 'SQL'], random.randint(1, 3))
        employee['salary'] = random.randint(600, 1200)
        employee['efficiency'] += random.randint(0, 10)
        
    elif employee_type == 'designer':
        employee['skills'] = random.sample(['UI/UX', 'Grafik Tasarım', 'Figma', 'Adobe'], random.randint(1, 3))
        employee['salary'] = random.randint(500, 1000)
        
    elif employee_type == 'analyst':
        employee['skills'] = random.sample(['Veri Analizi', 'Excel', 'Power BI', 'İstatistik'], random.randint(1, 3))
        employee['salary'] = random.randint(550, 900)
        
    elif employee_type == 'manager':
        employee['skills'] = random.sample(['Proje Yönetimi', 'Liderlik', 'Planlama', 'İletişim'], random.randint(2, 4))
        employee['salary'] = random.randint(800, 1500)
        employee['efficiency'] += random.randint(5, 15)
        
    elif employee_type == 'sales':
        employee['skills'] = random.sample(['Satış', 'Müşteri İlişkileri', 'Pazarlama', 'Sunum'], random.randint(1, 3))
        employee['salary'] = random.randint(500, 1000)
    
    # Adjust salary based on experience and efficiency
    experience_bonus = employee['experience'] * 50
    efficiency_bonus = (employee['efficiency'] - 50) * 10
    employee['salary'] = int(employee['salary'] + experience_bonus + efficiency_bonus)
    
    return employee
