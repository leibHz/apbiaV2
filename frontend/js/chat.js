/**
 * Sistema de Chat APBIA
 */

// Estado global
let currentChatId = null;
let currentProjectId = null;
let mensagemIdParaNota = null;
let isLoadingResponse = false;

// Elementos DOM
let chatMessages, messageForm, messageInput, sendBtn;
let chatTitle, projectName, userName, userAvatar, apiStatus;
let notaModal, notaInput, loadingOverlay;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Verifica autenticação
    if (!requireAuth()) return;

    initElements();
    initEventListeners();
    loadChatFromURL();
    checkAPIStatus();
    updateUserInfo();

    // Atualiza status da API periodicamente
    setInterval(checkAPIStatus, 30000); // 30 segundos
});

/**
 * Inicializa elementos DOM
 */
function initElements() {
    chatMessages = document.getElementById('chatMessages');
    messageForm = document.getElementById('messageForm');
    messageInput = document.getElementById('messageInput');
    sendBtn = document.getElementById('sendBtn');
    chatTitle = document.getElementById('chatTitle');
    projectName = document.getElementById('projectName');
    userName = document.getElementById('userName');
    userAvatar = document.getElementById('userAvatar');
    apiStatus = document.getElementById('apiStatus');
    notaModal = document.getElementById('notaModal');
    notaInput = document.getElementById('notaInput');
    loadingOverlay = document.getElementById('loadingOverlay');
}

/**
 * Inicializa event listeners
 */
function initEventListeners() {
    // Submit do formulário
    messageForm.addEventListener('submit', handleSendMessage);

    // Auto-resize textarea
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });

    // Ctrl+Enter para enviar
    messageInput.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            messageForm.dispatchEvent(new Event('submit'));
        }
    });
}

/**
 * Carrega chat da URL
 */
async function loadChatFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const chatId = urlParams.get('id');

    if (!chatId) {
        showToast('ID do chat não encontrado', 'error');
        setTimeout(() => window.location.href = 'projetos.html', 2000);
        return;
    }

    currentChatId = parseInt(chatId);
    await loadChat();
}

/**
 * Carrega dados do chat
 */
