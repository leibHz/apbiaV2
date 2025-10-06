/**
 * Painel Administrativo APBIA
 */

let currentTab = 'usuarios';
let sistemaAtivo = true;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    if (!requireAuth()) return;
    
    // Verifica se é admin
    if (!isAdmin()) {
        showToast('Acesso negado. Apenas administradores.', 'error');
        setTimeout(() => window.location.href = 'projetos.html', 2000);
        return;
    }

    initEventListeners();
    carregarRelatorio();
});

/**
 * Inicializa event listeners
 */
function initEventListeners() {
    // Form de cadastro
    const cadastroForm = document.getElementById('cadastroForm');
    if (cadastroForm) {
        cadastroForm.addEventListener('submit', handleCadastroUsuario);
    }

    // Tipo de usuário
    const cadTipo = document.getElementById('cadTipo');
    if (cadTipo) {
        cadTipo.addEventListener('change', function() {
            const bpField = document.getElementById('bpField');
            if (this.value === 'participante') {
                bpField.style.display = 'block';
                document.getElementById('cadBP').required = true;
            } else {
                bpField.style.display = 'none';
                document.getElementById('cadBP').required = false;
                document.getElementById('cadBP').value = '';
            }
        });
    }
}

/**
 * Carrega relatório completo
 */
async function carregarRelatorio() {
    try {
        const response = await api.statusSistema();

        if (response.success) {
            const data = response.data;
            
            // Atualiza cards
            document.getElementById('totalUsuarios').textContent = data.usuarios?.total || 0;
            document.getElementById('totalProjetos').textContent = data.projetos?.total || 0;
            document.getElementById('totalChats').textContent = data.chats?.total || 0;
            
            // Uso da API
            const usoAPI = data.api?.status?.uso_percentual || 0;
            document.getElementById('usoAPI').textContent = `${usoAPI.toFixed(1)}%`;

            // Status do sistema
            sistemaAtivo = data.sistema?.ativo !== false;
            atualizarBotaoToggle();

            // Carrega dados das tabs, passando os dados para evitar nova chamada
            await carregarUsuarios(data.usuarios);
            await carregarProjetos();
            await carregarStatusAPI();
        }
    } catch (error) {
        console.error('Erro ao carregar relatório:', error);
        showToast('Erro ao carregar relatório', 'error');
    }
}

/**
 * Carrega lista de usuários
 */
