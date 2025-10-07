/**
 * APBIA - Funções Utilitárias (CORRIGIDO)
 * Inclui correção da função de logout
 */

// ==================== AUTENTICAÇÃO E STORAGE ====================

/**
 * Salva token no localStorage
 */
function saveToken(token) {
    localStorage.setItem('apbia_token', token);
}

/**
 * Obtém token do localStorage
 */
function getToken() {
    return localStorage.getItem('apbia_token');
}

/**
 * Remove token do localStorage
 */
function removeToken() {
    localStorage.removeItem('apbia_token');
}

/**
 * Salva dados do usuário no localStorage
 */
function saveUser(userData) {
    localStorage.setItem('apbia_user', JSON.stringify(userData));
}

/**
 * Obtém dados do usuário do localStorage
 */
function getCurrentUser() {
    const userStr = localStorage.getItem('apbia_user');
    return userStr ? JSON.parse(userStr) : null;
}

/**
 * Remove dados do usuário do localStorage
 */
function removeUser() {
    localStorage.removeItem('apbia_user');
}

/**
 * Limpa todos os dados do localStorage
 */
function clearStorage() {
    localStorage.removeItem('apbia_token');
    localStorage.removeItem('apbia_user');
    // Mantém preferências se existirem
    // localStorage.clear(); // Use isso para limpar TUDO
}

/**
 * CORRIGIDO: Função de logout
 */
function logout() {
    try {
        console.log('🚪 Realizando logout...');
        
        // Limpa dados do localStorage
        clearStorage();
        
        // Redireciona para página de login
        window.location.href = '/public/index.html';
        
        console.log('✅ Logout realizado com sucesso');
    } catch (error) {
        console.error('❌ Erro ao fazer logout:', error);
        // Mesmo com erro, redireciona para login
        window.location.href = '/public/index.html';
    }
}

/**
 * Verifica se usuário está autenticado
 */
function isAuthenticated() {
    const token = getToken();
    return token !== null && token !== undefined && token !== '';
}

/**
 * Middleware: Requer autenticação
 * Redireciona para login se não autenticado
 */
function requireAuth() {
    if (!isAuthenticated()) {
        console.warn('⚠️  Usuário não autenticado. Redirecionando...');
        window.location.href = '/public/index.html';
        return false;
    }
    return true;
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

// ==================== FORMATAÇÃO ====================

/**
 * Formata data para formato brasileiro
 */
function formatDate(dateString) {
    if (!dateString) return '-';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return dateString;
    }
}

/**
 * Formata data (apenas dia/mês/ano)
 */
function formatDateShort(dateString) {
    if (!dateString) return '-';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    } catch (error) {
        return dateString;
    }
}

/**
 * Formata data relativa (há X horas/dias)
 */
function formatRelativeDate(dateString) {
    if (!dateString) return '-';
    
    try {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) return `há ${days} dia(s)`;
        if (hours > 0) return `há ${hours} hora(s)`;
        if (minutes > 0) return `há ${minutes} minuto(s)`;
        return 'agora mesmo';
    } catch (error) {
        return dateString;
    }
}

/**
 * Obtém iniciais do nome
 */
