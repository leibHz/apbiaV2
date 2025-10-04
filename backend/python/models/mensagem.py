"""
Model de Mensagem
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Mensagem:
    """Classe que representa uma mensagem"""
    
    id: Optional[int] = None
    chat_id: int = 0
    usuario_id: Optional[int] = None
    conteudo: str = ""
    e_nota_orientador: bool = False
    data_envio: Optional[datetime] = None
    
    # Campos extras (não persistidos)
    usuario_nome: Optional[str] = None
    arquivos: Optional[List[dict]] = None
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        data = {
            "id": self.id,
            "chat_id": self.chat_id,
            "usuario_id": self.usuario_id,
            "conteudo": self.conteudo,
            "e_nota_orientador": self.e_nota_orientador,
            "data_envio": self.data_envio.isoformat() if self.data_envio else None
        }
        
        if self.usuario_nome:
            data["usuario_nome"] = self.usuario_nome
        
        if self.arquivos:
            data["arquivos"] = self.arquivos
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Mensagem':
        """Cria instância a partir de dicionário"""
        return cls(
            id=data.get("id"),
            chat_id=data.get("chat_id", 0),
            usuario_id=data.get("usuario_id"),
            conteudo=data.get("conteudo", ""),
            e_nota_orientador=data.get("e_nota_orientador", False),
            data_envio=data.get("data_envio"),
            usuario_nome=data.get("usuario_nome"),
            arquivos=data.get("arquivos")
        )
    
    def is_from_ia(self) -> bool:
        """Verifica se a mensagem é da IA"""
        return self.usuario_id is None