async function loadChat() {
    try {
        showLoading(true);

        const response = await api.buscarChat(currentChatId, true);

        if (response.success) {
            const chat = response.data;
            currentProjectId = chat.projeto_id;

            // Atualiza UI
            chatTitle.textContent = chat.titulo || 'Chat APBIA';
            projectName.textContent = chat.projeto_nome || 'Projeto';

            // Carrega mensagens
            if (chat.mensagens && chat.mensagens.length > 0) {
                displayMessages(chat.mensagens);
            }
        } else {
            showToast('Erro ao carregar chat', 'error');
        }
    } catch (error) {
        console.error('Erro ao carregar chat:', error);
        showToast('Erro ao carregar chat', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Exibe mensagens no chat
 */
function displayMessages(mensagens) {
    // Limpa mensagem de boas-vindas
    chatMessages.innerHTML = '';

    mensagens.forEach(msg => {
        addMessageToChat(msg);
    });

    scrollToBottom();
}

/**
 * Adiciona mensagem ao chat
 */
function addMessageToChat(mensagem) {
    const isIA = mensagem.usuario_id === null;
    const isNota = mensagem.e_nota_orientador;
    const user = getCurrentUser();

    const messageDiv = document.createElement('div');
    messageDiv.className = `message-bubble flex ${isIA ? 'justify-start' : 'justify-end'}`;

    const bubbleClass = isNota 
        ? 'bg-yellow-100 border border-yellow-300'
        : isIA 
            ? 'bg-gray-100' 
            : 'bg-purple-600 text-white';

    const html = `
        <div class="max-w-3xl ${isIA ? 'mr-12' : 'ml-12'}">
            <div class="${bubbleClass} rounded-lg p-4 shadow-sm">
                ${!isIA && !isNota ? `
                    <div class="flex items-center gap-2 mb-2 text-sm opacity-90">
                        <i class="fas fa-user"></i>
                        <span class="font-semibold">${mensagem.usuario_nome || 'Você'}</span>
                    </div>
                ` : ''}
                ${isIA ? `
                    <div class="flex items-center gap-2 mb-2 text-sm text-gray-600">
                        <i class="fas fa-robot"></i>
                        <span class="font-semibold">APBIA</span>
                    </div>
                ` : ''}
                ${isNota ? `
                    <div class="flex items-center gap-2 mb-2 text-sm text-yellow-800">
                        <i class="fas fa-sticky-note"></i>
                        <span class="font-semibold">Nota do Orientador</span>
                    </div>
                ` : ''}
                <div class="prose prose-sm max-w-none ${isIA || isNota ? 'text-gray-800' : 'text-white'}">
                    ${formatMessageContent(mensagem.conteudo)}
                </div>
                <div class="flex items-center justify-between mt-3 pt-2 border-t ${isIA || isNota ? 'border-gray-300' : 'border-white border-opacity-20'}">
                    <span class="text-xs ${isIA || isNota ? 'text-gray-500' : 'text-white text-opacity-70'}">
                        <i class="far fa-clock mr-1"></i>
                        ${formatTime(mensagem.data_envio)}
                    </span>
                    ${isIA && (isOrientador() || isAdmin()) && !isNota ? `
                        <button 
                            onclick="abrirModalNota(${mensagem.id})"
                            class="text-xs text-yellow-600 hover:text-yellow-700 font-medium"
                        >
                            <i class="fas fa-sticky-note mr-1"></i>
                            Adicionar Nota
                        </button>
                    ` : ''}
                </div>
            </div>
        </div>
    `;

    messageDiv.innerHTML = html;
    chatMessages.appendChild(messageDiv);
}

/**
 * Formata conteúdo da mensagem
 */
function formatMessageContent(content) {
    // Converte markdown simples para HTML
    let formatted = markdownToHtml(content);
    
    // Adiciona classes para listas
    formatted = formatted.replace(/<ul>/g, '<ul class="list-disc list-inside ml-4 space-y-1">');
    formatted = formatted.replace(/<ol>/g, '<ol class="list-decimal list-inside ml-4 space-y-1">');
    
    return formatted;
}

/**
 * Handle envio de mensagem
 */
async function handleSendMessage(e) {
    e.preventDefault();

    const content = messageInput.value.trim();
    if (!content || isLoadingResponse) return;

    const useThinking = document.querySelector('input[name="responseMode"]:checked').value === 'thinking';

    // Adiciona mensagem do usuário imediatamente
    const userMessage = {
        usuario_id: getCurrentUser().id,
        usuario_nome: getCurrentUser().nome_completo,
        conteudo: content,
        data_envio: new Date().toISOString(),
        e_nota_orientador: false
    };

    addMessageToChat(userMessage);
    messageInput.value = '';
    messageInput.style.height = 'auto';
    scrollToBottom();

    // Mostra indicador de digitação
    showTypingIndicator();
    setButtonLoading(true);
    isLoadingResponse = true;

    try {
        const response = await api.enviarMensagem(currentChatId, content, useThinking);

        if (response.success) {
            // Remove indicador de digitação
            hideTypingIndicator();

            // Adiciona resposta da IA
            if (response.data.mensagem_ia) {
                addMessageToChat(response.data.mensagem_ia);
            }

            // Atualiza status da API se fornecido
            if (response.data.uso_api) {
                updateAPIStatus(response.data.uso_api);
            }

            scrollToBottom();
        } else {
            showToast(response.message || 'Erro ao enviar mensagem', 'error');
            hideTypingIndicator();
        }
    } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
        showToast('Erro ao enviar mensagem', 'error');
        hideTypingIndicator();
    } finally {
        setButtonLoading(false);
        isLoadingResponse = false;
    }
}

/**
 * Mostra indicador de digitação
 */
function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'typingIndicator';
    indicator.className = 'message-bubble flex justify-start';
    indicator.innerHTML = `
        <div class="max-w-3xl mr-12">
            <div class="bg-gray-100 rounded-lg p-4 shadow-sm">
                <div class="flex items-center gap-2 mb-2 text-sm text-gray-600">
                    <i class="fas fa-robot"></i>
                    <span class="font-semibold">APBIA</span>
                </div>
                <div class="typing-indicator flex gap-1">
                    <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
                    <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
                    <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
                </div>
            </div>
        </div>
    `;
    chatMessages.appendChild(indicator);
    scrollToBottom();
}

/**
 * Remove indicador de digitação
 */
function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

/**
 * Abre modal de nota
 */
function abrirModalNota(mensagemId) {
    mensagemIdParaNota = mensagemId;
    notaInput.value = '';
    notaModal.classList.remove('hidden');
}

/**
 * Fecha modal de nota
 */
function fecharModalNota() {
    notaModal.classList.add('hidden');
    mensagemIdParaNota = null;
}

/**
 * Salva nota do orientador
 */
async function salvarNota() {
    const nota = notaInput.value.trim();

    if (!nota) {
        showToast('Digite uma nota', 'warning');
        return;
    }

    try {
        showLoading(true);

        const response = await api.adicionarNotaOrientador(mensagemIdParaNota, nota);

        if (response.success) {
            showToast('Nota adicionada com sucesso!', 'success');
            fecharModalNota();

            // Adiciona nota ao chat
            if (response.data) {
                addMessageToChat(response.data);
                scrollToBottom();
            }
        } else {
            showToast(response.message || 'Erro ao adicionar nota', 'error');
        }
    } catch (error) {
        console.error('Erro ao adicionar nota:', error);
        showToast('Erro ao adicionar nota', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Verifica status da API
 */
async function checkAPIStatus() {
    try {
        const response = await api.statusAPI();

        if (response.success) {
            updateAPIStatus(response.data);
        }
    } catch (error) {
        console.error('Erro ao verificar status da API:', error);
    }
}

/**
 * Atualiza status da API na UI
 */
function updateAPIStatus(status) {
    if (!status) return;

    const isActive = status.sistema_ativo;
    const isThrottling = status.throttling_ativo;
    const usagePercent = status.uso_percentual || 0;

    let statusClass, statusText, statusIcon;

    if (!isActive) {
        statusClass = 'bg-red-100 text-red-700';
        statusText = 'Offline';
        statusIcon = 'fa-circle';
    } else if (isThrottling || usagePercent >= 80) {
        statusClass = 'bg-yellow-100 text-yellow-700';
        statusText = 'Limitado';
        statusIcon = 'fa-exclamation-circle';
    } else {
        statusClass = 'bg-green-100 text-green-700';
        statusText = 'Online';
        statusIcon = 'fa-circle';
    }

    apiStatus.className = `flex items-center gap-2 px-3 py-1 rounded-full text-sm ${statusClass}`;
    apiStatus.innerHTML = `
        <i class="fas ${statusIcon} text-xs"></i>
        <span>${statusText}</span>
    `;
}

/**
 * Atualiza informações do usuário
 */
function updateUserInfo() {
    const user = getCurrentUser();
    if (user) {
        userName.textContent = user.nome_completo.split(' ')[0];
        userAvatar.textContent = getInitials(user.nome_completo);
        userAvatar.style.backgroundColor = getRandomColor();
    }
}

/**
 * Limpa conversa (apenas visualmente)
 */
function limparChat() {
    if (confirm('Deseja limpar a visualização desta conversa? (As mensagens não serão apagadas do banco de dados)')) {
        chatMessages.innerHTML = `
            <div class="text-center py-8">
                <div class="inline-block p-4 bg-purple-100 rounded-full mb-4">
                    <i class="fas fa-robot text-4xl text-purple-600"></i>
                </div>
                <h2 class="text-xl font-bold text-gray-800 mb-2">Conversa limpa!</h2>
                <p class="text-gray-600">Recarregue a página para ver as mensagens novamente</p>
            </div>
        `;
        showToast('Conversa limpa', 'info');
    }
}

/**
 * Exporta chat
 */
async function exportarChat() {
    try {
        const response = await api.buscarChat(currentChatId, true);

        if (response.success && response.data.mensagens) {
            const chat = response.data;
            let text = `CHAT APBIA - ${chat.titulo}\n`;
            text += `Projeto: ${chat.projeto_nome || 'N/A'}\n`;
            text += `Data: ${formatDate(new Date())}\n`;
            text += `\n${'='.repeat(50)}\n\n`;

            chat.mensagens.forEach(msg => {
                const remetente = msg.usuario_id ? (msg.usuario_nome || 'Usuário') : 'APBIA';
                text += `[${formatDateTime(msg.data_envio)}] ${remetente}:\n`;
                text += `${msg.conteudo}\n\n`;
            });

            // Cria e baixa arquivo
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `chat_${currentChatId}_${Date.now()}.txt`;
            a.click();
            URL.revokeObjectURL(url);

            showToast('Chat exportado com sucesso!', 'success');
        }
    } catch (error) {
        console.error('Erro ao exportar chat:', error);
        showToast('Erro ao exportar chat', 'error');
    }
}

/**
 * Scroll para o final do chat
 */
function scrollToBottom() {
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

/**
 * Mostra/esconde loading
 */
function showLoading(show) {
    if (show) {
        loadingOverlay.classList.remove('hidden');
    } else {
        loadingOverlay.classList.add('hidden');
    }
}

/**
 * Altera estado do botão de enviar
 */
function setButtonLoading(loading) {
    if (loading) {
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    } else {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i><span class="hidden sm:inline">Enviar</span>';
    }
}

// Exporta funções globais
window.abrirModalNota = abrirModalNota;
window.fecharModalNota = fecharModalNota;
window.salvarNota = salvarNota;
window.limparChat = limparChat;
window.exportarChat = exportarChat;