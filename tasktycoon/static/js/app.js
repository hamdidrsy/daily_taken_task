// TaskTycoon Dashboard JavaScript
// Departman kodunu kullanıcıya okunabilir şekilde çeviren yardımcı fonksiyon
function getDepartmentDisplayName(deptKey) {
    const map = {
        'engLevel': 'Mühendislik',
        'rndLevel': 'Ar-Ge',
        'hrLevel': 'İK',
        'salesLevel': 'Satış'
    };
    return map[deptKey] || deptKey;
}
console.log('TaskTycoon JavaScript başarıyla yüklendi!');

let gameState = null;

// State update functions
function animateValue(id, start, end, duration, formatter) {
    const obj = document.getElementById(id);
    if (!obj) return;
    const range = end - start;
    let startTime = null;
    function step(timestamp) {
        if (!startTime) startTime = timestamp;
        const progress = Math.min((timestamp - startTime) / duration, 1);
        const value = Math.floor(start + range * progress);
        obj.textContent = formatter ? formatter(value) : value;
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.textContent = formatter ? formatter(end) : end;
        }
    }
    window.requestAnimationFrame(step);
}

let lastCash = null;
let lastResearch = null;

function updateDashboard() {
    fetch('/api/state')
        .then(response => response.json())
        .then(state => {
            gameState = state;
            // Animasyonlu para ve araştırma
            const cashVal = typeof state.cash === 'number' ? state.cash : 0;
            const researchVal = typeof state.research === 'number' ? state.research : 0;
            if (lastCash !== null && lastCash !== cashVal) {
                animateValue('cash', lastCash, cashVal, 700, v => new Intl.NumberFormat().format(v));
            } else {
                document.getElementById('cash').textContent = new Intl.NumberFormat().format(cashVal);
            }
            if (lastResearch !== null && lastResearch !== researchVal) {
                animateValue('research', lastResearch, researchVal, 700);
            } else {
                document.getElementById('research').textContent = researchVal;
            }
            lastCash = cashVal;
            lastResearch = researchVal;
            document.getElementById('energy').textContent = state.energy;
            document.getElementById('current-day').textContent = state.current_day || state.day;
            // Update progress bars
            const energyBar = document.getElementById('energy-bar');
            if (energyBar) {
                const energyPercent = (state.energy / 100) * 100;
                energyBar.style.width = energyPercent + '%';
                energyBar.setAttribute('aria-valuenow', state.energy);
                energyBar.textContent = state.energy + '/100';
            }
            // Update departments
            updateDepartmentsDisplay();
            // Update employees
            updateEmployeesDisplay();
            // Tooltipleri yeniden başlat
            if (window.bootstrap) {
                setTimeout(() => {
                    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
                        new bootstrap.Tooltip(tooltipTriggerEl);
                    });
                }, 200);
            }
        })
        .catch(error => {
            console.error('Dashboard güncellenirken hata:', error);
            showAlert('Dashboard güncellenirken hata oluştu', 'danger');
        });
}

function updateDepartmentsDisplay() {
    if (!gameState || !gameState.departments) return;
    
    const container = document.getElementById('departments-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    for (const [deptName, deptInfo] of Object.entries(gameState.departments)) {
        const col = document.createElement('div');
        col.className = 'col-md-6 mb-3';
        const displayName = getDepartmentDisplayName(deptName);
        const level = (typeof deptInfo === 'object') ? (deptInfo.level || 0) : deptInfo;
        const employeeCount = (typeof deptInfo === 'object' && Array.isArray(deptInfo.employees)) ? deptInfo.employees.length : 0;
        col.innerHTML = `
            <div class="card border-secondary">
                <div class="card-body text-center">
                    <h6 class="card-title">${displayName}</h6>
                    <p class="card-text">
                        <small class="text-muted">
                            Seviye: ${level}<br>
                            Çalışan: ${employeeCount}
                        </small>
                    </p>
                    <button class="btn btn-sm btn-outline-primary" onclick="upgradeDepartment('${deptName}')" data-bs-toggle="tooltip" title="Departmanı geliştirerek daha fazla çalışan ve gelir elde edebilirsin!">
                        <i class="fas fa-arrow-up"></i> Geliştir
                    </button>
                </div>
            </div>
        `;
        container.appendChild(col);
    }
}