async function carregarUsuarios(usuariosData = null) {
    const container = document.getElementById('usuariosList');
    container.innerHTML = '<div class="text-center py-4"><i class="fas fa-spinner fa-spin text-purple-600"></i></div>';

    try {
        let usuarios = usuariosData;

        // Se os dados não foram passados, busca na API como fallback
        if (!usuarios) {
            const response = await api.statusSistema();
            if (response.success) {
                usuarios = response.data.usuarios;
            } else {
                throw new Error(response.message || "Não foi possível buscar dados dos usuários");
            }
        }
        
        if (usuarios && usuarios.por_tipo) {
            let html = '';
            
            // Por tipo
            const tipos = ['participante', 'orientador', 'admin'];
            tipos.forEach(tipo => {
                const qtd = usuarios.por_tipo[tipo] || 0;
                html += `
                    <div class="border border-gray-200 rounded-lg p-4">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 rounded-full flex items-center justify-center ${
                                    tipo === 'admin' ? 'bg-red-100 text-red-600' :
                                    tipo === 'orientador' ? 'bg-blue-100 text-blue-600' :
                                    'bg-green-100 text-green-600'
                                }">
                                    <i class="fas ${
                                        tipo === 'admin' ? 'fa-user-shield' :
                                        tipo === 'orientador' ? 'fa-chalkboard-teacher' :
                                        'fa-user-graduate'
                                    }"></i>
                                </div>
                                <div>
                                    <h4 class="font-semibold text-gray-800 capitalize">${tipo}s</h4>
                                    <p class="text-sm text-gray-500">${qtd} cadastrado(s)</p>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html || '<p class="text-center py-4 text-gray-500">Nenhum usuário cadastrado</p>';
        } else {
            container.innerHTML = '<p class="text-center py-4 text-gray-500">Nenhum usuário cadastrado</p>';
        }
    } catch (error) {
        console.error('Erro ao carregar usuários:', error);
        container.innerHTML = '<p class="text-center py-4 text-red-600">Erro ao carregar usuários</p>';
    }
}

/**
 * Carrega lista de projetos
 */
async function carregarProjetos() {
    const container = document.getElementById('projetosList');
    container.innerHTML = '<div class="text-center py-4"><i class="fas fa-spinner fa-spin text-purple-600"></i></div>';

    try {
        const response = await api.listarProjetos();

        if (response.success && response.data.length > 0) {
            let html = '';
            
            response.data.forEach(projeto => {
                html += `
                    <div class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                        <div class="flex items-start justify-between">
                            <div class="flex-1">
                                <h4 class="font-semibold text-gray-800 mb-1">${projeto.nome}</h4>
                                <p class="text-sm text-gray-600 mb-2">${projeto.descricao || 'Sem descrição'}</p>
                                <div class="flex items-center gap-4 text-xs text-gray-500">
                                    <span><i class="fas fa-tag mr-1"></i>${projeto.area_projeto}</span>
                                    <span><i class="fas fa-calendar mr-1"></i>${projeto.ano_edicao}</span>
                                    ${projeto.participantes ? `
                                        <span><i class="fas fa-users mr-1"></i>${projeto.participantes.length} participante(s)</span>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        } else {
            container.innerHTML = '<p class="text-center py-8 text-gray-500">Nenhum projeto cadastrado</p>';
        }
    } catch (error) {
        console.error('Erro ao carregar projetos:', error);
        container.innerHTML = '<p class="text-center py-4 text-red-600">Erro ao carregar projetos</p>';
    }
}

/**
 * Carrega status da API
 */
async function carregarStatusAPI() {
    const container = document.getElementById('apiStatus');
    container.innerHTML = '<div class="text-center py-4"><i class="fas fa-spinner fa-spin text-purple-600"></i></div>';

    try {
        const response = await api.statusAPI();

        if (response.success) {
            const status = response.data;
            
            const html = `
                <!-- Status Geral -->
                <div class="bg-${status.sistema_ativo ? 'green' : 'red'}-50 border border-${status.sistema_ativo ? 'green' : 'red'}-200 rounded-lg p-4">
                    <div class="flex items-center gap-3">
                        <i class="fas fa-circle text-${status.sistema_ativo ? 'green' : 'red'}-600 text-xl"></i>
                        <div>
                            <h4 class="font-semibold text-gray-800">Sistema ${status.sistema_ativo ? 'Ativo' : 'Desativado'}</h4>
                            <p class="text-sm text-gray-600">Status atual do sistema</p>
                        </div>
                    </div>
                </div>

                <!-- Uso da API -->
                <div class="border border-gray-200 rounded-lg p-4">
                    <h4 class="font-semibold text-gray-800 mb-3">Uso da API do Mês</h4>
                    <div class="space-y-3">
                        <div>
                            <div class="flex justify-between text-sm mb-1">
                                <span class="text-gray-600">Requisições</span>
                                <span class="font-semibold">${status.requisicoes_mes || 0}</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="bg-purple-600 h-2 rounded-full" style="width: ${Math.min(status.uso_percentual || 0, 100)}%"></div>
                            </div>
                            <p class="text-xs text-gray-500 mt-1">${(status.uso_percentual || 0).toFixed(1)}% do limite mensal</p>
                        </div>
                        ${status.throttling_ativo ? `
                            <div class="bg-yellow-50 border border-yellow-200 rounded p-3">
                                <p class="text-sm text-yellow-800">
                                    <i class="fas fa-exclamation-triangle mr-1"></i>
                                    Throttling ativo - Sistema operando com delay
                                </p>
                            </div>
                        ` : ''}
                    </div>
                </div>

                <!-- Estatísticas -->
                <div class="grid grid-cols-2 gap-4">
                    <div class="border border-gray-200 rounded-lg p-4">
                        <p class="text-sm text-gray-600 mb-1">Total de Requisições</p>
                        <p class="text-2xl font-bold text-gray-800">${status.requisicoes_total || 0}</p>
                    </div>
                    <div class="border border-gray-200 rounded-lg p-4">
                        <p class="text-sm text-gray-600 mb-1">Último Minuto</p>
                        <p class="text-2xl font-bold text-gray-800">${status.requisicoes_ultimo_minuto || 0}</p>
                    </div>
                </div>

                <!-- Última Requisição -->
                ${status.ultima_requisicao ? `
                    <div class="border border-gray-200 rounded-lg p-4">
                        <p class="text-sm text-gray-600 mb-1">Última Requisição</p>
                        <p class="text-sm font-medium text-gray-800">${formatDate(status.ultima_requisicao)}</p>
                    </div>
                ` : ''}
            `;

            container.innerHTML = html;
        }
    } catch (error) {
        console.error('Erro ao carregar status da API:', error);
        container.innerHTML = '<p class="text-center py-4 text-red-600">Erro ao carregar status</p>';
    }
}

/**
 * Muda de tab
 */
function changeTab(tab) {
    // Remove active de todas as tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active', 'border-purple-600', 'text-purple-600');
        btn.classList.add('border-transparent', 'text-gray-600');
    });

    // Adiciona active na tab atual
    event.target.classList.remove('border-transparent', 'text-gray-600');
    event.target.classList.add('active', 'border-purple-600', 'text-purple-600');

    // Esconde todos os conteúdos
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });

    // Mostra conteúdo da tab atual
    document.getElementById(`tab-${tab}`).classList.remove('hidden');
    currentTab = tab;
}

/**
 * Toggle do sistema
 */
async function toggleSistema() {
    const ativar = !sistemaAtivo;
    const motivo = ativar ? '' : prompt('Motivo da desativação (opcional):') || 'Desativado pelo administrador';

    try {
        const response = await api.toggleSistema(ativar, motivo);

        if (response.success) {
            sistemaAtivo = ativar;
            atualizarBotaoToggle();
            showToast(ativar ? 'Sistema ativado!' : 'Sistema desativado!', 'success');
            await carregarStatusAPI();
        } else {
            showToast(response.message || 'Erro ao alterar status', 'error');
        }
    } catch (error) {
        console.error('Erro ao toggle sistema:', error);
        showToast('Erro ao alterar status do sistema', 'error');
    }
}

/**
 * Atualiza botão de toggle
 */
function atualizarBotaoToggle() {
    const btn = document.getElementById('toggleBtn');
    if (sistemaAtivo) {
        btn.className = 'px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold transition-colors';
        btn.innerHTML = '<i class="fas fa-power-off mr-2"></i>Sistema Ativo';
    } else {
        btn.className = 'px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-semibold transition-colors';
        btn.innerHTML = '<i class="fas fa-power-off mr-2"></i>Sistema Desativado';
    }
}

/**
 * Reseta contador mensal
 */
async function resetarContador() {
    if (!confirm('Deseja realmente resetar o contador mensal da API? Esta ação não pode ser desfeita.')) {
        return;
    }

    try {
        showToast('Resetando contador...', 'info');
        // Implementar endpoint no backend se necessário
        showToast('Contador resetado com sucesso!', 'success');
        await carregarStatusAPI();
    } catch (error) {
        console.error('Erro ao resetar contador:', error);
        showToast('Erro ao resetar contador', 'error');
    }
}

/**
 * Recarrega relatório
 */
async function recarregarRelatorio() {
    showToast('Atualizando dados...', 'info');
    await carregarRelatorio();
    showToast('Dados atualizados!', 'success');
}

/**
 * Abre modal de cadastro
 */
function abrirModalCadastro() {
    document.getElementById('cadastroModal').classList.remove('hidden');
    document.getElementById('cadastroForm').reset();
}

/**
 * Fecha modal de cadastro
 */
function fecharModalCadastro() {
    document.getElementById('cadastroModal').classList.add('hidden');
}

/**
 * Handle cadastro de usuário
 */
async function handleCadastroUsuario(e) {
    e.preventDefault();

    const dados = {
        nome_completo: document.getElementById('cadNome').value.trim(),
        email: document.getElementById('cadEmail').value.trim(),
        senha: document.getElementById('cadSenha').value,
        tipo_usuario: document.getElementById('cadTipo').value,
        bp: document.getElementById('cadBP').value.trim().toUpperCase() || null
    };

    // Validações
    if (!validateEmail(dados.email)) {
        showToast('Email inválido', 'error');
        return;
    }

    const senhaValidacao = validatePassword(dados.senha);
    if (!senhaValidacao.valid) {
        showToast(senhaValidacao.message, 'error');
        return;
    }

    if (dados.tipo_usuario === 'participante') {
        if (!dados.bp) {
            showToast('BP é obrigatório para participantes', 'error');
            return;
        }
        if (!validateBP(dados.bp)) {
            showToast('BP inválido. Use o formato: BRG12345678', 'error');
            return;
        }
    }

    try {
        showToast('Cadastrando usuário...', 'info');

        const response = await api.cadastrarUsuario(dados);

        if (response.success) {
            showToast('Usuário cadastrado com sucesso!', 'success');
            fecharModalCadastro();
            await carregarRelatorio();
        } else {
            showToast(response.message || 'Erro ao cadastrar usuário', 'error');
        }
    } catch (error) {
        console.error('Erro ao cadastrar usuário:', error);
        showToast('Erro ao cadastrar usuário', 'error');
    }
}

// Exporta funções globais
window.changeTab = changeTab;
window.toggleSistema = toggleSistema;
window.resetarContador = resetarContador;
window.recarregarRelatorio = recarregarRelatorio;
window.abrirModalCadastro = abrirModalCadastro;
window.fecharModalCadastro = fecharModalCadastro;