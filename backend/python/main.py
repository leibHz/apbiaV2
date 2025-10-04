"""
API Principal do APBIA
Sistema de IA para auxiliar projetos da Bragantec
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from config.settings import settings
from config.database import db
from controllers.chat_controller import chat_controller
from controllers.gemini_controller import gemini_controller
from services.auth_service import auth_service
from services.api_monitor_service import api_monitor
from dao.usuario_dao import UsuarioDAO
from dao.projeto_dao import ProjetoDAO
from utils.logger import logger
from utils.helpers import helpers
from functools import wraps

# Inicializa Flask
app = Flask(__name__)
CORS(app)

# Configurações
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = settings.MAX_UPLOAD_SIZE

# DAOs
usuario_dao = UsuarioDAO()
projeto_dao = ProjetoDAO()


# ==================== MIDDLEWARE ====================

def require_auth(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify(helpers.create_response(False, "Token não fornecido", error="Unauthorized")), 401
        
        sucesso, payload, erro = auth_service.validar_token(token)
        
        if not sucesso:
            return jsonify(helpers.create_response(False, "Token inválido", error=erro)), 401
        
        request.user_id = payload['user_id']
        request.user_tipo = payload['tipo_usuario']
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_admin(f):
    """Decorator para rotas que requerem admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.user_tipo != 'admin':
            return jsonify(helpers.create_response(False, "Acesso negado", error="Forbidden")), 403
        return f(*args, **kwargs)
    
    return decorated_function


# ==================== ROTAS DE AUTENTICAÇÃO ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Rota de login"""
    try:
        data = request.json
        email = data.get('email')
        senha = data.get('senha')
        bp = data.get('bp')
        
        if not email or not senha:
            return jsonify(helpers.create_response(False, "Email e senha são obrigatórios")), 400
        
        sucesso, user_data, erro = auth_service.login(email, senha, bp)
        
        if sucesso:
            return jsonify(helpers.create_response(True, "Login realizado com sucesso", data=user_data)), 200
        else:
            return jsonify(helpers.create_response(False, "Falha no login", error=erro)), 401
            
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return jsonify(helpers.create_response(False, "Erro no servidor", error=str(e))), 500


@app.route('/api/auth/validate', methods=['GET'])
@require_auth
def validate_token():
    """Valida token atual"""
    usuario = usuario_dao.buscar_por_id(request.user_id)
    
    if usuario:
        return jsonify(helpers.create_response(True, "Token válido", data=usuario.to_dict())), 200
    else:
        return jsonify(helpers.create_response(False, "Usuário não encontrado")), 404


@app.route('/api/auth/alterar-senha', methods=['POST'])
@require_auth
def alterar_senha():
    """Altera senha do usuário"""
    try:
        data = request.json
        senha_atual = data.get('senha_atual')
        nova_senha = data.get('nova_senha')
        
        sucesso, erro = auth_service.alterar_senha(request.user_id, senha_atual, nova_senha)
        
        if sucesso:
            return jsonify(helpers.create_response(True, "Senha alterada com sucesso")), 200
        else:
            return jsonify(helpers.create_response(False, "Erro ao alterar senha", error=erro)), 400
            
    except Exception as e:
        return jsonify(helpers.create_response(False, "Erro no servidor", error=str(e))), 500


# ==================== ROTAS DE CHAT ====================

@app.route('/api/chat/criar', methods=['POST'])
@require_auth
def criar_chat():
    """Cria novo chat"""
    try:
        data = request.json
        projeto_id = data.get('projeto_id')
        tipo_ia = data.get('tipo_ia', 'gemini')
        titulo = data.get('titulo', '')
        
        resultado = chat_controller.criar_chat(projeto_id, tipo_ia, titulo)
        
        if resultado['success']:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        return jsonify(helpers.create_response(False, "Erro ao criar chat", error=str(e))), 500


@app.route('/api/chat/<int:chat_id>', methods=['GET'])
@require_auth
def buscar_chat(chat_id):
    """Busca chat por ID"""
    incluir_mensagens = request.args.get('incluir_mensagens', 'true').lower() == 'true'
    resultado = chat_controller.buscar_chat(chat_id, incluir_mensagens)
    
    if resultado['success']:
        return jsonify(resultado), 200
    else:
        return jsonify(resultado), 404