// Eksik olan showAddDepartmentModal fonksiyonu (doğru yerde)
function showAddDepartmentModal() {
    const modalEl = document.getElementById('addDepartmentModal');
    if (!modalEl) return;
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
}

function updateEmployeesDisplay() {
    if (!gameState || !gameState.employees) return;
    
    const container = document.getElementById('employees-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (gameState.employees.length === 0) {
        container.innerHTML = '<p class="text-muted">Henüz çalışan bulunmuyor</p>';
        return;
    }
    
    gameState.employees.forEach(employee => {
        const div = document.createElement('div');
        div.className = 'mb-2 p-2 border rounded';
        div.innerHTML = `
            <strong>${employee.name}</strong><br>
            <small class="text-muted">
                ${employee.position} - ${employee.department}<br>
                Maaş: ${employee.salary} TL
            </small>
        `;
        container.appendChild(div);
    });
}

// Task functions
function executeTask(taskType) {
    fetch('/api/task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task_type: taskType })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
            updateDashboard();
        } else {
            showAlert(data.message, 'warning');
        }
    })
    .catch(error => {
        console.error('Görev yürütülürken hata:', error);
        showAlert('Görev gerçekleştirilirken hata oluştu', 'danger');
    });
}

// Department functions
function upgradeDepartment(deptType) {
    fetch(`/api/department/${deptType}/upgrade`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
            updateDashboard();
        } else {
            showAlert(data.message, 'warning');
        }
    })
    .catch(error => {
        console.error('Departman yükseltilirken hata:', error);
        showAlert('Departman yükseltilirken hata oluştu', 'danger');
    });
}

// Employee functions
function showHireEmployeeModal() {
    // Update department options
    const select = document.getElementById('empDepartment');
    if (select && gameState && gameState.departments) {
        select.innerHTML = '';
        for (const deptName of Object.keys(gameState.departments)) {
            const option = document.createElement('option');
            option.value = deptName;
            option.textContent = deptName;
            select.appendChild(option);
        }
    }
    
    const modal = new bootstrap.Modal(document.getElementById('hireEmployeeModal'));
    modal.show();
}

function hireEmployee() {
    const name = document.getElementById('empName').value;
    const position = document.getElementById('empPosition').value;
    const department = document.getElementById('empDepartment').value;
    
    if (!name || !position || !department) {
        showAlert('Lütfen tüm alanları doldurun', 'warning');
        return;
    }
    
    fetch('/api/employees/hire', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: name,
            position: position,
            department: department
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
            updateDashboard();
            
            // Close modal and clear form
            const modal = bootstrap.Modal.getInstance(document.getElementById('hireEmployeeModal'));
            modal.hide();
            document.getElementById('empName').value = '';
            document.getElementById('empPosition').value = '';
        } else {
            showAlert(data.message, 'warning');
        }
    })
    .catch(error => {
        console.error('Çalışan işe alınırken hata:', error);
        showAlert('Çalışan işe alınırken hata oluştu', 'danger');
    });
}

// Day management functions
function restoreEnergy() {
    fetch('/api/energy/restore', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
            updateDashboard();
        } else {
            showAlert(data.message, 'warning');
        }
    })
    .catch(error => {
        console.error('Enerji yenilenirken hata:', error);
        showAlert('Enerji yenilenirken hata oluştu', 'danger');
    });
}

