// TaskTycoon Dashboard JavaScript
console.log('TaskTycoon JavaScript loaded successfully!');

let gameState = null;

// State update functions
function updateDashboard() {
    fetch('/api/state')
        .then(response => response.json())
        .then(state => {
            gameState = state;
            
            // Update basic stats
            document.getElementById('cash').textContent = new Intl.NumberFormat().format(state.cash);
            document.getElementById('research').textContent = state.research;
            document.getElementById('energy').textContent = state.energy;
            document.getElementById('day').textContent = state.day;
            
            // Update progress bars
            const energyBar = document.getElementById('energyBar');
            const energyPercent = (state.energy / 100) * 100;
            energyBar.style.width = energyPercent + '%';
            energyBar.setAttribute('aria-valuenow', state.energy);
            
            // Update departments
            updateDepartmentsDisplay();
            
            // Update employees
            updateEmployeesDisplay();
        })
        .catch(error => {
            console.error('Error updating dashboard:', error);
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
        
        col.innerHTML = `
            <div class="card border-secondary">
                <div class="card-body text-center">
                    <h6 class="card-title">${deptName}</h6>
                    <p class="card-text">
                        <small class="text-muted">
                            Seviye: ${deptInfo.level || deptInfo}<br>
                            Çalışan: ${deptInfo.employees ? deptInfo.employees.length : 0}
                        </small>
                    </p>
                    <button class="btn btn-sm btn-outline-primary" onclick="upgradeDepartment('${deptName}')">
                        <i class="fas fa-arrow-up"></i> Geliştir
                    </button>
                </div>
            </div>
        `;
        
        container.appendChild(col);
    }
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
        console.error('Error executing task:', error);
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
        console.error('Error upgrading department:', error);
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
        console.error('Error hiring employee:', error);
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
        console.error('Error restoring energy:', error);
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
            showAlert(data.message, 'info');
            updateDashboard();
        } else {
            showAlert(data.message, 'warning');
        }
    })
    .catch(error => {
        console.error('Error ending day:', error);
        showAlert('Gün bitirilirken hata oluştu', 'danger');
    });
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
        console.error('Error saving game:', error);
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
        console.error('Error loading game:', error);
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
        console.error('Error resetting game:', error);
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
    
    // Show welcome message
    setTimeout(() => {
        showAlert('TaskTycoon\'a hoş geldiniz! Şirketinizi büyütmek için görevleri gerçekleştirin.', 'info');
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
