"""
DAO de Chat
"""
from typing import Optional, List
from dao.base_dao import BaseDAO
from models.chat import Chat, TipoIA
from utils.logger import logger


class ChatDAO(BaseDAO):
    """DAO para gerenciar chats"""
    
    def __init__(self):
        super().__init__("chats")
    
    def criar_chat(self, chat: Chat) -> Optional[Chat]:
        """Cria um novo chat"""
        data = {
            "projeto_id": chat.projeto_id,
            "tipo_ia_id": chat.tipo_ia_id,
            "titulo": chat.titulo
        }
        
        result = self.create(data)
        if result:
            return Chat.from_dict(result)
        return None
    
    def buscar_por_id(self, id: int) -> Optional[Chat]:
        """Busca chat por ID"""
        result = self.find_by_id(id)
        if result:
            chat = Chat.from_dict(result)
            return self._enrich_chat(chat)
        return None
    
    def listar_por_projeto(self, projeto_id: int) -> List[Chat]:
        """Lista chats de um projeto"""
        results = self.find_by_field("projeto_id", projeto_id)
        return [self._enrich_chat(Chat.from_dict(r)) for r in results]
    
    def listar_por_tipo_ia(self, tipo_ia_id: int) -> List[Chat]:
        """Lista chats por tipo de IA"""
        results = self.find_by_field("tipo_ia_id", tipo_ia_id)
        return [self._enrich_chat(Chat.from_dict(r)) for r in results]
    
    def atualizar_titulo(self, chat_id: int, novo_titulo: str) -> Optional[Chat]:
        """Atualiza título do chat"""
        result = self.update(chat_id, {"titulo": novo_titulo})
        if result:
            return Chat.from_dict(result)
        return None
    
    def _enrich_chat(self, chat: Chat) -> Chat:
        """Enriquece chat com informações adicionais"""
        # Busca tipo de IA
        tipo_ia_dao = TipoIADAO()
        tipo_ia = tipo_ia_dao.buscar_por_id(chat.tipo_ia_id)
        if tipo_ia:
            chat.tipo_ia_nome = tipo_ia.nome
        
        return chat
    
    def deletar_chat(self, chat_id: int) -> bool:
        """Deleta um chat e suas mensagens"""
        return self.delete(chat_id)


class TipoIADAO(BaseDAO):
    """DAO para gerenciar tipos de IA"""
    
    def __init__(self):
        super().__init__("tipos_ia")
    
    def buscar_por_nome(self, nome: str) -> Optional[TipoIA]:
        """Busca tipo de IA por nome"""
        result = self.find_one_by_field("nome", nome)
        if result:
            return TipoIA.from_dict(result)
        return None
    
    def buscar_por_id(self, id: int) -> Optional[TipoIA]:
        """Busca tipo de IA por ID"""
        result = self.find_by_id(id)
        if result:
            return TipoIA.from_dict(result)
        return None
    
    def listar_todos(self) -> List[TipoIA]:
        """Lista todos os tipos de IA"""
        results = self.find_all()
        return [TipoIA.from_dict(r) for r in results]