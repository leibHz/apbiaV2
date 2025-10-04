"""
Controller para funcionalidades administrativas
"""
from typing import Dict, List, Optional
from dao.usuario_dao import UsuarioDAO, TipoUsuarioDAO
from dao.projeto_dao import ProjetoDAO
from dao.chat_dao import ChatDAO
from dao.mensagem_dao import MensagemDAO
from services.auth_service import auth_service
from services.api_monitor_service import api_monitor
from services.context_service import context_service
from models.usuario import Usuario
from models.projeto import Projeto
from utils.logger import logger
from utils.helpers import helpers
from utils.validators import validators
from config.database import db


class AdminController:
    """Controller para operações administrativas"""
    
    def __init__(self):
        self.usuario_dao = UsuarioDAO()
        self.tipo_usuario_dao = TipoUsuarioDAO()
        self.projeto_dao = ProjetoDAO()
        self.chat_dao = ChatDAO()
        self.mensagem_dao = MensagemDAO()
    
    # ==================== GERENCIAMENTO DE USUÁRIOS ====================
    
    def listar_usuarios(self, tipo_usuario: Optional[str] = None) -> Dict:
        """Lista todos os usuários ou filtra por tipo"""
        try:
            if tipo_usuario:
                tipo = self.tipo_usuario_dao.buscar_por_nome(tipo_usuario)
                if tipo:
                    usuarios = self.usuario_dao.listar_por_tipo(tipo.id)
                else:
                    return helpers.create_response(False, "Tipo de usuário inválido")
            else:
                # Lista todos (implementar no DAO se necessário)
                usuarios = []
                for tipo_nome in ['participante', 'orientador', 'admin']:
                    tipo = self.tipo_usuario_dao.buscar_por_nome(tipo_nome)
                    if tipo:
                        usuarios.extend(self.usuario_dao.listar_por_tipo(tipo.id))
            
            return helpers.create_response(
                True,
                f"{len(usuarios)} usuário(s) encontrado(s)",
                data=[u.to_dict() for u in usuarios]
            )
            
        except Exception as e:
            logger.error_trace(e, "listar_usuarios")
            return helpers.create_response(False, "Erro ao listar usuários", error=str(e))
    
    def cadastrar_usuario_completo(self, dados: Dict) -> Dict:
        """Cadastra usuário com validações completas"""
        try:
            sucesso, usuario, erro = auth_service.cadastrar_usuario(
                nome_completo=dados.get('nome_completo'),
                email=dados.get('email'),
                senha=dados.get('senha'),
                tipo_usuario_nome=dados.get('tipo_usuario'),
                bp=dados.get('bp')
            )
            
            if sucesso:
                logger.info(f"✅ Admin cadastrou usuário: {usuario.email}")
                return helpers.create_response(
                    True,
                    "Usuário cadastrado com sucesso",
                    data=usuario.to_dict()
                )
            else:
                return helpers.create_response(False, "Erro ao cadastrar usuário", error=erro)
                
        except Exception as e:
            logger.error_trace(e, "cadastrar_usuario_completo")
            return helpers.create_response(False, "Erro ao cadastrar usuário", error=str(e))
    
    def atualizar_usuario(self, usuario_id: int, dados: Dict) -> Dict:
        """Atualiza dados do usuário"""
        try:
            usuario = self.usuario_dao.buscar_por_id(usuario_id)
            if not usuario:
                return helpers.create_response(False, "Usuário não encontrado")
            
            # Atualiza campos permitidos
            if 'nome_completo' in dados:
                usuario.nome_completo = dados['nome_completo']
            
            if 'email' in dados:
                if not validators.validate_email(dados['email']):
                    return helpers.create_response(False, "Email inválido")
                
                # Verifica se email já existe (exceto o próprio usuário)
                if self.usuario_dao.email_existe(dados['email']):
                    usuario_existente = self.usuario_dao.buscar_por_email(dados['email'])
                    if usuario_existente and usuario_existente.id != usuario_id:
                        return helpers.create_response(False, "Email já cadastrado")
                
                usuario.email = dados['email']
            
            if 'bp' in dados and dados['bp']:
                if not validators.validate_bp(dados['bp']):
                    return helpers.create_response(False, "BP inválido")
                usuario.bp = dados['bp'].upper()
            
            usuario_atualizado = self.usuario_dao.atualizar_usuario(usuario)
            
            if usuario_atualizado:
                return helpers.create_response(
                    True,
                    "Usuário atualizado com sucesso",
                    data=usuario_atualizado.to_dict()
                )
            else:
                return helpers.create_response(False, "Erro ao atualizar usuário")
                
        except Exception as e:
            logger.error_trace(e, "atualizar_usuario")
            return helpers.create_response(False, "Erro ao atualizar usuário", error=str(e))
    
    def resetar_senha_usuario(self, usuario_id: int, nova_senha: str) -> Dict:
        """Admin reseta senha de um usuário"""
        try:
            usuario = self.usuario_dao.buscar_por_id(usuario_id)
            if not usuario:
                return helpers.create_response(False, "Usuário não encontrado")
            
            # Valida nova senha
            senha_valida, erro_senha = validators.validate_senha(nova_senha)
            if not senha_valida:
                return helpers.create_response(False, erro_senha)
            
            # Atualiza senha
            usuario.senha_hash = helpers.hash_password(nova_senha)
            self.usuario_dao.atualizar_usuario(usuario)
            
            logger.info(f"✅ Admin resetou senha do usuário ID: {usuario_id}")
            return helpers.create_response(True, "Senha resetada com sucesso")
            
        except Exception as e:
            logger.error_trace(e, "resetar_senha_usuario")
            return helpers.create_response(False, "Erro ao resetar senha", error=str(e))
    
    # ==================== GERENCIAMENTO DE PROJETOS ====================
    
    def criar_projeto(self, dados: Dict) -> Dict:
        """Cria novo projeto"""
        try:
            # Valida dados
            if not dados.get('nome'):
                return helpers.create_response(False, "Nome do projeto é obrigatório")
            
            if not dados.get('area_projeto'):
                return helpers.create_response(False, "Área do projeto é obrigatória")
            
            if not validators.validate_area_projeto(dados['area_projeto']):
                return helpers.create_response(False, "Área do projeto inválida")
            
            ano = dados.get('ano_edicao')
            if not ano or not validators.validate_ano_edicao(ano):
                return helpers.create_response(False, "Ano de edição inválido")
            
            # Cria projeto
            projeto = Projeto(
                nome=dados['nome'],
                descricao=dados.get('descricao'),
                area_projeto=dados['area_projeto'],
                ano_edicao=ano
            )
            
            projeto_criado = self.projeto_dao.criar_projeto(projeto)
            
            if projeto_criado:
                logger.info(f"✅ Projeto criado: {projeto_criado.nome}")
                return helpers.create_response(
                    True,
                    "Projeto criado com sucesso",
                    data=projeto_criado.to_dict()
                )
            else:
                return helpers.create_response(False, "Erro ao criar projeto")
                
        except Exception as e:
            logger.error_trace(e, "criar_projeto")
            return helpers.create_response(False, "Erro ao criar projeto", error=str(e))
    
    def vincular_participante_projeto(self, projeto_id: int, participante_id: int) -> Dict:
        """Vincula participante a um projeto"""
        try:
            # Verifica se projeto existe
            if not self.projeto_dao.buscar_por_id(projeto_id):
                return helpers.create_response(False, "Projeto não encontrado")
            
            # Verifica se usuário existe e é participante
            usuario = self.usuario_dao.buscar_por_id(participante_id)
            if not usuario:
                return helpers.create_response(False, "Usuário não encontrado")
            
            if not usuario.is_participante():
                return helpers.create_response(False, "Usuário não é participante")
            
            # Vincula
            sucesso = self.projeto_dao.adicionar_participante(projeto_id, participante_id)
            
            if sucesso:
                logger.info(f"✅ Participante {participante_id} vinculado ao projeto {projeto_id}")
                return helpers.create_response(True, "Participante vinculado com sucesso")
            else:
                return helpers.create_response(False, "Erro ao vincular participante")
                
        except Exception as e:
            logger.error_trace(e, "vincular_participante_projeto")
            return helpers.create_response(False, "Erro ao vincular participante", error=str(e))
    
    def vincular_orientador_projeto(self, projeto_id: int, orientador_id: int) -> Dict:
        """Vincula orientador a um projeto"""
        try:
            # Verifica se projeto existe
            if not self.projeto_dao.buscar_por_id(projeto_id):
                return helpers.create_response(False, "Projeto não encontrado")
            
            # Verifica se usuário existe e é orientador
            usuario = self.usuario_dao.buscar_por_id(orientador_id)
            if not usuario:
                return helpers.create_response(False, "Usuário não encontrado")
            
            if not usuario.is_orientador():
                return helpers.create_response(False, "Usuário não é orientador")
            
            # Vincula
            sucesso = self.projeto_dao.adicionar_orientador(projeto_id, orientador_id)
            
            if sucesso:
                logger.info(f"✅ Orientador {orientador_id} vinculado ao projeto {projeto_id}")
                return helpers.create_response(True, "Orientador vinculado com sucesso")
            else:
                return helpers.create_response(False, "Erro ao vincular orientador")
                
        except Exception as e:
            logger.error_trace(e, "vincular_orientador_projeto")
            return helpers.create_response(False, "Erro ao vincular orientador", error=str(e))
    
    # ==================== RELATÓRIOS E ESTATÍSTICAS ====================
    
    def obter_relatorio_completo(self) -> Dict:
        """Retorna relatório completo do sistema"""
        try:
            # Contagem de usuários por tipo
            usuarios_total = 0
            usuarios_por_tipo = {}
            
            for tipo_nome in ['participante', 'orientador', 'admin']:
                tipo = self.tipo_usuario_dao.buscar_por_nome(tipo_nome)
                if tipo:
                    usuarios = self.usuario_dao.listar_por_tipo(tipo.id)
                    usuarios_por_tipo[tipo_nome] = len(usuarios)
                    usuarios_total += len(usuarios)
            
            # Contagem de projetos
            projetos = self.projeto_dao.listar_todos()
            total_projetos = len(projetos)
            
            # Contagem de chats
            total_chats = self.chat_dao.count()
            
            # Contagem de mensagens
            total_mensagens = self.mensagem_dao.count()
            
            # Status da API
            status_api = api_monitor.obter_relatorio()
            estatisticas_api = api_monitor.obter_estatisticas_periodo()
            
            # Status dos contextos
            contextos_info = context_service.obter_resumo_contextos()
            contextos_disponiveis = context_service.listar_contextos_disponiveis()
            
            relatorio = {
                'usuarios': {
                    'total': usuarios_total,
                    'por_tipo': usuarios_por_tipo
                },
                'projetos': {
                    'total': total_projetos
                },
                'chats': {
                    'total': total_chats
                },
                'mensagens': {
                    'total': total_mensagens
                },
                'api': {
                    'status': status_api,
                    'estatisticas': estatisticas_api
                },
                'contextos': {
                    'cache': contextos_info,
                    'disponiveis': len(contextos_disponiveis)
                },
                'sistema': {
                    'ativo': api_monitor.uso_atual['sistema_ativo'],
                    'throttling': api_monitor.uso_atual['throttling_ativo'],
                    'database_ok': db.health_check()
                }
            }
            
            return helpers.create_response(
                True,
                "Relatório gerado com sucesso",
                data=relatorio
            )
            
        except Exception as e:
            logger.error_trace(e, "obter_relatorio_completo")
            return helpers.create_response(False, "Erro ao gerar relatório", error=str(e))
    
    def obter_estatisticas_uso(self, periodo_dias: int = 30) -> Dict:
        """Retorna estatísticas de uso do sistema"""
        try:
            estatisticas = api_monitor.obter_estatisticas_periodo(periodo_dias)
            
            return helpers.create_response(
                True,
                "Estatísticas obtidas com sucesso",
                data=estatisticas
            )
            
        except Exception as e:
            logger.error_trace(e, "obter_estatisticas_uso")
            return helpers.create_response(False, "Erro ao obter estatísticas", error=str(e))
    
    # ==================== GERENCIAMENTO DO SISTEMA ====================
    
    def ativar_sistema(self) -> Dict:
        """Ativa o sistema"""
        try:
            api_monitor.ativar_sistema()
            return helpers.create_response(True, "Sistema ativado com sucesso")
        except Exception as e:
            return helpers.create_response(False, "Erro ao ativar sistema", error=str(e))
    
    def desativar_sistema(self, motivo: str = "Manutenção programada") -> Dict:
        """Desativa o sistema"""
        try:
            api_monitor.desativar_sistema(motivo)
            return helpers.create_response(True, f"Sistema desativado: {motivo}")
        except Exception as e:
            return helpers.create_response(False, "Erro ao desativar sistema", error=str(e))
    
    def resetar_contador_mensal(self) -> Dict:
        """Reseta contador mensal da API"""
        try:
            api_monitor.resetar_contador_mensal()
            return helpers.create_response(True, "Contador mensal resetado com sucesso")
        except Exception as e:
            return helpers.create_response(False, "Erro ao resetar contador", error=str(e))
    
    # ==================== GERENCIAMENTO DE CONTEXTOS ====================
    
    def listar_contextos(self) -> Dict:
        """Lista todos os contextos disponíveis"""
        try:
            contextos = context_service.listar_contextos_disponiveis()
            return helpers.create_response(
                True,
                f"{len(contextos)} contexto(s) disponível(is)",
                data=contextos
            )
        except Exception as e:
            return helpers.create_response(False, "Erro ao listar contextos", error=str(e))
    
    def recarregar_contextos(self) -> Dict:
        """Recarrega todos os contextos"""
        try:
            context_service.limpar_cache()
            sucesso, contextos, erro = context_service.carregar_todos_contextos()
            
            if sucesso:
                return helpers.create_response(
                    True,
                    f"{len(contextos)} contexto(s) recarregado(s)",
                    data={'total': len(contextos)}
                )
            else:
                return helpers.create_response(False, "Erro ao recarregar contextos", error=erro)
                
        except Exception as e:
            return helpers.create_response(False, "Erro ao recarregar contextos", error=str(e))


# Instância global
admin_controller = AdminController()