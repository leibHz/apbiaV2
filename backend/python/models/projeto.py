"""
Model de Projeto
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Projeto:
    """Classe que representa um projeto da Bragantec"""
    
    id: Optional[int] = None
    nome: str = ""
    descricao: Optional[str] = None
    area_projeto: str = ""
    ano_edicao: int = 0
    data_criacao: Optional[datetime] = None
    
    # Campos extras (não persistidos)
    participantes: Optional[List[dict]] = None
    orientadores: Optional[List[dict]] = None
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        data = {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "area_projeto": self.area_projeto,
            "ano_edicao": self.ano_edicao,
            "data_criacao": self.data_criacao.isoformat() if self.data_criacao else None
        }
        
        if self.participantes:
            data["participantes"] = self.participantes
        
        if self.orientadores:
            data["orientadores"] = self.orientadores
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Projeto':
        """Cria instância a partir de dicionário"""
        return cls(
            id=data.get("id"),
            nome=data.get("nome", ""),
            descricao=data.get("descricao"),
            area_projeto=data.get("area_projeto", ""),
            ano_edicao=data.get("ano_edicao", 0),
            data_criacao=data.get("data_criacao"),
            participantes=data.get("participantes"),
            orientadores=data.get("orientadores")
        )