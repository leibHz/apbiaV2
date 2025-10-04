/**
 * Sistema de Autenticação APBIA
 */

// Configuração
const API_URL = 'http://localhost:5000/api';

// Elementos DOM
let loginForm, emailInput, senhaInput, bpInput, bpField, isOrientadorCheckbox;
let errorMessage, errorText, successMessage, successText;
let loginBtn, loadingOverlay, togglePassword;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    initElements();
    initEventListeners();
    checkExistingAuth();
});

/**
 * Inicializa elementos DOM
 */
function initElements() {
    loginForm = document.getElementById('loginForm');
    emailInput = document.getElementById('email');
    senhaInput = document.getElementById('senha');
    bpInput = document.getElementById('bp');
    bpField = document.getElementById('bpField');
    isOrientadorCheckbox = document.getElementById('isOrientador');
    errorMessage = document.getElementById('errorMessage');
    errorText = document.getElementById('errorText');
    successMessage = document.getElementById('successMessage');
    successText = document.getElementById('successText');
    loginBtn = document.getElementById('loginBtn');
    loadingOverlay = document.getElementById('loadingOverlay');
    togglePassword = document.getElementById('togglePassword');
}

/**
 * Inicializa event listeners
 */
function initEventListeners() {
    // Submit do formulário
    loginForm.addEventListener('submit', handleLogin);
    
    // Toggle orientador
    isOrientadorCheckbox.addEventListener('change', function() {
        if (this.checked) {
            bpField.style.display = 'none';
            bpInput.required = false;
            bpInput.value = '';
        } else {
            bpField.style.display = 'block';
            bpInput.required = false; // Não obrigatório pois admin também não precisa
        }
    });
    
    // Toggle senha
    togglePassword.addEventListener('click', function() {
        const type = senhaInput.type === 'password' ? 'text' : 'password';
        senhaInput.type = type;
        this.querySelector('i').classList.toggle('fa-eye');
        this.querySelector('i').classList.toggle('fa-eye-slash');
    });
    
    // Auto-formatar BP
    bpInput.addEventListener('input', function() {
        this.value = this.value.toUpperCase();
    });
}

/**
 * Verifica se já existe autenticação
 */
function checkExistingAuth() {
    const token = localStorage.getItem('apbia_token');
    const userData = localStorage.getItem('apbia_user');
    
    if (token && userData) {
        // Valida token
        validateToken(token).then(valid => {
            if (valid) {
                const user = JSON.parse(userData);
                redirectUser(user);
            } else {
                // Token inválido, limpa storage
                clearAuth();
            }
        });
    }
}

/**
 * Valida token no servidor
 */
async function validateToken(token) {
    try {
        const response = await fetch(`${API_URL}/auth/validate`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        return response.ok;
    } catch (error) {
        console.error('Erro ao validar token:', error);
        return false;
    }
}

/**
 * Handle do login
 */
async function handleLogin(e) {
    e.preventDefault();
    
    // Esconde mensagens
    hideMessages();
    
    // Validação básica
    const email = emailInput.value.trim();
    const senha = senhaInput.value;
    const bp = !isOrientadorCheckbox.checked ? bpInput.value.trim() : null;
    
    if (!email || !senha) {
        showError('Por favor, preencha todos os campos obrigatórios');
        return;
    }
    
    // Valida formato do BP se fornecido
    if (bp && !validateBP(bp)) {
        showError('BP inválido. Use o formato: BRG12345678');
        return;
    }
    
    // Mostra loading
    showLoading(true);
    setButtonLoading(true);
    
    try {
        // Prepara dados
        const loginData = {
            email: email,
            senha: senha
        };
        
        if (bp) {
            loginData.bp = bp;
        }
        
        // Faz requisição
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(loginData)
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Login bem-sucedido
            const userData = data.data;
            
            // Salva no localStorage
            localStorage.setItem('apbia_token', userData.token);
            localStorage.setItem('apbia_user', JSON.stringify(userData));
            
            // Mostra sucesso
            showSuccess('Login realizado com sucesso! Redirecionando...');
            
            // Redireciona após 1 segundo
            setTimeout(() => {
                redirectUser(userData);
            }, 1000);
            
        } else {
            // Erro no login
            showError(data.message || 'Erro ao fazer login. Verifique suas credenciais.');
        }
        
    } catch (error) {
        console.error('Erro ao fazer login:', error);
        showError('Erro de conexão com o servidor. Tente novamente.');
    } finally {
        showLoading(false);
        setButtonLoading(false);
    }
}

/**
 * Valida formato do BP
 */
function validateBP(bp) {
    const regex = /^BRG\d{8}$/;
    return regex.test(bp);
}

/**
 * Redireciona usuário baseado no tipo
 */
function redirectUser(userData) {
    const tipoUsuario = userData.tipo_usuario_nome;
    
    switch(tipoUsuario) {
        case 'admin':
            window.location.href = 'admin.html';
            break;
        case 'orientador':
            window.location.href = 'projetos.html';
            break;
        case 'participante':
            window.location.href = 'projetos.html';
            break;
        default:
            window.location.href = 'projetos.html';
    }
}

/**
 * Limpa autenticação
 */
function clearAuth() {
    localStorage.removeItem('apbia_token');
    localStorage.removeItem('apbia_user');
}

/**
 * Mostra mensagem de erro
 */
function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
    successMessage.classList.add('hidden');
    
    // Auto-hide após 5 segundos
    setTimeout(() => {
        errorMessage.classList.add('hidden');
    }, 5000);
}

/**
 * Mostra mensagem de sucesso
 */
function showSuccess(message) {
    successText.textContent = message;
    successMessage.classList.remove('hidden');
    errorMessage.classList.add('hidden');
}

/**
 * Esconde todas as mensagens
 */
function hideMessages() {
    errorMessage.classList.add('hidden');
    successMessage.classList.add('hidden');
}

/**
 * Mostra/esconde loading overlay
 */
function showLoading(show) {
    if (show) {
        loadingOverlay.classList.remove('hidden');
    } else {
        loadingOverlay.classList.add('hidden');
    }
}

/**
 * Altera estado do botão de login
 */
function setButtonLoading(loading) {
    if (loading) {
        loginBtn.disabled = true;
        loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Entrando...';
    } else {
        loginBtn.disabled = false;
        loginBtn.innerHTML = '<i class="fas fa-sign-in-alt mr-2"></i>Entrar';
    }
}

/**
 * Função para logout (usada em outras páginas)
 */
function logout() {
    clearAuth();
    window.location.href = 'index.html';
}

// Exporta funções globais
window.logout = logout;
window.clearAuth = clearAuth;