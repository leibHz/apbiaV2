"""
APBIA - API Principal
Sistema de Ajuda com IA para Projetos da Bragantec
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from config.settings import settings
from config.database import db
from utils.logger import logger
from utils.helpers import helpers

# Controllers
from controllers.chat_controller import chat_controller
from controllers.gemini_controller import gemini_controller
from controllers.admin_controller import admin_controller

# Services
from services.auth_service import auth_service
from dao.projeto_dao import ProjetoDAO
from dao.usuario_dao import UsuarioDAO

# Inicializa Flask
app = Flask(__name__)
CORS(app)

# Inicializa DAOs
projeto_dao = ProjetoDAO()
usuario_dao = UsuarioDAO()

# ==================== MIDDLEWARE DE AUTENTICAÇÃO ====================

def require_auth(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify(helpers.create_response(False, "Token não fornecido")), 401
        
        token = auth_header.split(' ')[1]
        sucesso, payload, erro = auth_service.validar_token(token)
        
        if not sucesso:
            return jsonify(helpers.create_response(False, erro or "Token inválido")), 401
        
        # Adiciona dados do usuário ao request
        request.user_id = payload['user_id']
        request.user_tipo = payload['tipo_usuario']
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_admin(f):
    """Decorator para rotas que requerem privilégios de admin"""
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        if request.user_tipo != 'admin':
            return jsonify(helpers.create_response(False, "Acesso negado. Apenas administradores.")), 403
        return f(*args, **kwargs)
    
    return decorated_function


# ==================== ROTAS DE AUTENTICAÇÃO ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login de usuário"""
    try:
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')
        bp = data.get('bp')
        
        if not email or not senha:
            return jsonify(helpers.create_response(False, "Email e senha são obrigatórios")), 400
        
        sucesso, user_data, erro = auth_service.login(email, senha, bp)
        
        if sucesso:
            return jsonify(helpers.create_response(True, "Login realizado com sucesso", data=user_data)), 200
        else:
            return jsonify(helpers.create_response(False, erro or "Erro ao fazer login")), 401
            
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


