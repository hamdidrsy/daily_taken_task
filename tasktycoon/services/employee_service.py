def get_next_employee_id(state):
    if not state["employees"]:
        return 1
    return max(emp["id"] for emp in state["employees"]) + 1

def get_max_employees(state):
    return state["departments"]["hrLevel"] * 3 + 2
