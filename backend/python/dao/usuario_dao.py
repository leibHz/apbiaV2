"""
DAO de Usuário
"""
from typing import Optional, List
from dao.base_dao import BaseDAO
from models.usuario import Usuario, TipoUsuario
from utils.logger import logger


class UsuarioDAO(BaseDAO):
    """DAO para gerenciar usuários"""
    
    def __init__(self):
        super().__init__("usuarios")
    
    def criar_usuario(self, usuario: Usuario) -> Optional[Usuario]:
        """Cria um novo usuário"""
        data = {
            "nome_completo": usuario.nome_completo,
            "email": usuario.email,
            "senha_hash": usuario.senha_hash,
            "tipo_usuario_id": usuario.tipo_usuario_id,
            "bp": usuario.bp
        }
        
        result = self.create(data)
        if result:
            return Usuario.from_dict(result)
        return None
    
    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        """Busca usuário por email"""
        result = self.find_one_by_field("email", email)
        if result:
            return self._enrich_usuario(Usuario.from_dict(result))
        return None
    
    def buscar_por_bp(self, bp: str) -> Optional[Usuario]:
        """Busca usuário por BP"""
        result = self.find_one_by_field("bp", bp)
        if result:
            return self._enrich_usuario(Usuario.from_dict(result))
        return None
    
    def buscar_por_id(self, id: int) -> Optional[Usuario]:
        """Busca usuário por ID"""
        result = self.find_by_id(id)
        if result:
            return self._enrich_usuario(Usuario.from_dict(result))
        return None
    
    def listar_por_tipo(self, tipo_usuario_id: int) -> List[Usuario]:
        """Lista usuários por tipo"""
        results = self.find_by_field("tipo_usuario_id", tipo_usuario_id)
        return [self._enrich_usuario(Usuario.from_dict(r)) for r in results]
    
    def atualizar_usuario(self, usuario: Usuario) -> Optional[Usuario]:
        """Atualiza dados do usuário"""
        data = {
            "nome_completo": usuario.nome_completo,
            "email": usuario.email,
            "data_atualizacao": "now()"
        }
        
        if usuario.senha_hash:
            data["senha_hash"] = usuario.senha_hash
        
        if usuario.bp:
            data["bp"] = usuario.bp
        
        result = self.update(usuario.id, data)
        if result:
            return Usuario.from_dict(result)
        return None
    
    def _enrich_usuario(self, usuario: Usuario) -> Usuario:
        """Enriquece usuário com informações do tipo"""
        tipo_dao = TipoUsuarioDAO()
        tipo = tipo_dao.buscar_por_id(usuario.tipo_usuario_id)
        if tipo:
            usuario.tipo_usuario_nome = tipo.nome
        return usuario
    
    def email_existe(self, email: str) -> bool:
        """Verifica se email já existe"""
        return self.exists("email", email)
    
    def bp_existe(self, bp: str) -> bool:
        """Verifica se BP já existe"""
        return self.exists("bp", bp)


class TipoUsuarioDAO(BaseDAO):
    """DAO para gerenciar tipos de usuário"""
    
    def __init__(self):
        super().__init__("tipos_usuario")
    
    def buscar_por_nome(self, nome: str) -> Optional[TipoUsuario]:
        """Busca tipo por nome"""
        result = self.find_one_by_field("nome", nome)
        if result:
            return TipoUsuario.from_dict(result)
        return None
    
    def buscar_por_id(self, id: int) -> Optional[TipoUsuario]:
        """Busca tipo por ID"""
        result = self.find_by_id(id)
        if result:
            return TipoUsuario.from_dict(result)
        return None
    
    def listar_todos(self) -> List[TipoUsuario]:
        """Lista todos os tipos"""
        results = self.find_all()
        return [TipoUsuario.from_dict(r) for r in results]