@app.route('/api/chat/projeto/<int:projeto_id>', methods=['GET'])
@require_auth
def listar_chats_projeto(projeto_id):
    """Lista chats de um projeto"""
    resultado = chat_controller.listar_chats_projeto(projeto_id)
    return jsonify(resultado), 200


@app.route('/api/chat/<int:chat_id>/mensagens', methods=['GET'])
@require_auth
def listar_mensagens(chat_id):
    """Lista mensagens de um chat"""
    limit = request.args.get('limit', 100, type=int)
    resultado = chat_controller.listar_mensagens_chat(chat_id, limit)
    return jsonify(resultado), 200


@app.route('/api/chat/<int:chat_id>', methods=['DELETE'])
@require_auth
def deletar_chat(chat_id):
    """Deleta um chat"""
    resultado = chat_controller.deletar_chat(chat_id)
    
    if resultado['success']:
        return jsonify(resultado), 200
    else:
        return jsonify(resultado), 400


# ==================== ROTAS DE IA ====================

@app.route('/api/ia/mensagem', methods=['POST'])
@require_auth
def enviar_mensagem():
    """Envia mensagem para IA"""
    try:
        # Verifica se sistema está ativo
        if not api_monitor.uso_atual['sistema_ativo']:
            return jsonify(helpers.create_response(
                False, 
                "Sistema temporariamente desativado",
                error="System disabled"
            )), 503
        
        data = request.json
        chat_id = data.get('chat_id')
        conteudo = data.get('conteudo')
        usar_thinking = data.get('usar_thinking', False)
        
        if not chat_id or not conteudo:
            return jsonify(helpers.create_response(False, "chat_id e conteudo são obrigatórios")), 400
        
        resultado = gemini_controller.processar_mensagem(
            chat_id, 
            request.user_id, 
            conteudo, 
            usar_thinking
        )
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        return jsonify(helpers.create_response(False, "Erro ao processar mensagem", error=str(e))), 500


@app.route('/api/ia/nota-orientador', methods=['POST'])
@require_auth
def adicionar_nota():
    """Adiciona nota do orientador"""
    try:
        # Verifica se é orientador ou admin
        if request.user_tipo not in ['orientador', 'admin']:
            return jsonify(helpers.create_response(False, "Apenas orientadores podem adicionar notas")), 403
        
        data = request.json
        mensagem_id = data.get('mensagem_id')
        nota = data.get('nota')
        
        resultado = gemini_controller.adicionar_nota_orientador(mensagem_id, request.user_id, nota)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        return jsonify(helpers.create_response(False, "Erro ao adicionar nota", error=str(e))), 500


@app.route('/api/ia/status', methods=['GET'])
@require_auth
def status_api():
    """Retorna status da API"""
    resultado = gemini_controller.obter_status_api()
    return jsonify(resultado), 200


# ==================== ROTAS DE PROJETOS ====================

@app.route('/api/projetos', methods=['GET'])
@require_auth
def listar_projetos():
    """Lista todos os projetos"""
    try:
        projetos = projeto_dao.listar_todos()
        return jsonify(helpers.create_response(
            True,
            f"{len(projetos)} projeto(s) encontrado(s)",
            data=[p.to_dict() for p in projetos]
        )), 200
    except Exception as e:
        return jsonify(helpers.create_response(False, "Erro ao listar projetos", error=str(e))), 500


@app.route('/api/projetos/<int:projeto_id>', methods=['GET'])
@require_auth
def buscar_projeto(projeto_id):
    """Busca projeto por ID"""
    try:
        projeto = projeto_dao.buscar_por_id(projeto_id)
        
        if projeto:
            return jsonify(helpers.create_response(True, "Projeto encontrado", data=projeto.to_dict())), 200
        else:
            return jsonify(helpers.create_response(False, "Projeto não encontrado")), 404
    except Exception as e:
        return jsonify(helpers.create_response(False, "Erro ao buscar projeto", error=str(e))), 500


# ==================== ROTAS DE USUÁRIO ====================

