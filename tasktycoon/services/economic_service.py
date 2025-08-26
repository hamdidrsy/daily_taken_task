"""
Economic System Service - Day 8
Advanced economic balancing and financial calculations
"""

class EconomicSystem:
    """Handle economic calculations and balancing"""
    
    # Economic Constants
    BASE_DAILY_COSTS = {
        'office_rent': 50,
        'utilities': 25,
        'software_licenses': 30,
        'internet': 15
    }
    
    DEPARTMENT_COSTS = {
        'engLevel': {'setup': 0, 'daily': 40, 'upgrade_base': 200},
        'rndLevel': {'setup': 500, 'daily': 60, 'upgrade_base': 300}, 
        'hrLevel': {'setup': 300, 'daily': 25, 'upgrade_base': 150},
        'salesLevel': {'setup': 400, 'daily': 50, 'upgrade_base': 250}
    }
    
    TASK_ECONOMICS = {
        'work': {
            'base_reward': 80,
            'energy_cost': 12,
            'xp_reward': 8,
            'skill_multiplier': 1.2,
            'department_bonus': 'engLevel'
        },
        'research': {
            'base_reward': 0,
            'research_points': 6,
            'energy_cost': 18,
            'xp_reward': 12,
            'breakthrough_chance': 0.1,
            'department_bonus': 'rndLevel'
        },
        'network': {
            'base_reward': 40,
            'reputation_gain': 4,
            'energy_cost': 10,
            'xp_reward': 6,
            'client_chance': 0.15,
            'department_bonus': 'salesLevel'
        }
    }
    
    @staticmethod
    def calculate_daily_costs(state):
        """Calculate total daily operational costs"""
        base_cost = sum(EconomicSystem.BASE_DAILY_COSTS.values())
        
        # Department costs
        dept_costs = 0
        for dept_key, level in state['departments'].items():
            if level > 0:  # Only active departments
                dept_config = EconomicSystem.DEPARTMENT_COSTS[dept_key]
                dept_costs += dept_config['daily'] * level
        
        # Employee salaries
        employee_costs = sum(emp.get('salary', 0) for emp in state.get('employees', []))
        
        # Market conditions (new feature)
        market_modifier = EconomicSystem._get_market_modifier(state)
        
        total_cost = (base_cost + dept_costs + employee_costs) * market_modifier
        
        return {
            'base_cost': base_cost,
            'department_costs': dept_costs,
            'employee_costs': employee_costs,
            'market_modifier': market_modifier,
            'total_cost': round(total_cost, 2)
        }
    
    @staticmethod
    def calculate_task_reward(task_type, state):
        """Calculate dynamic task rewards based on state"""
        if task_type not in EconomicSystem.TASK_ECONOMICS:
            return None
            
        task_config = EconomicSystem.TASK_ECONOMICS[task_type]
        base_reward = task_config['base_reward']
        
        # Department bonus
        dept_key = task_config.get('department_bonus')
        dept_level = state['departments'].get(dept_key, 0)
        dept_multiplier = 1 + (dept_level * 0.25)
        
        # Company level bonus
        company_level = state.get('level', 1)
        level_multiplier = 1 + (company_level * 0.1)
        
        # Reputation bonus (for client-facing tasks)
        reputation = state.get('reputation', 0)
        reputation_multiplier = 1 + (reputation * 0.02)
        
        # Calculate final reward
        final_reward = base_reward * dept_multiplier * level_multiplier
        
        if task_type in ['network']:  # Client-facing tasks
            final_reward *= reputation_multiplier
            
        return {
            'base_reward': base_reward,
            'department_multiplier': dept_multiplier,
            'level_multiplier': level_multiplier,
            'reputation_multiplier': reputation_multiplier if task_type in ['network'] else 1.0,
            'final_reward': round(final_reward, 2),
            'energy_cost': task_config['energy_cost'],
            'xp_reward': task_config['xp_reward']
        }
    
    @staticmethod
    def calculate_upgrade_cost(department, current_level):
        """Calculate department upgrade cost with scaling"""
        if department not in EconomicSystem.DEPARTMENT_COSTS:
            return None
            
        base_cost = EconomicSystem.DEPARTMENT_COSTS[department]['upgrade_base']
        
        # Exponential scaling: each level costs more
        scaling_factor = 1.5 ** current_level
        final_cost = base_cost * scaling_factor
        
        return round(final_cost, 2)
    
    @staticmethod
    def calculate_employee_efficiency(employee, state):
        """Calculate employee contribution to company efficiency"""
        base_efficiency = 1.0
        
        # Experience bonus (simulated by department level)
        dept = employee.get('department', '')
        dept_key = f"{dept.lower()}Level"
        dept_level = state['departments'].get(dept_key, 0)
        
        experience_bonus = dept_level * 0.1
        
        # Salary satisfaction (higher paid = more productive)
        salary = employee.get('salary', 0)
        satisfaction_bonus = min(salary / 1000, 2.0)  # Cap at 2x
        
        efficiency = base_efficiency + experience_bonus + satisfaction_bonus
        
        return {
            'base_efficiency': base_efficiency,
            'experience_bonus': experience_bonus,
            'satisfaction_bonus': satisfaction_bonus,
            'total_efficiency': round(efficiency, 2)
        }
    
    @staticmethod
    def _get_market_modifier(state):
        """Simulate market conditions affecting costs"""
        day = state.get('currentDay', 1)
        
        # Market cycles every 30 days
        cycle_position = (day % 30) / 30
        
        # Sine wave for market fluctuation (0.8 to 1.2)
        import math
        market_modifier = 1 + 0.2 * math.sin(cycle_position * 2 * math.pi)
        
        return round(market_modifier, 3)
    
    @staticmethod
    def get_financial_health(state):
        """Analyze company financial health"""
        cash = state.get('cash', 0)
        daily_costs = EconomicSystem.calculate_daily_costs(state)['total_cost']
        
        # Days of runway
        days_of_runway = cash / daily_costs if daily_costs > 0 else float('inf')
        
        # Financial health score (0-100)
        if days_of_runway >= 30:
            health_score = 100
        elif days_of_runway >= 14:
            health_score = 80 + (days_of_runway - 14) * 20 / 16
        elif days_of_runway >= 7:
            health_score = 50 + (days_of_runway - 7) * 30 / 7
        else:
            health_score = max(0, days_of_runway * 50 / 7)
        
        return {
            'cash': cash,
            'daily_costs': daily_costs,
            'days_of_runway': round(days_of_runway, 1),
            'health_score': round(health_score, 1),
            'status': EconomicSystem._get_financial_status(health_score)
        }
    
    @staticmethod
    def _get_financial_status(health_score):
        """Get financial status description"""
        if health_score >= 80:
            return "Excellent"
        elif health_score >= 60:
            return "Good"
        elif health_score >= 40:
            return "Fair"
        elif health_score >= 20:
            return "Poor"
        else:
            return "Critical"
    
    @staticmethod
    def calculate_hiring_cost(employee_type, current_count):
        """Calculate cost to hire new employee"""
        base_costs = {
            'developer': 800,
            'designer': 600,
            'analyst': 650,
            'manager': 1200,
            'sales': 550,
            'general': 500
        }
        
        base_cost = base_costs.get(employee_type, 500)
        
        # Increase cost based on current employee count (market scarcity)
        scarcity_multiplier = 1 + (current_count * 0.1)
        
        return int(base_cost * scarcity_multiplier)
    
    @staticmethod
    def calculate_training_cost(current_efficiency):
        """Calculate cost to train employee based on current efficiency"""
        # Higher efficiency = more expensive to improve further
        base_cost = 200
        efficiency_multiplier = 1 + (current_efficiency / 100)
        
        return int(base_cost * efficiency_multiplier)
