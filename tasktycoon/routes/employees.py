from flask import Blueprint, request, jsonify
from ..services.state_service import load_state, save_state
from ..services.employee_service import get_next_employee_id, get_max_employees

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/api/employees', methods=['GET'])
def list_employees():
    state = load_state()
    return jsonify({"employees": state["employees"]})

@employees_bp.route('/api/employees', methods=['POST'])
def add_employee():
    state = load_state()
    data = request.get_json()
    name = data.get("name")
    role = data.get("role")
    salary = data.get("salary")
    if not name or not role or not salary:
        return jsonify({"error": "name, role ve salary zorunlu"}), 400
    if not isinstance(salary, (int, float)) or salary <= 0:
        return jsonify({"error": "salary pozitif sayı olmalı"}), 400
    if state["departments"]["hrLevel"] == 0:
        return jsonify({"error": "İK departmanı açılmadan çalışan eklenemez"}), 400
    if len(state["employees"]) >= get_max_employees(state):
        return jsonify({"error": "Maksimum çalışan sayısına ulaşıldı"}), 400
    if state["cash"] < salary:
        return jsonify({"error": "Yetersiz nakit (ilk maaş peşin ödenir)"}), 400
    state["cash"] -= salary
    emp_id = get_next_employee_id(state)
    employee = {"id": emp_id, "name": name, "role": role, "salary": salary}
    state["employees"].append(employee)
    save_state(state)
    return jsonify({"message": "Çalışan eklendi", "employee": employee, "state": state})

@employees_bp.route('/api/employees/<int:emp_id>', methods=['DELETE'])
def remove_employee(emp_id):
    state = load_state()
    employees = state["employees"]
    employee = next((e for e in employees if e["id"] == emp_id), None)
    if not employee:
        return jsonify({"error": "Çalışan bulunamadı"}), 404
    employees.remove(employee)
    save_state(state)
    return jsonify({"message": "Çalışan çıkarıldı", "employee": employee, "state": state})