function endDay() {
    if (!confirm('Günü bitirmek istediğinizden emin misiniz?')) {
        return;
    }
    fetch('/api/day/end', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateDashboard();
            // Gün sonu özet modalı göster
            showDaySummaryModal(data.day_summary || data.summary || data.message);
        } else {
            showAlert(data.message, 'warning');
        }
    })
    .catch(error => {
        console.error('Gün bitirilirken hata:', error);
        showAlert('Gün bitirilirken hata oluştu', 'danger');
    });
}
// Gün sonu özet modalı (gelişmiş, iç içe nesneleri destekler)
function showDaySummaryModal(summary) {
    const modalEl = document.getElementById('daySummaryModal');
    const contentEl = document.getElementById('day-summary-content');
    if (!modalEl || !contentEl) return;

    function renderValue(value) {
        if (value === null || value === undefined) return '<span class="text-muted">-</span>';
        if (typeof value === 'object') {
            if (Array.isArray(value)) {
                return `<ul>${value.map(v => `<li>${renderValue(v)}</li>`).join('')}</ul>`;
            } else {
                // İç içe nesne
                return `<ul class="list-group mb-2">${Object.entries(value).map(([k, v]) => `<li class="list-group-item d-flex justify-content-between align-items-center"><span>${k}</span><span>${renderValue(v)}</span></li>`).join('')}</ul>`;
            }
        }
        return String(value);
    }

    if (typeof summary === 'object' && summary !== null) {
        let html = '';
        // Eğer bankruptcy_message gibi özel anahtarlar varsa öne çıkar
        if (summary.bankruptcy_message) {
            html += `<div class="alert alert-danger">${summary.bankruptcy_message}</div>`;
        }
        for (const [key, value] of Object.entries(summary)) {
            if (key === 'bankruptcy_message') continue;
            html += `<div class="mb-2"><strong>${key.replace(/_/g, ' ').toUpperCase()}:</strong> ${renderValue(value)}</div>`;
        }
        contentEl.innerHTML = html;
    } else {
        contentEl.textContent = summary;
    }
    const modal = new bootstrap.Modal(modalEl);

    // Eski event listener'ları temizle
    modalEl.removeEventListener('hidden.bs.modal', modalEl._updateDashboardHandler || (()=>{}));
    // Yeni event listener ekle
    modalEl._updateDashboardHandler = function() {
        updateDashboard();
    };
    modalEl.addEventListener('hidden.bs.modal', modalEl._updateDashboardHandler);

    modal.show();
}

// Save/Load functions
function saveGame() {
    fetch('/api/state/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Oyun kaydedildi', 'success');
        } else {
            showAlert('Oyun kaydedilemedi', 'danger');
        }
    })
    .catch(error => {
        console.error('Oyun kaydedilirken hata:', error);
        showAlert('Oyun kaydedilirken hata oluştu', 'danger');
    });
}

function loadGame() {
    if (!confirm('Mevcut oyun durumu kaybolacak. Devam etmek istediğinizden emin misiniz?')) {
        return;
    }
    
    fetch('/api/state/load', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Oyun yüklendi', 'success');
            updateDashboard();
        } else {
            showAlert('Oyun yüklenemedi', 'danger');
        }
    })
    .catch(error => {
        console.error('Oyun yüklenirken hata:', error);
        showAlert('Oyun yüklenirken hata oluştu', 'danger');
    });
}

function resetGame() {
    if (!confirm('Oyunu sıfırlamak istediğinizden emin misiniz? Tüm ilerleme kaybolacak!')) {
        return;
    }
    
    fetch('/api/state/reset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Oyun sıfırlandı', 'info');
            updateDashboard();
        } else {
            showAlert('Oyun sıfırlanamadı', 'danger');
        }
    })
    .catch(error => {
        console.error('Oyun sıfırlanırken hata:', error);
        showAlert('Oyun sıfırlanırken hata oluştu', 'danger');
    });
}

// Utility functions
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to body
    document.body.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing dashboard...');
    updateDashboard();
    
    // Set up auto-refresh every 30 seconds
    setInterval(updateDashboard, 30000);
    
    // Hoş geldiniz mesajı
    setTimeout(() => {
        showAlert('TaskTycoon\'a hoş geldiniz! Şirketinizi büyütmek için görevleri tamamlayın.', 'info');
    }, 1000);
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey) {
        switch(e.key) {
            case 's':
                e.preventDefault();
                saveGame();
                break;
            case 'l':
                e.preventDefault();
                loadGame();
                break;
            case 'e':
                e.preventDefault();
                endDay();
                break;
        }
    }
});

// Auto-save every 5 minutes
setInterval(() => {
    console.log('Auto-saving game...');
    saveGame();
}, 5 * 60 * 1000);
