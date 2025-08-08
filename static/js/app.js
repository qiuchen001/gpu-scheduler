// 通用JavaScript功能

// 全局配置
const CONFIG = {
    API_BASE_URL: '',
    REFRESH_INTERVAL: 10000, // 10秒
    TASK_REFRESH_INTERVAL: 5000, // 5秒
};

// 工具函数
const Utils = {
    // 格式化时间
    formatTime: function(timeStr) {
        if (!timeStr) return '-';
        const date = new Date(timeStr);
        return date.toLocaleString('zh-CN');
    },
    
    // 格式化文件大小
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // 格式化GPU内存
    formatGPUMemory: function(bytes) {
        return this.formatFileSize(bytes);
    },
    
    // 显示通知
    showNotification: function(message, type = 'info') {
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';
        
        const alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // 创建通知容器（如果不存在）
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
            document.body.appendChild(container);
        }
        
        // 添加通知
        container.insertAdjacentHTML('beforeend', alertHtml);
        
        // 自动移除通知
        setTimeout(() => {
            const alerts = container.querySelectorAll('.alert');
            if (alerts.length > 0) {
                alerts[0].remove();
            }
        }, 5000);
    },
    
    // 防抖函数
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // 节流函数
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// API请求封装
const API = {
    // 基础请求方法
    request: function(method, url, data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        return fetch(url, options)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            });
    },
    
    // GET请求
    get: function(url) {
        return this.request('GET', url);
    },
    
    // POST请求
    post: function(url, data) {
        return this.request('POST', url, data);
    },
    
    // PUT请求
    put: function(url, data) {
        return this.request('PUT', url, data);
    },
    
    // DELETE请求
    delete: function(url) {
        return this.request('DELETE', url);
    }
};

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 初始化弹出框
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // 添加页面加载动画
    document.body.classList.add('fade-in');
    
    // 初始化导航栏状态
    updateNavbarStatus();
});

// 更新导航栏状态
function updateNavbarStatus() {
    const statusElement = document.getElementById('scheduler-status');
    if (statusElement) {
        // 这里可以根据实际状态更新显示
        // 暂时保持默认状态
    }
}

// 全局错误处理
window.addEventListener('error', function(e) {
    console.error('JavaScript错误:', e.error);
    Utils.showNotification('页面发生错误，请刷新页面重试', 'error');
});

// 网络状态检测
window.addEventListener('online', function() {
    Utils.showNotification('网络连接已恢复', 'success');
});

window.addEventListener('offline', function() {
    Utils.showNotification('网络连接已断开', 'warning');
});

// 导出全局对象
window.Utils = Utils;
window.API = API;
window.CONFIG = CONFIG; 