@app.route('/api/usuario/perfil', methods=['GET'])
@require_auth
def meu_perfil():
    """Retorna perfil do usuário logado"""
    usuario = usuario_dao.buscar_por_id(request.user_id)
    
    if usuario:
        return jsonify(helpers.create_response(True, "Perfil encontrado", data=usuario.to_dict())), 200
    else:
        return jsonify(helpers.create_response(False, "Usuário não encontrado")), 404


# ==================== ROTAS DE ADMIN ====================

@app.route('/api/admin/cadastrar-usuario', methods=['POST'])
@require_auth
@require_admin
def admin_cadastrar_usuario():
    """Admin cadastra novo usuário"""
    try:
        data = request.json
        
        sucesso, usuario, erro = auth_service.cadastrar_usuario(
            nome_completo=data.get('nome_completo'),
            email=data.get('email'),
            senha=data.get('senha'),
            tipo_usuario_nome=data.get('tipo_usuario'),
            bp=data.get('bp')
        )
        
        if sucesso:
            return jsonify(helpers.create_response(True, "Usuário cadastrado", data=usuario.to_dict())), 201
        else:
            return jsonify(helpers.create_response(False, "Erro ao cadastrar", error=erro)), 400
            
    except Exception as e:
        return jsonify(helpers.create_response(False, "Erro no servidor", error=str(e))), 500


@app.route('/api/admin/sistema/status', methods=['GET'])
@require_auth
@require_admin
def admin_sistema_status():
    """Status completo do sistema"""
    try:
        relatorio = api_monitor.obter_relatorio()
        estatisticas = api_monitor.obter_estatisticas_periodo()
        
        return jsonify(helpers.create_response(True, "Status obtido", data={
            'relatorio': relatorio,
            'estatisticas': estatisticas,
            'database_ok': db.health_check()
        })), 200
    except Exception as e:
        return jsonify(helpers.create_response(False, "Erro ao obter status", error=str(e))), 500


@app.route('/api/admin/sistema/toggle', methods=['POST'])
@require_auth
@require_admin
def admin_toggle_sistema():
    """Ativa/desativa sistema"""
    try:
        data = request.json
        ativar = data.get('ativar', True)
        
        if ativar:
            api_monitor.ativar_sistema()
        else:
            motivo = data.get('motivo', 'Manutenção programada')
            api_monitor.desativar_sistema(motivo)
        
        return jsonify(helpers.create_response(True, "Sistema atualizado", data={
            'sistema_ativo': api_monitor.uso_atual['sistema_ativo']
        })), 200
    except Exception as e:
        return jsonify(helpers.create_response(False, "Erro ao atualizar sistema", error=str(e))), 500


# ==================== ROTAS DE SAÚDE ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check do sistema"""
    return jsonify({
        'status': 'ok',
        'version': settings.VERSION,
        'database': 'ok' if db.health_check() else 'error',
        'timestamp': helpers.format_datetime(datetime.now())
    }), 200


@app.route('/', methods=['GET'])
def root():
    """Rota raiz"""
    return jsonify({
        'name': settings.PROJECT_NAME,
        'version': settings.VERSION,
        'message': 'API APBIA - Sistema de IA para Bragantec'
    }), 200


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify(helpers.create_response(False, "Rota não encontrada", error="Not found")), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erro interno: {error}")
    return jsonify(helpers.create_response(False, "Erro interno do servidor", error="Internal error")), 500


@app.errorhandler(413)
def too_large(error):
    return jsonify(helpers.create_response(False, "Arquivo muito grande", error="File too large")), 413


# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    try:
        # Valida configurações
        settings.validate()
        
        # Testa conexão com banco
        if db.health_check():
            logger.info("✅ Conexão com banco de dados OK")
        else:
            logger.error("❌ Falha na conexão com banco de dados")
        
        # Inicia servidor
        logger.info(f"🚀 Iniciando {settings.PROJECT_NAME} v{settings.VERSION}")
        logger.info(f"🌐 Servidor: http://{settings.HOST}:{settings.PORT}")
        
        app.run(
            host=settings.HOST,
            port=settings.PORT,
            debug=settings.DEBUG
        )
        
    except Exception as e:
        logger.critical(f"❌ Falha ao iniciar servidor: {e}")
        raise