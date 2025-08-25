from flask import Blueprint, render_template
from ..services.state_service import load_state

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    state = load_state()
    return render_template('dashboard.html', state=state)

@home_bp.route('/api-docs')
def api_docs():
    return '''
    <h1>TaskTycoon - API Documentation</h1>
    <p>API Endpointleri:</p>
    <ul>
        <li>GET /api/state - Şirket durumunu görüntüle</li>
        <li>POST /api/task - Görev yap</li>
        <li>POST /api/day/end - Günü bitir</li>
        <li>POST /api/department/unlock - Departman aç</li>
        <li>POST /api/department/levelup - Departman seviye artır</li>
        <li>POST /api/save - Manuel olarak kaydet</li>
        <li>GET /api/load - Manuel olarak yükle</li>
        <li>POST /api/reset - State'i sıfırla</li>
        <li>GET /api/employees - Çalışanları listele</li>
        <li>POST /api/employees - Çalışan ekle</li>
        <li>DELETE /api/employees/&lt;id&gt; - Çalışan çıkar</li>
    </ul>
    <p>Örnek kullanım:</p>
    <pre>curl http://127.0.0.1:5000/api/state</pre>
    '''
