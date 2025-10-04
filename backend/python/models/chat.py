"""
Model de Chat
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Chat:
    """Classe que representa um chat"""
    
    id: Optional[int] = None
    projeto_id: int = 0
    tipo_ia_id: int = 0
    titulo: str = ""
    data_criacao: Optional[datetime] = None
    
    # Campos extras (não persistidos)
    tipo_ia_nome: Optional[str] = None
    projeto_nome: Optional[str] = None
    mensagens: Optional[List[dict]] = None
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        data = {
            "id": self.id,
            "projeto_id": self.projeto_id,
            "tipo_ia_id": self.tipo_ia_id,
            "titulo": self.titulo,
            "data_criacao": self.data_criacao.isoformat() if self.data_criacao else None
        }
        
        if self.tipo_ia_nome:
            data["tipo_ia_nome"] = self.tipo_ia_nome
        
        if self.projeto_nome:
            data["projeto_nome"] = self.projeto_nome
        
        if self.mensagens:
            data["mensagens"] = self.mensagens
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Chat':
        """Cria instância a partir de dicionário"""
        return cls(
            id=data.get("id"),
            projeto_id=data.get("projeto_id", 0),
            tipo_ia_id=data.get("tipo_ia_id", 0),
            titulo=data.get("titulo", ""),
            data_criacao=data.get("data_criacao"),
            tipo_ia_nome=data.get("tipo_ia_nome"),
            projeto_nome=data.get("projeto_nome"),
            mensagens=data.get("mensagens")
        )


@dataclass
class TipoIA:
    """Classe que representa um tipo de IA"""
    
    id: Optional[int] = None
    nome: str = ""
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "nome": self.nome
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TipoIA':
        """Cria instância a partir de dicionário"""
        return cls(
            id=data.get("id"),
            nome=data.get("nome", "")
        )