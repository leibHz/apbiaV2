"""
Serviço de Autenticação
"""
from typing import Optional, Tuple, Dict
from dao.usuario_dao import UsuarioDAO, TipoUsuarioDAO
from models.usuario import Usuario
from utils.helpers import helpers
from utils.validators import validators
from utils.logger import logger


class AuthService:
    """Serviço de autenticação e autorização"""
    
    def __init__(self):
        self.usuario_dao = UsuarioDAO()
        self.tipo_usuario_dao = TipoUsuarioDAO()
    
    def login(self, email: str, senha: str, bp: Optional[str] = None) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Realiza login do usuário
        
        Returns:
            Tuple[success, user_data_with_token, error_message]
        """
        try:
            # Valida email
            if not validators.validate_email(email):
                return False, None, "Email inválido"
            
            # Busca usuário por email
            usuario = self.usuario_dao.buscar_por_email(email)
            
            if not usuario:
                return False, None, "Usuário não encontrado"
            
            # Verifica senha
            if not usuario.senha_hash:
                return False, None, "Senha não configurada. Entre em contato com o administrador"
            
            if not helpers.verify_password(senha, usuario.senha_hash):
                logger.warning(f"Tentativa de login falhou para: {email}")
                return False, None, "Senha incorreta"
            
            # Verifica BP se o usuário for participante
            if usuario.is_participante():
                if not bp:
                    return False, None, "BP (prontuário) é obrigatório para participantes"
                
                if not validators.validate_bp(bp):
                    return False, None, "BP inválido"
                
                if usuario.bp != bp.upper():
                    return False, None, "BP não corresponde ao usuário"
            
            # Gera token JWT
            token = helpers.generate_token(usuario.id, usuario.tipo_usuario_nome)
            
            # Prepara dados de resposta
            user_data = usuario.to_dict()
            user_data['token'] = token
            
            logger.info(f"✅ Login bem-sucedido: {email}")
            return True, user_data, None
            
        except Exception as e:
            error_msg = f"Erro ao realizar login: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
    
    def validar_token(self, token: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Valida token JWT
        
        Returns:
            Tuple[success, payload, error_message]
        """
        try:
            payload = helpers.decode_token(token)
            
            if not payload:
                return False, None, "Token inválido ou expirado"
            
            # Verifica se usuário ainda existe
            usuario = self.usuario_dao.buscar_por_id(payload['user_id'])
            if not usuario:
                return False, None, "Usuário não encontrado"
            
            return True, payload, None
            
        except Exception as e:
            error_msg = f"Erro ao validar token: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
    
    def cadastrar_usuario(self, nome_completo: str, email: str, senha: str, 
                         tipo_usuario_nome: str, bp: Optional[str] = None) -> Tuple[bool, Optional[Usuario], Optional[str]]:
        """
        Cadastra novo usuário (apenas admin pode fazer isso)
        
        Returns:
            Tuple[success, usuario, error_message]
        """
        try:
            # Valida email
            if not validators.validate_email(email):
                return False, None, "Email inválido"
            
            # Verifica se email já existe
            if self.usuario_dao.email_existe(email):
                return False, None, "Email já cadastrado"
            
            # Valida senha
            senha_valida, erro_senha = validators.validate_senha(senha)
            if not senha_valida:
                return False, None, erro_senha
            
            # Valida tipo de usuário
            if not validators.validate_tipo_usuario(tipo_usuario_nome):
                return False, None, "Tipo de usuário inválido"
            
            # Busca tipo de usuário
            tipo_usuario = self.tipo_usuario_dao.buscar_por_nome(tipo_usuario_nome.lower())
            if not tipo_usuario:
                return False, None, "Tipo de usuário não encontrado"
            
            # Valida BP se for participante
            if tipo_usuario_nome.lower() == "participante":
                if not bp:
                    return False, None, "BP é obrigatório para participantes"
                
                if not validators.validate_bp(bp):
                    return False, None, "BP inválido. Formato: BRGxxxxxxxx"
                
                if self.usuario_dao.bp_existe(bp.upper()):
                    return False, None, "BP já cadastrado"
            
            # Hash da senha
            senha_hash = helpers.hash_password(senha)
            
            # Cria usuário
            usuario = Usuario(
                nome_completo=nome_completo,
                email=email,
                senha_hash=senha_hash,
                tipo_usuario_id=tipo_usuario.id,
                bp=bp.upper() if bp else None
            )
            
            usuario_criado = self.usuario_dao.criar_usuario(usuario)
            
            if usuario_criado:
                logger.info(f"✅ Usuário cadastrado: {email}")
                return True, usuario_criado, None
            else:
                return False, None, "Erro ao criar usuário"
            
        except Exception as e:
            error_msg = f"Erro ao cadastrar usuário: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
    
    def alterar_senha(self, usuario_id: int, senha_atual: str, nova_senha: str) -> Tuple[bool, Optional[str]]:
        """
        Altera senha do usuário
        
        Returns:
            Tuple[success, error_message]
        """
        try:
            # Busca usuário
            usuario = self.usuario_dao.buscar_por_id(usuario_id)
            if not usuario:
                return False, "Usuário não encontrado"
            
            # Verifica senha atual
            if not helpers.verify_password(senha_atual, usuario.senha_hash):
                return False, "Senha atual incorreta"
            
            # Valida nova senha
            senha_valida, erro_senha = validators.validate_senha(nova_senha)
            if not senha_valida:
                return False, erro_senha
            
            # Hash da nova senha
            nova_senha_hash = helpers.hash_password(nova_senha)
            
            # Atualiza senha
            usuario.senha_hash = nova_senha_hash
            self.usuario_dao.atualizar_usuario(usuario)
            
            logger.info(f"✅ Senha alterada para usuário ID: {usuario_id}")
            return True, None
            
        except Exception as e:
            error_msg = f"Erro ao alterar senha: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def verificar_permissao(self, usuario_id: int, tipo_requerido: str) -> bool:
        """Verifica se usuário tem permissão necessária"""
        try:
            usuario = self.usuario_dao.buscar_por_id(usuario_id)
            if not usuario:
                return False
            
            # Admin tem acesso a tudo
            if usuario.is_admin():
                return True
            
            # Verifica permissão específica
            return usuario.tipo_usuario_nome == tipo_requerido
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar permissão: {e}")
            return False


# Instância global
auth_service = AuthService()