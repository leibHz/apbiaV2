"""
Model de Arquivo
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Arquivo:
    """Classe que representa um arquivo anexado a uma mensagem"""
    
    id: Optional[int] = None
    mensagem_id: int = 0
    nome_arquivo: str = ""
    url_arquivo: str = ""
    tipo_arquivo: Optional[str] = None
    tamanho_bytes: Optional[int] = None
    data_upload: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "mensagem_id": self.mensagem_id,
            "nome_arquivo": self.nome_arquivo,
            "url_arquivo": self.url_arquivo,
            "tipo_arquivo": self.tipo_arquivo,
            "tamanho_bytes": self.tamanho_bytes,
            "data_upload": self._format_datetime(self.data_upload)
        }
    
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
    def from_dict(cls, data: dict) -> 'Arquivo':
        """Cria instância a partir de dicionário"""
        return cls(
            id=data.get("id"),
            mensagem_id=data.get("mensagem_id", 0),
            nome_arquivo=data.get("nome_arquivo", ""),
            url_arquivo=data.get("url_arquivo", ""),
            tipo_arquivo=data.get("tipo_arquivo"),
            tamanho_bytes=data.get("tamanho_bytes"),
            data_upload=data.get("data_upload")
        )
    
    def get_extension(self) -> str:
        """Retorna a extensão do arquivo"""
        from pathlib import Path
        return Path(self.nome_arquivo).suffix.lower()
    
    def is_text_file(self) -> bool:
        """Verifica se é arquivo de texto"""
        text_extensions = {'.txt', '.md', '.csv'}
        return self.get_extension() in text_extensions