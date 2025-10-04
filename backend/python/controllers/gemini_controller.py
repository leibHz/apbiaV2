"""
Controller para gerenciar interações com o Gemini AI
"""
from typing import Dict, Optional
from services.gemini_service import gemini_service
from services.context_service import context_service
from services.api_monitor_service import api_monitor
from dao.mensagem_dao import MensagemDAO
from dao.chat_dao import ChatDAO
from models.mensagem import Mensagem
from utils.logger import logger
from utils.helpers import helpers


class GeminiController:
    """Controller para interações com IA"""
    
    def __init__(self):
        self.mensagem_dao = MensagemDAO()
        self.chat_dao = ChatDAO()
    
    def processar_mensagem(self, chat_id: int, usuario_id: int, conteudo: str, 
                          usar_thinking: bool = False) -> Dict:
        """
        Processa mensagem do usuário e gera resposta da IA
        
        Args:
            chat_id: ID do chat
            usuario_id: ID do usuário
            conteudo: Mensagem do usuário
            usar_thinking: Se deve usar thinking mode
        
        Returns:
            Dict com resultado da operação
        """
        try:
            # Verifica rate limit
            pode_fazer, erro_rate = api_monitor.verificar_rate_limit()
            if not pode_fazer:
                return helpers.create_response(False, erro_rate, error=erro_rate)
            
            # Salva mensagem do usuário
            mensagem_usuario = Mensagem(
                chat_id=chat_id,
                usuario_id=usuario_id,
                conteudo=conteudo,
                e_nota_orientador=False
            )
            
            msg_salva = self.mensagem_dao.criar_mensagem(mensagem_usuario)
            if not msg_salva:
                return helpers.create_response(False, "Erro ao salvar mensagem", error="Database error")
            
            # Busca chat para contexto
            chat = self.chat_dao.buscar_por_id(chat_id)
            if not chat:
                return helpers.create_response(False, "Chat não encontrado", error="Chat not found")
            
            # Carrega contextos da Bragantec
            sucesso_ctx, contextos, erro_ctx = context_service.carregar_todos_contextos()
            if not sucesso_ctx:
                logger.warning(f"⚠️  Continuando sem contextos: {erro_ctx}")
                contextos = []
            
            # Busca histórico do chat
            historico = self.mensagem_dao.listar_por_chat(chat_id, limit=20)
            historico_formatado = [msg.to_dict() for msg in historico[:-1]]  # Exclui última (a que acabamos de salvar)
            
            # Gera resposta da IA
            if usar_thinking:
                sucesso_ia, resposta_ia, erro_ia = gemini_service.gerar_resposta_com_thinking(
                    conteudo, contextos
                )
            else:
                sucesso_ia, resposta_ia, erro_ia = gemini_service.gerar_resposta(
                    conteudo, contextos, historico_formatado
                )
            
            if not sucesso_ia:
                return helpers.create_response(
                    False, 
                    "Erro ao gerar resposta da IA", 
                    error=erro_ia
                )
            
            # Salva resposta da IA
            mensagem_ia = Mensagem(
                chat_id=chat_id,
                usuario_id=None,  # None indica que é da IA
                conteudo=resposta_ia,
                e_nota_orientador=False
            )
            
            msg_ia_salva = self.mensagem_dao.criar_mensagem(mensagem_ia)
            
            # Registra uso da API
            api_monitor.registrar_requisicao(
                tokens=len(conteudo + resposta_ia) // 4  # Estimativa
            )
            
            # Retorna resultado
            return helpers.create_response(
                True,
                "Resposta gerada com sucesso",
                data={
                    "mensagem_usuario": msg_salva.to_dict(),
                    "mensagem_ia": msg_ia_salva.to_dict() if msg_ia_salva else None,
                    "uso_api": api_monitor.obter_relatorio()
                }
            )
            
        except Exception as e:
            logger.error_trace(e, "processar_mensagem")
            return helpers.create_response(
                False,
                "Erro ao processar mensagem",
                error=str(e)
            )
    
    def adicionar_nota_orientador(self, mensagem_id: int, usuario_id: int, 
                                  nota: str) -> Dict:
        """
        Adiciona nota do orientador a uma resposta da IA
        
        Args:
            mensagem_id: ID da mensagem da IA
            usuario_id: ID do orientador
            nota: Conteúdo da nota
        
        Returns:
            Dict com resultado da operação
        """
        try:
            # Busca mensagem original
            mensagem_original = self.mensagem_dao.buscar_por_id(mensagem_id)
            if not mensagem_original:
                return helpers.create_response(False, "Mensagem não encontrada", error="Message not found")
            
            # Cria mensagem de nota
            mensagem_nota = Mensagem(
                chat_id=mensagem_original.chat_id,
                usuario_id=usuario_id,
                conteudo=f"📝 NOTA DO ORIENTADOR:\n{nota}",
                e_nota_orientador=True
            )
            
            nota_salva = self.mensagem_dao.criar_mensagem(mensagem_nota)
            
            if nota_salva:
                logger.info(f"✅ Nota do orientador adicionada por usuário {usuario_id}")
                return helpers.create_response(
                    True,
                    "Nota adicionada com sucesso",
                    data=nota_salva.to_dict()
                )
            else:
                return helpers.create_response(False, "Erro ao salvar nota", error="Database error")
            
        except Exception as e:
            logger.error_trace(e, "adicionar_nota_orientador")
            return helpers.create_response(False, "Erro ao adicionar nota", error=str(e))
    
    def regenerar_resposta(self, chat_id: int, mensagem_id: int) -> Dict:
        """
        Regenera resposta da IA para uma mensagem
        
        Args:
            chat_id: ID do chat
            mensagem_id: ID da mensagem do usuário
        
        Returns:
            Dict com resultado da operação
        """
        try:
            # Verifica rate limit
            pode_fazer, erro_rate = api_monitor.verificar_rate_limit()
            if not pode_fazer:
                return helpers.create_response(False, erro_rate, error=erro_rate)
            
            # Busca mensagem original
            mensagem = self.mensagem_dao.buscar_por_id(mensagem_id)
            if not mensagem or mensagem.is_from_ia():
                return helpers.create_response(False, "Mensagem inválida", error="Invalid message")
            
            # Carrega contextos
            sucesso_ctx, contextos, erro_ctx = context_service.carregar_todos_contextos()
            if not sucesso_ctx:
                contextos = []
            
            # Gera nova resposta
            sucesso_ia, resposta_ia, erro_ia = gemini_service.gerar_resposta(
                mensagem.conteudo, contextos
            )
            
            if not sucesso_ia:
                return helpers.create_response(False, "Erro ao regenerar resposta", error=erro_ia)
            
            # Salva nova resposta
            mensagem_ia = Mensagem(
                chat_id=chat_id,
                usuario_id=None,
                conteudo=f"[RESPOSTA REGENERADA]\n\n{resposta_ia}",
                e_nota_orientador=False
            )
            
            msg_ia_salva = self.mensagem_dao.criar_mensagem(mensagem_ia)
            
            # Registra uso
            api_monitor.registrar_requisicao(tokens=len(resposta_ia) // 4)
            
            return helpers.create_response(
                True,
                "Resposta regenerada com sucesso",
                data=msg_ia_salva.to_dict() if msg_ia_salva else None
            )
            
        except Exception as e:
            logger.error_trace(e, "regenerar_resposta")
            return helpers.create_response(False, "Erro ao regenerar resposta", error=str(e))
    
    def obter_status_api(self) -> Dict:
        """Retorna status atual da API"""
        try:
            relatorio = api_monitor.obter_relatorio()
            
            return helpers.create_response(
                True,
                "Status da API obtido com sucesso",
                data=relatorio
            )
            
        except Exception as e:
            logger.error_trace(e, "obter_status_api")
            return helpers.create_response(False, "Erro ao obter status", error=str(e))


# Instância global
gemini_controller = GeminiController()