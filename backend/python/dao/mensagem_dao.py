"""
DAO de Mensagem
"""
from typing import Optional, List
from dao.base_dao import BaseDAO
from models.mensagem import Mensagem
from config.database import db
from utils.logger import logger


class MensagemDAO(BaseDAO):
    """DAO para gerenciar mensagens"""
    
    def __init__(self):
        super().__init__("mensagens")
    
    def criar_mensagem(self, mensagem: Mensagem) -> Optional[Mensagem]:
        """Cria uma nova mensagem"""
        data = {
            "chat_id": mensagem.chat_id,
            "usuario_id": mensagem.usuario_id,
            "conteudo": mensagem.conteudo,
            "e_nota_orientador": mensagem.e_nota_orientador
        }
        
        result = self.create(data)
        if result:
            return Mensagem.from_dict(result)
        return None
    
    def buscar_por_id(self, id: int) -> Optional[Mensagem]:
        """Busca mensagem por ID"""
        result = self.find_by_id(id)
        if result:
            mensagem = Mensagem.from_dict(result)
            return self._enrich_mensagem(mensagem)
        return None
    
    def listar_por_chat(self, chat_id: int, limit: int = 100) -> List[Mensagem]:
        """Lista mensagens de um chat"""
        try:
            result = self.table.select("*").eq("chat_id", chat_id).order("data_envio", desc=False).limit(limit).execute()
            mensagens = [Mensagem.from_dict(m) for m in result.data] if result.data else []
            return [self._enrich_mensagem(m) for m in mensagens]
        except Exception as e:
            logger.error(f"Erro ao listar mensagens: {e}")
            return []
    
    def listar_por_usuario(self, usuario_id: int) -> List[Mensagem]:
        """Lista mensagens de um usuário"""
        results = self.find_by_field("usuario_id", usuario_id)
        return [self._enrich_mensagem(Mensagem.from_dict(m)) for m in results]
    
    def listar_notas_orientador(self, chat_id: int) -> List[Mensagem]:
        """Lista apenas notas do orientador em um chat"""
        try:
            result = self.table.select("*").eq("chat_id", chat_id).eq("e_nota_orientador", True).execute()
            mensagens = [Mensagem.from_dict(m) for m in result.data] if result.data else []
            return [self._enrich_mensagem(m) for m in mensagens]
        except Exception as e:
            logger.error(f"Erro ao listar notas do orientador: {e}")
            return []
    
    def atualizar_conteudo(self, mensagem_id: int, novo_conteudo: str) -> Optional[Mensagem]:
        """Atualiza conteúdo da mensagem"""
        result = self.update(mensagem_id, {"conteudo": novo_conteudo})
        if result:
            return Mensagem.from_dict(result)
        return None
    
    def _enrich_mensagem(self, mensagem: Mensagem) -> Mensagem:
        """Enriquece mensagem com informações adicionais"""
        # Busca nome do usuário se existir
        if mensagem.usuario_id:
            try:
                usuario_result = db.get_table("usuarios").select("nome_completo").eq("id", mensagem.usuario_id).execute()
                if usuario_result.data:
                    mensagem.usuario_nome = usuario_result.data[0].get("nome_completo")
            except Exception as e:
                logger.error(f"Erro ao buscar nome do usuário: {e}")
        
        # Busca arquivos anexados
        try:
            from dao.arquivo_dao import ArquivoDAO
            arquivo_dao = ArquivoDAO()
            mensagem.arquivos = [a.to_dict() for a in arquivo_dao.listar_por_mensagem(mensagem.id)]
        except Exception as e:
            logger.error(f"Erro ao buscar arquivos: {e}")
            mensagem.arquivos = []
        
        return mensagem
    
    def deletar_mensagem(self, mensagem_id: int) -> bool:
        """Deleta uma mensagem"""
        return self.delete(mensagem_id)
    
    def contar_mensagens_chat(self, chat_id: int) -> int:
        """Conta mensagens de um chat"""
        try:
            result = self.table.select("id", count="exact").eq("chat_id", chat_id).execute()
            return result.count if result.count else 0
        except Exception as e:
            logger.error(f"Erro ao contar mensagens: {e}")
            return 0