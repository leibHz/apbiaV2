"""
DAO de Projeto
"""
from typing import Optional, List
from dao.base_dao import BaseDAO
from models.projeto import Projeto
from config.database import db
from utils.logger import logger


class ProjetoDAO(BaseDAO):
    """DAO para gerenciar projetos"""
    
    def __init__(self):
        super().__init__("projetos")
    
    def criar_projeto(self, projeto: Projeto) -> Optional[Projeto]:
        """Cria um novo projeto"""
        data = {
            "nome": projeto.nome,
            "descricao": projeto.descricao,
            "area_projeto": projeto.area_projeto,
            "ano_edicao": projeto.ano_edicao
        }
        
        result = self.create(data)
        if result:
            return Projeto.from_dict(result)
        return None
    
    def buscar_por_id(self, id: int) -> Optional[Projeto]:
        """Busca projeto por ID"""
        result = self.find_by_id(id)
        if result:
            projeto = Projeto.from_dict(result)
            return self._enrich_projeto(projeto)
        return None
    
    def listar_por_ano(self, ano: int) -> List[Projeto]:
        """Lista projetos por ano"""
        results = self.find_by_field("ano_edicao", ano)
        return [self._enrich_projeto(Projeto.from_dict(r)) for r in results]
    
    def listar_por_area(self, area: str) -> List[Projeto]:
        """Lista projetos por área"""
        results = self.find_by_field("area_projeto", area)
        return [self._enrich_projeto(Projeto.from_dict(r)) for r in results]
    
    def listar_todos(self) -> List[Projeto]:
        """Lista todos os projetos"""
        results = self.find_all()
        return [self._enrich_projeto(Projeto.from_dict(r)) for r in results]
    
    def atualizar_projeto(self, projeto: Projeto) -> Optional[Projeto]:
        """Atualiza projeto"""
        data = {
            "nome": projeto.nome,
            "descricao": projeto.descricao,
            "area_projeto": projeto.area_projeto,
            "ano_edicao": projeto.ano_edicao
        }
        
        result = self.update(projeto.id, data)
        if result:
            return Projeto.from_dict(result)
        return None
    
    def _enrich_projeto(self, projeto: Projeto) -> Projeto:
        """Enriquece projeto com participantes e orientadores"""
        # Busca participantes
        participantes = self._buscar_participantes(projeto.id)
        projeto.participantes = participantes
        
        # Busca orientadores
        orientadores = self._buscar_orientadores(projeto.id)
        projeto.orientadores = orientadores
        
        return projeto
    
    def _buscar_participantes(self, projeto_id: int) -> List[dict]:
        """Busca participantes do projeto"""
        try:
            query = """
                SELECT u.id, u.nome_completo, u.email, u.bp
                FROM usuarios u
                INNER JOIN participantes_projetos pp ON u.id = pp.participante_id
                WHERE pp.projeto_id = {}
            """.format(projeto_id)
            
            result = db.client.table("usuarios").select(
                "id, nome_completo, email, bp"
            ).eq("id", "").execute()
            
            # Alternativa usando join do Supabase
            result = db.client.rpc('get_participantes_projeto', {'p_projeto_id': projeto_id}).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Erro ao buscar participantes: {e}")
            return []
    
    def _buscar_orientadores(self, projeto_id: int) -> List[dict]:
        """Busca orientadores do projeto"""
        try:
            result = db.client.rpc('get_orientadores_projeto', {'p_projeto_id': projeto_id}).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Erro ao buscar orientadores: {e}")
            return []
    
    def adicionar_participante(self, projeto_id: int, participante_id: int) -> bool:
        """Adiciona participante ao projeto"""
        try:
            data = {
                "projeto_id": projeto_id,
                "participante_id": participante_id
            }
            result = db.get_table("participantes_projetos").insert(data).execute()
            return result.data is not None
        except Exception as e:
            logger.error(f"Erro ao adicionar participante: {e}")
            return False
    
    def adicionar_orientador(self, projeto_id: int, orientador_id: int) -> bool:
        """Adiciona orientador ao projeto"""
        try:
            data = {
                "projeto_id": projeto_id,
                "orientador_id": orientador_id
            }
            result = db.get_table("orientadores_projetos").insert(data).execute()
            return result.data is not None
        except Exception as e:
            logger.error(f"Erro ao adicionar orientador: {e}")
            return False
    
    def remover_participante(self, projeto_id: int, participante_id: int) -> bool:
        """Remove participante do projeto"""
        try:
            result = db.get_table("participantes_projetos").delete().match({
                "projeto_id": projeto_id,
                "participante_id": participante_id
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao remover participante: {e}")
            return False
    
    def remover_orientador(self, projeto_id: int, orientador_id: int) -> bool:
        """Remove orientador do projeto"""
        try:
            result = db.get_table("orientadores_projetos").delete().match({
                "projeto_id": projeto_id,
                "orientador_id": orientador_id
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao remover orientador: {e}")
            return False