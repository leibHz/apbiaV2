/**
 * APBIA - Autenticação (CORRIGIDO)
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔐 Módulo de autenticação carregado');
    
    // Verifica se já está autenticado
    if (isAuthenticated()) {
        console.log('✅ Usuário já autenticado, redirecionando...');
        window.location.href = 'projetos.html';
        return;
    }
    
    // Inicializa form de login
    initLoginForm();
    initPasswordToggle();
    initBPField();
});

/**
 * Inicializa formulário de login
 */
function initLoginForm() {
    const form = document.getElementById('loginForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Limpa erros anteriores
        clearFieldErrors();
        hideMessage('errorMessage');
        hideMessage('successMessage');
        
        // Obtém valores
        const email = document.getElementById('email').value.trim();
        const senha = document.getElementById('senha').value;
        const bp = document.getElementById('bp').value.trim().toUpperCase();
        const isOrientadorCheckbox = document.getElementById('isOrientador').checked;
        
        // Validações
        if (!validateEmail(email)) {
            showFieldError('email', 'Email inválido');
            return;
        }
        
        if (!senha || senha.length < 6) {
            showFieldError('senha', 'Senha muito curta');
            return;
        }
        
        // Se não é orientador, valida BP
        if (!isOrientadorCheckbox) {
            if (!bp) {
                showFieldError('bp', 'BP é obrigatório para participantes');
                return;
            }
            
            if (!validateBP(bp)) {
                showFieldError('bp', 'BP inválido. Formato: BRG12345678');
                return;
            }
        }
        
        // Faz login
        await realizarLogin(email, senha, isOrientadorCheckbox ? null : bp);
    });
}

/**
 * Realiza login via API
 */
async function realizarLogin(email, senha, bp) {
    try {
        showLoading('Entrando...');
        
        const data = {
            email: email,
            senha: senha
        };
        
        // Adiciona BP se não for nulo
        if (bp) {
            data.bp = bp;
        }
        
        console.log('📤 Enviando requisição de login...');
        
        const response = await api.login(data);
        
        hideLoading();
        
        if (response.success) {
            console.log('✅ Login bem-sucedido!');
            
            // Salva token e dados do usuário
            saveToken(response.data.token);
            saveUser(response.data);
            
            // Mostra mensagem de sucesso
            showMessage('successMessage', 'Login realizado com sucesso! Redirecionando...');
            
            // Redireciona após 1 segundo
            setTimeout(() => {
                window.location.href = 'projetos.html';
            }, 1000);
            
        } else {
            console.error('❌ Erro no login:', response.message);
            showMessage('errorMessage', response.message || 'Erro ao fazer login');
        }
        
    } catch (error) {
        hideLoading();
        console.error('❌ Erro ao fazer login:', error);
        showMessage('errorMessage', 'Erro ao conectar com o servidor. Tente novamente.');
    }
}

/**
 * Inicializa toggle de senha
 */
function initPasswordToggle() {
    const toggleBtn = document.getElementById('togglePassword');
    const senhaInput = document.getElementById('senha');
    
    if (!toggleBtn || !senhaInput) return;
    
    toggleBtn.addEventListener('click', function() {
        const type = senhaInput.type === 'password' ? 'text' : 'password';
        senhaInput.type = type;
        
        // Troca ícone
        const icon = toggleBtn.querySelector('i');
        if (icon) {
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        }
    });
}

/**
 * Inicializa campo BP (mostra/esconde baseado no checkbox)
 */
function initBPField() {
    const checkbox = document.getElementById('isOrientador');
    const bpField = document.getElementById('bpField');
    const bpInput = document.getElementById('bp');
    
    if (!checkbox || !bpField || !bpInput) return;
    
    checkbox.addEventListener('change', function() {
        if (this.checked) {
            // É orientador - esconde BP
            bpField.style.display = 'none';
            bpInput.value = '';
            bpInput.required = false;
        } else {
            // É participante - mostra BP
            bpField.style.display = 'block';
            bpInput.required = true;
        }
    });
}

/**
 * Mostra mensagem de erro/sucesso
 */
function showMessage(elementId, text) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const textElement = element.querySelector('span');
    if (textElement) {
        textElement.textContent = text;
    }
    
    element.classList.remove('hidden');
    
    // Auto-hide após 5 segundos
    setTimeout(() => {
        hideMessage(elementId);
    }, 5000);
}

/**
 * Esconde mensagem
 */
function hideMessage(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add('hidden');
    }
}

console.log('✅ auth.js carregado e pronto');