/**
 * Cliente API APBIA
 */

const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Classe para fazer requisições à API
 */
class APIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    /**
     * Obtém headers padrão com autenticação
     */
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (includeAuth) {
            const token = getToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }

        return headers;
    }

    /**
     * Faz requisição GET
     */
    async get(endpoint, includeAuth = true) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'GET',
                headers: this.getHeaders(includeAuth)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Erro na requisição');
            }

            return data;
        } catch (error) {
            console.error('Erro GET:', error);
            throw error;
        }
    }

    /**
     * Faz requisição POST
     */
    async post(endpoint, body = {}, includeAuth = true) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers: this.getHeaders(includeAuth),
                body: JSON.stringify(body)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Erro na requisição');
            }

            return data;
        } catch (error) {
            console.error('Erro POST:', error);
            throw error;
        }
    }

    /**
     * Faz requisição PUT
     */
    async put(endpoint, body = {}, includeAuth = true) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'PUT',
                headers: this.getHeaders(includeAuth),
                body: JSON.stringify(body)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Erro na requisição');
            }

            return data;
        } catch (error) {
            console.error('Erro PUT:', error);
            throw error;
        }
    }

    /**
     * Faz requisição DELETE
     */
    async delete(endpoint, includeAuth = true) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'DELETE',
                headers: this.getHeaders(includeAuth)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Erro na requisição');
            }

            return data;
        } catch (error) {
            console.error('Erro DELETE:', error);
            throw error;
        }
    }

    // ==================== AUTENTICAÇÃO ====================

    async login(email, senha, bp = null) {
        const body = { email, senha };
        if (bp) body.bp = bp;
        return this.post('/auth/login', body, false);
    }

    async validateToken() {
        return this.get('/auth/validate');
    }

    async alterarSenha(senhaAtual, novaSenha) {
        return this.post('/auth/alterar-senha', { senha_atual: senhaAtual, nova_senha: novaSenha });
    }

    // ==================== CHATS ====================

    async criarChat(projetoId, tipoIA = 'gemini', titulo = '') {
        return this.post('/chat/criar', { projeto_id: projetoId, tipo_ia: tipoIA, titulo });
    }

    async buscarChat(chatId, incluirMensagens = true) {
        return this.get(`/chat/${chatId}?incluir_mensagens=${incluirMensagens}`);
    }

    async listarChatsProjeto(projetoId) {
        return this.get(`/chat/projeto/${projetoId}`);
    }

    async listarMensagensChat(chatId, limit = 100) {
        return this.get(`/chat/${chatId}/mensagens?limit=${limit}`);
    }

    async deletarChat(chatId) {
        return this.delete(`/chat/${chatId}`);
    }

    // ==================== IA ====================

    async enviarMensagem(chatId, conteudo, usarThinking = false) {
        return this.post('/ia/mensagem', { 
            chat_id: chatId, 
            conteudo, 
            usar_thinking: usarThinking 
        });
    }

    async adicionarNotaOrientador(mensagemId, nota) {
        return this.post('/ia/nota-orientador', { mensagem_id: mensagemId, nota });
    }

    async statusAPI() {
        return this.get('/ia/status');
    }

    // ==================== PROJETOS ====================

    async listarProjetos() {
        return this.get('/projetos');
    }

    async buscarProjeto(projetoId) {
        return this.get(`/projetos/${projetoId}`);
    }

    // ==================== USUÁRIO ====================

    async meuPerfil() {
        return this.get('/usuario/perfil');
    }

    // ==================== ADMIN ====================

    async cadastrarUsuario(dados) {
        return this.post('/admin/cadastrar-usuario', dados);
    }

    async statusSistema() {
        return this.get('/admin/sistema/status');
    }

    async toggleSistema(ativar, motivo = '') {
        return this.post('/admin/sistema/toggle', { ativar, motivo });
    }

    // ==================== HEALTH ====================

    async healthCheck() {
        return this.get('/health', false);
    }
}

// Instância global
const api = new APIClient();

// Exporta para uso global
window.api = api;
window.APIClient = APIClient;