"""
Controller para gerenciar chats
"""
from typing import Dict, Optional
from dao.chat_dao import ChatDAO, TipoIADAO
from dao.mensagem_dao import MensagemDAO
from dao.projeto_dao import ProjetoDAO
from models.chat import Chat
from utils.logger import logger
from utils.helpers import helpers


class ChatController:
    """Controller para gerenciar chats"""
    
    def __init__(self):
        self.chat_dao = ChatDAO()
        self.mensagem_dao = MensagemDAO()
        self.tipo_ia_dao = TipoIADAO()
        self.projeto_dao = ProjetoDAO()
    
    def criar_chat(self, projeto_id: int, tipo_ia_nome: str, titulo: str) -> Dict:
        """
        Cria um novo chat
        
        Args:
            projeto_id: ID do projeto
            tipo_ia_nome: Nome do tipo de IA
            titulo: Título do chat
        
        Returns:
            Dict com resultado da operação
        """
        try:
            # Verifica se projeto existe
            projeto = self.projeto_dao.buscar_por_id(projeto_id)
            if not projeto:
                return helpers.create_response(False, "Projeto não encontrado", error="Project not found")
            
            # Busca tipo de IA
            tipo_ia = self.tipo_ia_dao.buscar_por_nome(tipo_ia_nome)
            if not tipo_ia:
                return helpers.create_response(False, "Tipo de IA não encontrado", error="AI type not found")
            
            # Cria chat
            chat = Chat(
                projeto_id=projeto_id,
                tipo_ia_id=tipo_ia.id,
                titulo=titulo or f"Chat - {projeto.nome}"
            )
            
            chat_criado = self.chat_dao.criar_chat(chat)
            
            if chat_criado:
                logger.info(f"✅ Chat criado: ID {chat_criado.id} - Projeto {projeto_id}")
                return helpers.create_response(
                    True,
                    "Chat criado com sucesso",
                    data=chat_criado.to_dict()
                )
            else:
                return helpers.create_response(False, "Erro ao criar chat", error="Database error")
            
        except Exception as e:
            logger.error_trace(e, "criar_chat")
            return helpers.create_response(False, "Erro ao criar chat", error=str(e))
    
    def buscar_chat(self, chat_id: int, incluir_mensagens: bool = True) -> Dict:
        """
        Busca chat por ID
        
        Args:
            chat_id: ID do chat
            incluir_mensagens: Se deve incluir mensagens
        
        Returns:
            Dict com resultado da operação
        """
        try:
            chat = self.chat_dao.buscar_por_id(chat_id)
            
            if not chat:
                return helpers.create_response(False, "Chat não encontrado", error="Chat not found")
            
            chat_dict = chat.to_dict()
            
            # Inclui mensagens se solicitado
            if incluir_mensagens:
                mensagens = self.mensagem_dao.listar_por_chat(chat_id)
                chat_dict['mensagens'] = [msg.to_dict() for msg in mensagens]
                chat_dict['total_mensagens'] = len(mensagens)
            
            return helpers.create_response(
                True,
                "Chat encontrado",
                data=chat_dict
            )
            
        except Exception as e:
            logger.error_trace(e, "buscar_chat")
            return helpers.create_response(False, "Erro ao buscar chat", error=str(e))
    
    def listar_chats_projeto(self, projeto_id: int) -> Dict:
        """
        Lista todos os chats de um projeto
        
        Args:
            projeto_id: ID do projeto
        
        Returns:
            Dict com resultado da operação
        """
        try:
            chats = self.chat_dao.listar_por_projeto(projeto_id)
            
            # Adiciona contagem de mensagens a cada chat
            chats_com_info = []
            for chat in chats:
                chat_dict = chat.to_dict()
                chat_dict['total_mensagens'] = self.mensagem_dao.contar_mensagens_chat(chat.id)
                chats_com_info.append(chat_dict)
            
            return helpers.create_response(
                True,
                f"{len(chats)} chat(s) encontrado(s)",
                data=chats_com_info
            )
            
        except Exception as e:
            logger.error_trace(e, "listar_chats_projeto")
            return helpers.create_response(False, "Erro ao listar chats", error=str(e))
    
    def atualizar_titulo_chat(self, chat_id: int, novo_titulo: str) -> Dict:
        """
        Atualiza título do chat
        
        Args:
            chat_id: ID do chat
            novo_titulo: Novo título
        
        Returns:
            Dict com resultado da operação
        """
        try:
            if not novo_titulo or len(novo_titulo.strip()) == 0:
                return helpers.create_response(False, "Título não pode ser vazio", error="Empty title")
            
            chat_atualizado = self.chat_dao.atualizar_titulo(chat_id, novo_titulo)
            
            if chat_atualizado:
                logger.info(f"✅ Título do chat {chat_id} atualizado")
                return helpers.create_response(
                    True,
                    "Título atualizado com sucesso",
                    data=chat_atualizado.to_dict()
                )
            else:
                return helpers.create_response(False, "Erro ao atualizar título", error="Database error")
            
        except Exception as e:
            logger.error_trace(e, "atualizar_titulo_chat")
            return helpers.create_response(False, "Erro ao atualizar título", error=str(e))
    
    def deletar_chat(self, chat_id: int) -> Dict:
        """
        Deleta um chat e todas suas mensagens
        
        Args:
            chat_id: ID do chat
        
        Returns:
            Dict com resultado da operação
        """
        try:
            # Verifica se chat existe
            chat = self.chat_dao.buscar_por_id(chat_id)
            if not chat:
                return helpers.create_response(False, "Chat não encontrado", error="Chat not found")
            
            # Deleta chat (cascade deleta mensagens)
            sucesso = self.chat_dao.deletar_chat(chat_id)
            
            if sucesso:
                logger.info(f"✅ Chat {chat_id} deletado")
                return helpers.create_response(True, "Chat deletado com sucesso")
            else:
                return helpers.create_response(False, "Erro ao deletar chat", error="Database error")
            
        except Exception as e:
            logger.error_trace(e, "deletar_chat")
            return helpers.create_response(False, "Erro ao deletar chat", error=str(e))
    
    def listar_mensagens_chat(self, chat_id: int, limit: int = 100) -> Dict:
        """
        Lista mensagens de um chat
        
        Args:
            chat_id: ID do chat
            limit: Limite de mensagens
        
        Returns:
            Dict com resultado da operação
        """
        try:
            mensagens = self.mensagem_dao.listar_por_chat(chat_id, limit)
            
            return helpers.create_response(
                True,
                f"{len(mensagens)} mensagem(ns) encontrada(s)",
                data=[msg.to_dict() for msg in mensagens]
            )
            
        except Exception as e:
            logger.error_trace(e, "listar_mensagens_chat")
            return helpers.create_response(False, "Erro ao listar mensagens", error=str(e))
    
    def listar_notas_orientador(self, chat_id: int) -> Dict:
        """
        Lista apenas notas do orientador em um chat
        
        Args:
            chat_id: ID do chat
        
        Returns:
            Dict com resultado da operação
        """
        try:
            notas = self.mensagem_dao.listar_notas_orientador(chat_id)
            
            return helpers.create_response(
                True,
                f"{len(notas)} nota(s) encontrada(s)",
                data=[nota.to_dict() for nota in notas]
            )
            
        except Exception as e:
            logger.error_trace(e, "listar_notas_orientador")
            return helpers.create_response(False, "Erro ao listar notas", error=str(e))
    
    def listar_tipos_ia(self) -> Dict:
        """Lista todos os tipos de IA disponíveis"""
        try:
            tipos = self.tipo_ia_dao.listar_todos()
            
            return helpers.create_response(
                True,
                f"{len(tipos)} tipo(s) de IA disponível(is)",
                data=[tipo.to_dict() for tipo in tipos]
            )
            
        except Exception as e:
            logger.error_trace(e, "listar_tipos_ia")
            return helpers.create_response(False, "Erro ao listar tipos de IA", error=str(e))


# Instância global
chat_controller = ChatController()