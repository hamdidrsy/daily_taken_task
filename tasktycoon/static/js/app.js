// İstatistikler panelini doldur
function fetchAndRenderStats() {
    fetch('/api/dashboard/stats')
        .then(r => r.json())
        .then(data => {
            if (!data.success) {
                document.getElementById('stats-container').innerHTML = '<small class="text-danger">İstatistikler yüklenemedi</small>';
                return;
            }
            renderStats(data);
        })
        .catch(err => {
            console.error('Stats fetch error', err);
            document.getElementById('stats-container').innerHTML = '<small class="text-danger">İstatistikler yüklenemedi</small>';
        });
}

function renderStats(data) {
    const container = document.getElementById('stats-container');
    if (!container) return;
    let html = '';
    // Finansal özet
    if (data.financial_overview) {
        html += `<div><strong>Günlük Net Akış:</strong> <span class='${data.financial_overview.net_daily_flow >= 0 ? 'text-success' : 'text-danger'}'>${data.financial_overview.net_daily_flow} TL</span></div>`;
        html += `<div><strong>Kasa:</strong> ${data.financial_overview.current_cash} TL</div>`;
        html += `<div><strong>Runway:</strong> ${data.financial_overview.runway_days} gün</div>`;
    }
    // Çalışan ve departman
    if (data.employee_stats) {
        html += `<div><strong>Çalışan:</strong> ${data.employee_stats.total_employees} / ${data.employee_stats.max_employees}</div>`;
    }
    if (data.department_stats) {
        const activeDepts = Object.values(data.department_stats).filter(d => d.status === 'active').length;
        html += `<div><strong>Departman:</strong> ${activeDepts} / 4</div>`;
    }
    // Görevler
    if (data.task_performance) {
        html += `<div><strong>Tamamlanan Görev:</strong> ${data.task_performance.completed_tasks}</div>`;
        html += `<div><strong>Başarı Oranı:</strong> %${data.task_performance.success_rate.toFixed(1)}</div>`;
    }
    // Şirket değeri
    if (data.company_valuation) {
        html += `<div><strong>Şirket Değeri:</strong> ${data.company_valuation.total_assets} TL</div>`;
    }
    container.innerHTML = html;
}
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
            // Refresh history panel
            fetchAndRenderHistory(7);
            // Refresh achievements panel
            fetchAndRenderAchievements();
            // Refresh stats panel
            fetchAndRenderStats();
        })
        .catch(error => {
            console.error('Dashboard güncellenirken hata:', error);
            showAlert('Dashboard güncellenirken hata oluştu', 'danger');
        });
}

// Fetch achievements from backend and render into the achievements card
function fetchAndRenderAchievements() {
    fetch('/api/achievements')
        .then(r => r.json())
        .then(data => {
            if (!data.success) {
                document.getElementById('achievements-container').innerHTML = '<small class="text-danger">Başarımlar yüklenemedi</small>';
                return;
            }
            renderAchievements(data.achievements || []);
        })
        .catch(err => {
            console.error('Achievements fetch error', err);
            document.getElementById('achievements-container').innerHTML = '<small class="text-danger">Başarımlar yüklenemedi</small>';
        });
}

function renderAchievements(achievements) {
    const container = document.getElementById('achievements-container');
    if (!container) return;
    if (!achievements || achievements.length === 0) {
        container.innerHTML = '<small class="text-muted">Henüz başarı yok</small>';
        return;
    }
    let html = '<ul class="list-group list-group-flush">';
    achievements.forEach(a => {
        html += `<li class="list-group-item d-flex align-items-center ${a.unlocked ? 'text-success fw-bold' : 'text-muted'}">
            <i class="fas fa-trophy me-2 ${a.unlocked ? 'text-warning' : 'text-secondary'}"></i>
            <span>${a.name}</span>
            <span class="ms-auto small">${a.unlocked ? '✔️' : ''}</span>
            <br><small>${a.desc}</small>
        </li>`;
    });
    html += '</ul>';
    container.innerHTML = html;
}

// Fetch history from backend and render into the history card
function fetchAndRenderHistory(n = 7) {
    fetch(`/api/history?n=${n}`)
        .then(r => r.json())
        .then(data => {
            if (!data.success) {
                document.getElementById('history-container').innerHTML = '<small class="text-danger">Rapor yüklenemedi</small>';
                return;
            }
            renderHistory(data.history || []);
        })
        .catch(err => {
            console.error('History fetch error', err);
            document.getElementById('history-container').innerHTML = '<small class="text-danger">Rapor yüklenemedi</small>';
        });
}

