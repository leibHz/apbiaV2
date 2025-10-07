"""
Model de Usuário
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from utils.helpers import helpers


@dataclass
class Usuario:
    """Classe que representa um usuário do sistema"""
    
    id: Optional[int] = None
    nome_completo: str = ""
    email: str = ""
    senha_hash: Optional[str] = None
    tipo_usuario_id: int = 0
    bp: Optional[str] = None
    data_criacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    
    # Campos extras (não persistidos)
    tipo_usuario_nome: Optional[str] = None
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Converte para dicionário"""
        data = {
            "id": self.id,
            "nome_completo": self.nome_completo,
            "email": self.email,
            "tipo_usuario_id": self.tipo_usuario_id,
            "bp": self.bp,
            "data_criacao": self._format_datetime(self.data_criacao),
            "data_atualizacao": self._format_datetime(self.data_atualizacao)
        }
        
        if self.tipo_usuario_nome:
            data["tipo_usuario_nome"] = self.tipo_usuario_nome
        
        if include_sensitive and self.senha_hash:
            data["senha_hash"] = self.senha_hash
        
        return data
    
    def _format_datetime(self, dt) -> Optional[str]:
        """Formata datetime para string ISO"""
        if dt is None:
            return None
        
        # Se já é string, retorna como está
        if isinstance(dt, str):
            return dt
        
        # Se é datetime, converte para ISO
        if isinstance(dt, datetime):
            return dt.isoformat()
        
        return None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Usuario':
        """Cria instância a partir de dicionário"""
        return cls(
            id=data.get("id"),
            nome_completo=data.get("nome_completo", ""),
            email=data.get("email", ""),
            senha_hash=data.get("senha_hash"),
            tipo_usuario_id=data.get("tipo_usuario_id", 0),
            bp=data.get("bp"),
            data_criacao=data.get("data_criacao"),
            data_atualizacao=data.get("data_atualizacao"),
            tipo_usuario_nome=data.get("tipo_usuario_nome")
        )
    
    def is_participante(self) -> bool:
        """Verifica se é participante"""
        return self.tipo_usuario_nome == "participante" if self.tipo_usuario_nome else False
    
    def is_orientador(self) -> bool:
        """Verifica se é orientador"""
        return self.tipo_usuario_nome == "orientador" if self.tipo_usuario_nome else False
    
    def is_admin(self) -> bool:
        """Verifica se é administrador"""
        return self.tipo_usuario_nome == "admin" if self.tipo_usuario_nome else False


@dataclass
class TipoUsuario:
    """Classe que representa um tipo de usuário"""
    
    id: Optional[int] = None
    nome: str = ""
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "nome": self.nome
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TipoUsuario':
        """Cria instância a partir de dicionário"""
        return cls(
            id=data.get("id"),
            nome=data.get("nome", "")
        )