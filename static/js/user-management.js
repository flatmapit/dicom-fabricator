// User Management JavaScript
let users = [];
let currentUserId = null;

// Role permission mappings
const rolePermissions = {
    'admin': ['system_admin'],
    'operator': ['dicom_generate', 'dicom_view', 'dicom_export', 'pacs_query_test', 'pacs_move_test', 'pacs_configure_test', 'pacs_test_test', 'pacs_query_prod', 'pacs_move_prod', 'pacs_configure_prod', 'pacs_test_prod', 'patients_view', 'patients_create', 'patients_edit'],
    'viewer': ['dicom_view', 'pacs_query_test', 'pacs_query_prod', 'patients_view'],
    'pacs_admin': ['pacs_query_test', 'pacs_move_test', 'pacs_configure_test', 'pacs_test_test', 'pacs_query_prod', 'pacs_move_prod', 'pacs_configure_prod', 'pacs_test_prod', 'system_config'],
    'patient_manager': ['patients_view', 'patients_create', 'patients_edit', 'patients_delete', 'dicom_view'],
    'test_user': ['dicom_view', 'pacs_query_test', 'pacs_move_test', 'patients_view'],
    'test_viewer': ['dicom_view', 'pacs_query_test', 'patients_view'],
    'prod_user': ['dicom_view', 'pacs_query_prod', 'pacs_move_prod', 'patients_view'],
    'prod_viewer': ['dicom_view', 'pacs_query_prod', 'patients_view'],
    'user': []
};

// Load users on page load
document.addEventListener('DOMContentLoaded', function() {
    loadUsers();
    
    // Add event listeners
    document.getElementById('userSearch').addEventListener('input', searchUsers);
});

function loadUsers() {
    fetch('/api/users')
        .then(response => response.json())
        .then(data => {
            users = data.users;
            displayUsers(users);
            updateStatistics();
        })
        .catch(error => {
            console.error('Error loading users:', error);
            showAlert('Error loading users', 'danger');
        });
}

function displayUsers(userList) {
    const tbody = document.getElementById('usersTableBody');
    tbody.innerHTML = '';
    
    userList.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${user.username}</strong></td>
            <td>${user.email || '-'}</td>
            <td><span class="badge bg-${getRoleBadgeColor(user.role)} role-badge">${user.role}</span></td>
            <td>
                ${user.permissions.slice(0, 3).map(p => `<span class="badge bg-secondary permission-badge">${p}</span>`).join('')}
                ${user.permissions.length > 3 ? `<span class="badge bg-info permission-badge">+${user.permissions.length - 3} more</span>` : ''}
            </td>
            <td>${user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}</td>
            <td>${user.last_login ? new Date(user.last_login).toLocaleDateString() : '-'}</td>
            <td class="user-actions">
                <button class="btn btn-sm btn-outline-primary" onclick="editUser('${user.username}')" title="Edit User">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteUser('${user.username}')" title="Delete User" ${user.username === 'admin' ? 'disabled' : ''}>
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updateStatistics() {
    document.getElementById('totalUsers').textContent = users.length;
    document.getElementById('activeUsers').textContent = users.filter(u => u.last_login).length;
    document.getElementById('adminUsers').textContent = users.filter(u => u.role === 'admin').length;
    document.getElementById('regularUsers').textContent = users.filter(u => u.role !== 'admin').length;
}

function getRoleBadgeColor(role) {
    const colors = {
        'admin': 'danger',
        'operator': 'primary',
        'viewer': 'info',
        'pacs_admin': 'warning',
        'patient_manager': 'success',
        'test_user': 'secondary',
        'test_viewer': 'light',
        'prod_user': 'dark',
        'prod_viewer': 'secondary',
        'user': 'outline-secondary'
    };
    return colors[role] || 'secondary';
}

function searchUsers() {
    const searchTerm = document.getElementById('userSearch').value.toLowerCase();
    const filteredUsers = users.filter(user => 
        user.username.toLowerCase().includes(searchTerm) ||
        (user.email && user.email.toLowerCase().includes(searchTerm)) ||
        user.role.toLowerCase().includes(searchTerm)
    );
    displayUsers(filteredUsers);
}

function openCreateUserModal() {
    currentUserId = null;
    document.getElementById('userModalLabel').textContent = 'Add User';
    document.getElementById('userForm').reset();
    document.getElementById('userId').value = '';
    document.getElementById('password').required = true;
    document.getElementById('confirmPassword').required = true;
    clearAllPermissions();
    
    const modal = new bootstrap.Modal(document.getElementById('userModal'));
    modal.show();
}

function editUser(username) {
    const user = users.find(u => u.username === username);
    if (!user) return;
    
    currentUserId = username;
    document.getElementById('userModalLabel').textContent = 'Edit User';
    document.getElementById('userId').value = username;
    document.getElementById('username').value = user.username;
    document.getElementById('email').value = user.email || '';
    document.getElementById('role').value = user.role;
    
    // Password fields not required for editing
    document.getElementById('password').required = false;
    document.getElementById('confirmPassword').required = false;
    document.getElementById('password').value = '';
    document.getElementById('confirmPassword').value = '';
    
    clearAllPermissions();
    setPermissions(user.permissions);
    
    const modal = new bootstrap.Modal(document.getElementById('userModal'));
    modal.show();
}

function updatePermissionsByRole() {
    const role = document.getElementById('role').value;
    clearAllPermissions();
    
    if (role && rolePermissions[role]) {
        setPermissions(rolePermissions[role]);
    }
}

function clearAllPermissions() {
    document.querySelectorAll('input[name="permissions"]').forEach(checkbox => {
        checkbox.checked = false;
    });
}

function setPermissions(permissions) {
    permissions.forEach(permission => {
        const checkbox = document.getElementById(permission);
        if (checkbox) {
            checkbox.checked = true;
        }
    });
}

function getSelectedPermissions() {
    const permissions = [];
    document.querySelectorAll('input[name="permissions"]:checked').forEach(checkbox => {
        permissions.push(checkbox.value);
    });
    return permissions;
}

function saveUser() {
    const formData = new FormData(document.getElementById('userForm'));
    const userData = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password'),
        confirmPassword: formData.get('confirmPassword'),
        role: formData.get('role'),
        permissions: getSelectedPermissions()
    };
    
    // Validation
    if (!userData.username || !userData.role) {
        showAlert('Username and role are required', 'danger');
        return;
    }
    
    if (!currentUserId && (!userData.password || userData.password !== userData.confirmPassword)) {
        showAlert('Password and confirmation must match', 'danger');
        return;
    }
    
    const url = currentUserId ? `/api/users/${currentUserId}` : '/api/users';
    const method = currentUserId ? 'PUT' : 'POST';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('userModal')).hide();
            loadUsers();
        } else {
            showAlert(data.message || 'Error saving user', 'danger');
        }
    })
    .catch(error => {
        console.error('Error saving user:', error);
        showAlert('Error saving user', 'danger');
    });
}

function deleteUser(username) {
    if (username === 'admin') {
        showAlert('Cannot delete the admin user', 'warning');
        return;
    }
    
    document.getElementById('deleteUserName').textContent = username;
    currentUserId = username;
    
    const modal = new bootstrap.Modal(document.getElementById('deleteUserModal'));
    modal.show();
}

function confirmDeleteUser() {
    fetch(`/api/users/${currentUserId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('deleteUserModal')).hide();
            loadUsers();
        } else {
            showAlert(data.message || 'Error deleting user', 'danger');
        }
    })
    .catch(error => {
        console.error('Error deleting user:', error);
        showAlert('Error deleting user', 'danger');
    });
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}
