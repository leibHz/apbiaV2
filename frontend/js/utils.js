/**
 * Funções Utilitárias APBIA
 */

/**
 * Formata data para exibição
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${day}/${month}/${year} ${hours}:${minutes}`;
}

/**
 * Formata data para exibição curta
 */
function formatDateShort(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    
    return `${day}/${month}/${year}`;
}

/**
 * Formata hora para exibição
 */
function formatTime(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${hours}:${minutes}`;
}

/**
 * Formata tamanho de arquivo
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Trunca texto longo
 */
function truncateText(text, maxLength = 100) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Valida email
 */
function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Valida BP (prontuário)
 */
function validateBP(bp) {
    const regex = /^BRG\d{8}$/;
    return regex.test(bp);
}

/**
 * Valida senha
 */
function validatePassword(password) {
    if (password.length < 8) {
        return { valid: false, message: 'Senha deve ter no mínimo 8 caracteres' };
    }
    
    if (!/[A-Z]/.test(password)) {
        return { valid: false, message: 'Senha deve conter pelo menos uma letra maiúscula' };
    }
    
    if (!/[a-z]/.test(password)) {
        return { valid: false, message: 'Senha deve conter pelo menos uma letra minúscula' };
    }
    
    if (!/\d/.test(password)) {
        return { valid: false, message: 'Senha deve conter pelo menos um número' };
    }
    
    return { valid: true, message: 'Senha válida' };
}

/**
 * Obtém usuário atual do localStorage
 */
function getCurrentUser() {
    const userData = localStorage.getItem('apbia_user');
    return userData ? JSON.parse(userData) : null;
}

/**
 * Obtém token atual do localStorage
 */
function getToken() {
    return localStorage.getItem('apbia_token');
}

/**
 * Verifica se usuário está autenticado
 */
function isAuthenticated() {
    return getToken() !== null && getCurrentUser() !== null;
}

/**
 * Verifica se usuário é admin
 */
function isAdmin() {
    const user = getCurrentUser();
    return user && user.tipo_usuario_nome === 'admin';
}

/**
 * Verifica se usuário é orientador
 */
function isOrientador() {
    const user = getCurrentUser();
    return user && user.tipo_usuario_nome === 'orientador';
}

/**
 * Verifica se usuário é participante
 */
function isParticipante() {
    const user = getCurrentUser();
    return user && user.tipo_usuario_nome === 'participante';
}

/**
 * Redireciona para login se não autenticado
 */
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

/**
 * Mostra toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
    // Remove toast existente
    const existingToast = document.getElementById('toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Cria novo toast
    const toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = `fixed top-4 right-4 px-6 py-4 rounded-lg shadow-lg z-50 animate-slide-in`;
    
    // Define cor baseada no tipo
    const colors = {
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        warning: 'bg-yellow-500 text-white',
        info: 'bg-blue-500 text-white'
    };
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    toast.className += ` ${colors[type] || colors.info}`;
    toast.innerHTML = `
        <i class="fas ${icons[type] || icons.info} mr-2"></i>
        ${message}
    `;
    
    document.body.appendChild(toast);
    
    // Remove após duração
    setTimeout(() => {
        toast.style.animation = 'slide-out 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Copia texto para clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copiado para área de transferência!', 'success');
        return true;
    } catch (error) {
        console.error('Erro ao copiar:', error);
        showToast('Erro ao copiar texto', 'error');
        return false;
    }
}

/**
 * Debounce para funções
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Escapa HTML para prevenir XSS
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Converte markdown simples para HTML
 */
function markdownToHtml(text) {
    if (!text) return '';
    
    // Escapa HTML primeiro
    text = escapeHtml(text);
    
    // Negrito
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Itálico
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Links
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-blue-600 hover:underline" target="_blank">$1</a>');
    
    // Quebras de linha
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

/**
 * Gera cor aleatória para avatar
 */
function getRandomColor() {
    const colors = [
        '#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#6366F1', 
        '#8B5CF6', '#EC4899', '#14B8A6', '#F97316', '#06B6D4'
    ];
    return colors[Math.floor(Math.random() * colors.length)];
}

/**
 * Gera iniciais do nome
 */
function getInitials(name) {
    if (!name) return '?';
    
    const parts = name.trim().split(' ');
    if (parts.length === 1) {
        return parts[0].substring(0, 2).toUpperCase();
    }
    
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

/**
 * Adiciona CSS de animações
 */
function addAnimationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slide-in {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slide-out {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .animate-slide-in {
            animation: slide-in 0.3s ease-out;
        }
    `;
    document.head.appendChild(style);
}

// Adiciona estilos de animação ao carregar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addAnimationStyles);
} else {
    addAnimationStyles();
}

// Exporta funções globalmente
window.formatDate = formatDate;
window.formatDateShort = formatDateShort;
window.formatTime = formatTime;
window.formatFileSize = formatFileSize;
window.truncateText = truncateText;
window.validateEmail = validateEmail;
window.validateBP = validateBP;
window.validatePassword = validatePassword;
window.getCurrentUser = getCurrentUser;
window.getToken = getToken;
window.isAuthenticated = isAuthenticated;
window.isAdmin = isAdmin;
window.isOrientador = isOrientador;
window.isParticipante = isParticipante;
window.requireAuth = requireAuth;
window.showToast = showToast;
window.copyToClipboard = copyToClipboard;
window.debounce = debounce;
window.escapeHtml = escapeHtml;
window.markdownToHtml = markdownToHtml;
window.getRandomColor = getRandomColor;
window.getInitials = getInitials;