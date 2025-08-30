// DICOM Fabricator Main JavaScript

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
});

// Utility functions
function formatDate(dateString) {
    if (!dateString) return '-';
    const year = dateString.substring(0, 4);
    const month = dateString.substring(4, 6);
    const day = dateString.substring(6, 8);
    return `${year}-${month}-${day}`;
}

function formatFileSize(bytes) {
    if (!bytes) return '0 KB';
    const kb = bytes / 1024;
    if (kb < 1024) return kb.toFixed(2) + ' KB';
    const mb = kb / 1024;
    return mb.toFixed(2) + ' MB';
}

// API wrapper functions
const API = {
    async get(url) {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    },
    
    async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    },
    
    async delete(url) {
        const response = await fetch(url, {method: 'DELETE'});
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    }
};

// Toast notification system
class Toast {
    static show(message, type = 'info') {
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        const toastElement = document.createElement('div');
        toastElement.innerHTML = toastHtml;
        container.appendChild(toastElement.firstElementChild);
        
        const toast = new bootstrap.Toast(toastElement.firstElementChild);
        toast.show();
        
        setTimeout(() => {
            toastElement.firstElementChild.remove();
        }, 5000);
    }
    
    static success(message) { this.show(message, 'success'); }
    static error(message) { this.show(message, 'danger'); }
    static info(message) { this.show(message, 'info'); }
    static warning(message) { this.show(message, 'warning'); }
}

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Export for use in other scripts
window.DICOMFabricator = {
    API,
    Toast,
    formatDate,
    formatFileSize
};