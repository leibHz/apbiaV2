"""
DAO de Arquivo
"""
from typing import Optional, List
from dao.base_dao import BaseDAO
from models.arquivo import Arquivo
from utils.logger import logger


class ArquivoDAO(BaseDAO):
    """DAO para gerenciar arquivos"""
    
    def __init__(self):
        super().__init__("arquivos_chat")
    
    def criar_arquivo(self, arquivo: Arquivo) -> Optional[Arquivo]:
        """Registra um novo arquivo"""
        data = {
            "mensagem_id": arquivo.mensagem_id,
            "nome_arquivo": arquivo.nome_arquivo,
            "url_arquivo": arquivo.url_arquivo,
            "tipo_arquivo": arquivo.tipo_arquivo,
            "tamanho_bytes": arquivo.tamanho_bytes
        }
        
        result = self.create(data)
        if result:
            return Arquivo.from_dict(result)
        return None
    
    def buscar_por_id(self, id: int) -> Optional[Arquivo]:
        """Busca arquivo por ID"""
        result = self.find_by_id(id)
        if result:
            return Arquivo.from_dict(result)
        return None
    
    def listar_por_mensagem(self, mensagem_id: int) -> List[Arquivo]:
        """Lista arquivos de uma mensagem"""
        results = self.find_by_field("mensagem_id", mensagem_id)
        return [Arquivo.from_dict(r) for r in results]
    
    def listar_por_tipo(self, tipo_arquivo: str) -> List[Arquivo]:
        """Lista arquivos por tipo"""
        results = self.find_by_field("tipo_arquivo", tipo_arquivo)
        return [Arquivo.from_dict(r) for r in results]
    
    def deletar_arquivo(self, arquivo_id: int) -> bool:
        """Deleta registro de arquivo"""
        return self.delete(arquivo_id)
    
    def contar_por_mensagem(self, mensagem_id: int) -> int:
        """Conta arquivos de uma mensagem"""
        try:
            result = self.table.select("id", count="exact").eq("mensagem_id", mensagem_id).execute()
            return result.count if result.count else 0
        except Exception as e:
            logger.error(f"Erro ao contar arquivos: {e}")
            return 0
    
    def buscar_por_nome(self, nome_arquivo: str) -> List[Arquivo]:
        """Busca arquivos por nome"""
        try:
            result = self.table.select("*").ilike("nome_arquivo", f"%{nome_arquivo}%").execute()
            return [Arquivo.from_dict(r) for r in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Erro ao buscar arquivos por nome: {e}")
            return []