@app.route('/api/auth/validate', methods=['GET'])
@require_auth
def validate_token():
    """Valida token JWT"""
    try:
        usuario = usuario_dao.buscar_por_id(request.user_id)
        
        if usuario:
            return jsonify(helpers.create_response(
                True, 
                "Token válido",
                data=usuario.to_dict()
            )), 200
        else:
            return jsonify(helpers.create_response(False, "Usuário não encontrado")), 404
            
    except Exception as e:
        logger.error(f"Erro ao validar token: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


@app.route('/api/auth/alterar-senha', methods=['POST'])
@require_auth
def alterar_senha():
    """Altera senha do usuário"""
    try:
        data = request.get_json()
        senha_atual = data.get('senha_atual')
        nova_senha = data.get('nova_senha')
        
        if not senha_atual or not nova_senha:
            return jsonify(helpers.create_response(False, "Senhas são obrigatórias")), 400
        
        sucesso, erro = auth_service.alterar_senha(request.user_id, senha_atual, nova_senha)
        
        if sucesso:
            return jsonify(helpers.create_response(True, "Senha alterada com sucesso")), 200
        else:
            return jsonify(helpers.create_response(False, erro or "Erro ao alterar senha")), 400
            
    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


# ==================== ROTAS DE CHAT ====================

@app.route('/api/chat/criar', methods=['POST'])
@require_auth
def criar_chat():
    """Cria novo chat"""
    try:
        data = request.get_json()
        projeto_id = data.get('projeto_id')
        tipo_ia = data.get('tipo_ia', 'gemini')
        titulo = data.get('titulo', '')
        
        if not projeto_id:
            return jsonify(helpers.create_response(False, "projeto_id é obrigatório")), 400
        
        result = chat_controller.criar_chat(projeto_id, tipo_ia, titulo)
        return jsonify(result), 201 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Erro ao criar chat: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


@app.route('/api/chat/<int:chat_id>', methods=['GET'])
@require_auth
def buscar_chat(chat_id):
    """Busca chat por ID"""
    try:
        incluir_mensagens = request.args.get('incluir_mensagens', 'true').lower() == 'true'
        result = chat_controller.buscar_chat(chat_id, incluir_mensagens)
        return jsonify(result), 200 if result['success'] else 404
        
    except Exception as e:
        logger.error(f"Erro ao buscar chat: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


@app.route('/api/chat/projeto/<int:projeto_id>', methods=['GET'])
@require_auth
def listar_chats_projeto(projeto_id):
    """Lista chats de um projeto"""
    try:
        result = chat_controller.listar_chats_projeto(projeto_id)
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar chats: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


@app.route('/api/chat/<int:chat_id>/mensagens', methods=['GET'])
@require_auth
def listar_mensagens_chat(chat_id):
    """Lista mensagens de um chat"""
    try:
        limit = int(request.args.get('limit', 100))
        result = chat_controller.listar_mensagens_chat(chat_id, limit)
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar mensagens: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


@app.route('/api/chat/<int:chat_id>', methods=['DELETE'])
@require_auth
def deletar_chat(chat_id):
    """Deleta um chat"""
    try:
        result = chat_controller.deletar_chat(chat_id)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Erro ao deletar chat: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


# ==================== ROTAS DE IA ====================

@app.route('/api/ia/mensagem', methods=['POST'])
@require_auth
def enviar_mensagem():
    """Envia mensagem e recebe resposta da IA"""
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        conteudo = data.get('conteudo')
        usar_thinking = data.get('usar_thinking', False)
        
        if not chat_id or not conteudo:
            return jsonify(helpers.create_response(False, "chat_id e conteudo são obrigatórios")), 400
        
        result = gemini_controller.processar_mensagem(
            chat_id, 
            request.user_id, 
            conteudo, 
            usar_thinking
        )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


@app.route('/api/ia/nota-orientador', methods=['POST'])
@require_auth
def adicionar_nota_orientador():
    """Adiciona nota do orientador"""
    try:
        # Verifica se é orientador ou admin
        if request.user_tipo not in ['orientador', 'admin']:
            return jsonify(helpers.create_response(False, "Apenas orientadores podem adicionar notas")), 403
        
        data = request.get_json()
        mensagem_id = data.get('mensagem_id')
        nota = data.get('nota')
        
        if not mensagem_id or not nota:
            return jsonify(helpers.create_response(False, "mensagem_id e nota são obrigatórios")), 400
        
        result = gemini_controller.adicionar_nota_orientador(mensagem_id, request.user_id, nota)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Erro ao adicionar nota: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


@app.route('/api/ia/status', methods=['GET'])
@require_auth
def status_api():
    """Status da API do Gemini"""
    try:
        result = gemini_controller.obter_status_api()
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


@app.route('/api/ia/contextos/testar', methods=['GET'])
@require_auth
def testar_contextos():
    """Testa carregamento de contextos"""
    try:
        from services.context_service import context_service
        
        # Testa conexão
        sucesso_conexao, msg_conexao = context_service.testar_conexao_bucket()
        
        # Tenta carregar contextos
        sucesso_carga, contextos, erro_carga = context_service.carregar_todos_contextos()
        
        return jsonify(helpers.create_response(
            True,
            "Teste de contextos concluído",
            data={
                'conexao_bucket': {
                    'sucesso': sucesso_conexao,
                    'mensagem': msg_conexao
                },
                'carga_contextos': {
                    'sucesso': sucesso_carga,
                    'total_carregados': len(contextos) if contextos else 0,
                    'erro': erro_carga,
                    'resumo': context_service.obter_resumo_contextos()
                },
                'contextos_disponiveis': context_service.listar_contextos_disponiveis()
            }
        )), 200
        
    except Exception as e:
        logger.error(f"Erro ao testar contextos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify(helpers.create_response(False, "Erro ao testar contextos", error=str(e))), 500


# ==================== ROTAS DE PROJETOS ====================

@app.route('/api/projetos', methods=['GET'])
@require_auth
def listar_projetos():
    """Lista projetos do usuário"""
    try:
        usuario = usuario_dao.buscar_por_id(request.user_id)
        
        if not usuario:
            return jsonify(helpers.create_response(False, "Usuário não encontrado")), 404
        
        # Se for admin, lista todos
        if usuario.is_admin():
            projetos = projeto_dao.listar_todos()
        # Se for participante, lista projetos que participa
        elif usuario.is_participante():
            projetos = projeto_dao.listar_projetos_participante(request.user_id)
        # Se for orientador, lista projetos que orienta
        elif usuario.is_orientador():
            projetos = projeto_dao.listar_projetos_orientador(request.user_id)
        else:
            projetos = []
        
        return jsonify(helpers.create_response(
            True,
            f"{len(projetos)} projeto(s) encontrado(s)",
            data=[p.to_dict() for p in projetos]
        )), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar projetos: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


@app.route('/api/projetos/<int:projeto_id>', methods=['GET'])
@require_auth
def buscar_projeto(projeto_id):
    """Busca projeto por ID"""
    try:
        projeto = projeto_dao.buscar_por_id(projeto_id)
        
        if not projeto:
            return jsonify(helpers.create_response(False, "Projeto não encontrado")), 404
        
        return jsonify(helpers.create_response(
            True,
            "Projeto encontrado",
            data=projeto.to_dict()
        )), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar projeto: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


# ==================== ROTAS DE USUÁRIO ====================

@app.route('/api/usuario/perfil', methods=['GET'])
@require_auth
def meu_perfil():
    """Retorna perfil do usuário logado"""
    try:
        usuario = usuario_dao.buscar_por_id(request.user_id)
        
        if usuario:
            return jsonify(helpers.create_response(
                True,
                "Perfil obtido com sucesso",
                data=usuario.to_dict()
            )), 200
        else:
            return jsonify(helpers.create_response(False, "Usuário não encontrado")), 404
            
    except Exception as e:
        logger.error(f"Erro ao buscar perfil: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


# ==================== ROTAS ADMIN ====================

@app.route('/api/admin/cadastrar-usuario', methods=['POST'])
@require_admin
def cadastrar_usuario():
    """Cadastra novo usuário (apenas admin)"""
    try:
        data = request.get_json()
        result = admin_controller.cadastrar_usuario_completo(data)
        return jsonify(result), 201 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Erro ao cadastrar usuário: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


@app.route('/api/admin/sistema/status', methods=['GET'])
@require_admin
def sistema_status():
    """Status completo do sistema"""
    try:
        result = admin_controller.obter_relatorio_completo()
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


@app.route('/api/admin/sistema/toggle', methods=['POST'])
@require_admin
def sistema_toggle():
    """Ativa/desativa sistema"""
    try:
        data = request.get_json()
        ativar = data.get('ativar', True)
        motivo = data.get('motivo', '')
        
        if ativar:
            result = admin_controller.ativar_sistema()
        else:
            result = admin_controller.desativar_sistema(motivo)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erro ao toggle sistema: {e}")
        return jsonify(helpers.create_response(False, "Erro interno do servidor")), 500


# ==================== ROTAS DE HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check da API"""
    try:
        db_ok = db.health_check()
        
        return jsonify({
            "status": "ok",
            "version": settings.VERSION,
            "database": "ok" if db_ok else "error",
            "timestamp": helpers.format_datetime(datetime.now())
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    from datetime import datetime
    
    print("\n" + "="*50)
    print(f"🚀 Iniciando {settings.PROJECT_NAME} v{settings.VERSION}")
    print("="*50)
    
    # Valida configurações
    try:
        settings.validate()
        print("✅ Configurações validadas")
    except ValueError as e:
        print(f"❌ Erro nas configurações: {e}")
        exit(1)
    
    # Testa conexão com banco
    if db.health_check():
        print("✅ Conexão com Supabase estabelecida")
    else:
        print("❌ Erro ao conectar com Supabase")
        exit(1)
    
    print("\n🌐 Servidor rodando em:")
    print(f"   Local: http://127.0.0.1:{settings.PORT}")
    print(f"   Rede: http://{settings.HOST}:{settings.PORT}")
    print("\n" + "="*50 + "\n")
    
    # Inicia servidor
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG
    )