function renderHistory(history) {
    const container = document.getElementById('history-container');
    if (!container) return;

    if (!history || history.length === 0) {
        container.innerHTML = '<small class="text-muted">Henüz günlük özet yok</small>';
        return;
    }

    // Build table
    let html = '<div class="table-responsive"><table class="table table-sm mb-2"><thead><tr><th>Gün</th><th>Başlangıç</th><th>Bitiş</th><th>Net</th></tr></thead><tbody>';
    const values = [];
    history.forEach(h => {
        const day = h.previous_day != null ? h.previous_day : '-';
        const start = typeof h.starting_cash === 'number' ? h.starting_cash : (h.financial_health && h.financial_health.cash ? h.financial_health.cash : 0);
        const end = typeof h.ending_cash === 'number' ? h.ending_cash : start - (h.costs ? h.costs.total_cost : 0);
        const net = (typeof h.net_change === 'number') ? h.net_change : (end - start);
        html += `<tr><td>${day}</td><td>${new Intl.NumberFormat().format(Math.round(start))} TL</td><td>${new Intl.NumberFormat().format(Math.round(end))} TL</td><td>${net >= 0 ? '+' : ''}${new Intl.NumberFormat().format(Math.round(net))} TL</td></tr>`;
        values.push(net);
    });
    html += '</tbody></table></div>';

    // Small sparkline
    const spark = buildSparklineSVG(values, 200, 40);
    html += `<div class="d-flex justify-content-center">${spark}</div>`;

    container.innerHTML = html;
}

// Build a tiny inline SVG sparkline from numeric array
function buildSparklineSVG(values, width = 200, height = 40) {
    if (!values || values.length === 0) return '';
    const max = Math.max(...values);
    const min = Math.min(...values);
    const range = max - min || 1;
    const step = width / Math.max(values.length - 1, 1);
    const points = values.map((v, i) => {
        const x = Math.round(i * step);
        const y = Math.round(height - ((v - min) / range) * height);
        return `${x},${y}`;
    }).join(' ');

    const poly = `<polyline fill="none" stroke="#0d6efd" stroke-width="2" points="${points}"/>`;
    const svg = `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">${poly}</svg>`;
    return svg;
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

// Template uses performTask(...) in onclick handlers, provide a small wrapper
function performTask(taskType) {
    return executeTask(taskType);
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
            // Yeni başarımlar bildirimi
            if (data.day_summary && data.day_summary.new_achievements && data.day_summary.new_achievements.length > 0) {
                data.day_summary.new_achievements.forEach(ach => {
                    showAchievementToast(ach.name, ach.unlocked_at);
                });
                // Paneli güncelle
                fetchAndRenderAchievements();
            }
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
// Başarım toast bildirimi
function showAchievementToast(name, unlockedAt) {
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-bg-success border-0 show position-fixed';
    toast.style.cssText = 'top: 80px; right: 20px; z-index: 9999; min-width: 280px;';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-trophy text-warning me-2"></i>
                <strong>Yeni Başarım!</strong><br>
                <span>${name}</span><br>
                <small>${unlockedAt ? 'Kazanıldı: ' + unlockedAt : ''}</small>
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
        if (toast.parentNode) toast.remove();
    }, 6000);
}
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
        // Oyun sonu varsa büyük kutu ile göster
        if (summary.game_over) {
            html += `<div class="alert alert-danger text-center p-4">
                <h4 class="mb-2">OYUN SONU</h4>
                <div class="mb-2"><strong>${summary.game_over.reason}</strong></div>
                <div class="mb-3">${summary.game_over.desc}</div>
                <button class="btn btn-lg btn-primary" onclick="resetGame()">Yeniden Başlat</button>
            </div>`;
        }
        // Mini event varsa öne çıkar
        if (summary.mini_event) {
            html += `<div class="alert alert-info d-flex align-items-center"><i class='fas fa-bolt me-2'></i><div><strong>${summary.mini_event.name}</strong><br><span>${summary.mini_event.desc}</span></div></div>`;
        }
        // Eğer bankruptcy_message gibi özel anahtarlar varsa öne çıkar
        if (summary.bankruptcy_message) {
            html += `<div class="alert alert-danger">${summary.bankruptcy_message}</div>`;
        }
        for (const [key, value] of Object.entries(summary)) {
            if (key === 'bankruptcy_message' || key === 'mini_event' || key === 'game_over') continue;
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
    fetch('/api/reset_all', {
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
