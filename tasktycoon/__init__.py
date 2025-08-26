from flask import Flask
from .config import DATA_DIR, STATE_PATH
import os

def create_app():
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')

    # Gerekli klasör ve state dosyasını oluştur
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(STATE_PATH):
        from .services.state_service import save_state, get_default_state
        save_state(get_default_state())

    # Blueprint'leri kaydet
    from .routes.home import home_bp
    from .routes.state import state_bp
    from .routes.task import task_bp
    from .routes.day import day_bp
    from .routes.department import department_bp
    from .routes.manage import manage_bp
    from .routes.employees import employees_bp
    from .routes.employee import employee_bp
    from .routes.dashboard import dashboard_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(state_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(day_bp)
    app.register_blueprint(department_bp)
    app.register_blueprint(manage_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(dashboard_bp)

    return app