function getInitials(name) {
    if (!name) return '?';
    
    const parts = name.trim().split(' ');
    if (parts.length === 1) {
        return parts[0].charAt(0).toUpperCase();
    }
    
    return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

/**
 * Gera cor aleatória para avatar
 */
function getRandomColor() {
    const colors = [
        '#3b82f6', // blue
        '#10b981', // green
        '#8b5cf6', // purple
        '#f59e0b', // yellow
        '#ef4444', // red
        '#06b6d4', // cyan
        '#ec4899', // pink
        '#14b8a6'  // teal
    ];
    
    return colors[Math.floor(Math.random() * colors.length)];
}

/**
 * Trunca texto longo
 */
function truncateText(text, maxLength = 100) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// ==================== VALIDAÇÃO ====================

/**
 * Valida email
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Valida BP (prontuário)
 * Formato: BRGxxxxxxxx (BRG + 8 dígitos)
 */
function validateBP(bp) {
    if (!bp) return false;
    const re = /^BRG\d{8}$/i;
    return re.test(bp);
}

/**
 * Valida senha
 * Mínimo 8 caracteres, 1 maiúscula, 1 minúscula, 1 número
 */
function validatePassword(password) {
    if (password.length < 8) {
        return {
            valid: false,
            message: 'Senha deve ter no mínimo 8 caracteres'
        };
    }
    
    if (!/[A-Z]/.test(password)) {
        return {
            valid: false,
            message: 'Senha deve conter pelo menos uma letra maiúscula'
        };
    }
    
    if (!/[a-z]/.test(password)) {
        return {
            valid: false,
            message: 'Senha deve conter pelo menos uma letra minúscula'
        };
    }
    
    if (!/\d/.test(password)) {
        return {
            valid: false,
            message: 'Senha deve conter pelo menos um número'
        };
    }
    
    return {
        valid: true,
        message: 'Senha válida'
    };
}

// ==================== UI / FEEDBACK ====================

/**
 * Mostra toast de notificação
 */
function showToast(message, type = 'info') {
    // Remove toast anterior se existir
    const existingToast = document.getElementById('apbia-toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Define cores por tipo
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    };
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    // Cria elemento do toast
    const toast = document.createElement('div');
    toast.id = 'apbia-toast';
    toast.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-4 rounded-lg shadow-lg z-50 flex items-center gap-3 animate-fade-in-down`;
    toast.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    // Remove após 5 segundos
    setTimeout(() => {
        toast.classList.add('animate-fade-out-up');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

/**
 * Mostra loading overlay
 */
function showLoading(message = 'Carregando...') {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('hidden');
        const text = overlay.querySelector('p');
        if (text) text.textContent = message;
    }
}

/**
 * Esconde loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

/**
 * Mostra erro em campo de formulário
 */
function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    // Adiciona classe de erro
    field.classList.add('border-red-500');
    
    // Remove mensagem anterior se existir
    const existingError = field.parentElement.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Adiciona mensagem de erro
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error text-red-500 text-sm mt-1';
    errorDiv.textContent = message;
    field.parentElement.appendChild(errorDiv);
}

/**
 * Limpa erros de campo
 */
function clearFieldErrors() {
    document.querySelectorAll('.border-red-500').forEach(el => {
        el.classList.remove('border-red-500');
    });
    
    document.querySelectorAll('.field-error').forEach(el => {
        el.remove();
    });
}

/**
 * Confirma ação com modal
 */
function confirmAction(message, onConfirm) {
    if (confirm(message)) {
        onConfirm();
    }
}

// ==================== UTILITÁRIOS ====================

/**
 * Debounce function
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
 * Download de texto como arquivo
 */
function downloadTextAsFile(text, filename) {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

/**
 * Formata número com separador de milhares
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

/**
 * Gera ID único
 */
function generateUniqueId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

/**
 * Sanitiza HTML para prevenir XSS
 */
function sanitizeHTML(str) {
    const temp = document.createElement('div');
    temp.textContent = str;
    return temp.innerHTML;
}

/**
 * Escapa caracteres especiais de regex
 */
function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function validatePassword(password) {
    if (password.length < 8) {
        return {
            valid: false,
            message: 'Senha deve ter no mínimo 8 caracteres'
        };
    }
}

/**
 * Verifica se está em modo mobile
 */
function isMobile() {
    return window.innerWidth <= 768;
}

/**
 * Scroll suave para elemento
 */
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// ==================== ANIMAÇÕES CSS ====================

// Adiciona estilos de animação dinamicamente
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeOutUp {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-20px);
        }
    }
    
    .animate-fade-in-down {
        animation: fadeInDown 0.3s ease-out;
    }
    
    .animate-fade-out-up {
        animation: fadeOutUp 0.3s ease-out;
    }
`;
document.head.appendChild(style);

// ==================== EXPORTAÇÕES GLOBAIS ====================

// Torna funções disponíveis globalmente
window.saveToken = saveToken;
window.getToken = getToken;
window.removeToken = removeToken;
window.saveUser = saveUser;
window.getCurrentUser = getCurrentUser;
window.removeUser = removeUser;
window.clearStorage = clearStorage;
window.logout = logout;
window.isAuthenticated = isAuthenticated;
window.requireAuth = requireAuth;
window.isAdmin = isAdmin;
window.isOrientador = isOrientador;
window.isParticipante = isParticipante;
window.formatDate = formatDate;
window.formatDateShort = formatDateShort;
window.formatRelativeDate = formatRelativeDate;
window.getInitials = getInitials;
window.getRandomColor = getRandomColor;
window.truncateText = truncateText;
window.validateEmail = validateEmail;
window.validateBP = validateBP;
window.validatePassword = validatePassword;
window.showToast = showToast;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.showFieldError = showFieldError;
window.clearFieldErrors = clearFieldErrors;
window.confirmAction = confirmAction;
window.debounce = debounce;
window.copyToClipboard = copyToClipboard;
window.downloadTextAsFile = downloadTextAsFile;
window.formatNumber = formatNumber;
window.generateUniqueId = generateUniqueId;
window.sanitizeHTML = sanitizeHTML;
window.escapeRegex = escapeRegex;
window.isMobile = isMobile;
window.smoothScrollTo = smoothScrollTo;

console.log('✅ APBIA Utils carregado (CORRIGIDO)');