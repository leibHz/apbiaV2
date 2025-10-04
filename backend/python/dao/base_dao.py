"""
Base DAO - Classe base para todos os DAOs
"""
from typing import List, Optional, Dict, Any
from config.database import db
from utils.logger import logger


class BaseDAO:
    """Classe base para todos os DAOs"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.table = db.get_table(table_name)
    
    def create(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Cria um novo registro"""
        try:
            result = self.table.insert(data).execute()
            if result.data:
                logger.info(f"✅ Registro criado em {self.table_name}: ID {result.data[0].get('id')}")
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao criar registro em {self.table_name}: {e}")
            raise
    
    def find_by_id(self, id: int) -> Optional[Dict]:
        """Busca registro por ID"""
        try:
            result = self.table.select("*").eq("id", id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Erro ao buscar por ID em {self.table_name}: {e}")
            return None
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Busca todos os registros"""
        try:
            result = self.table.select("*").range(offset, offset + limit - 1).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"❌ Erro ao buscar todos em {self.table_name}: {e}")
            return []
    
    def find_by_field(self, field: str, value: Any) -> List[Dict]:
        """Busca registros por campo específico"""
        try:
            result = self.table.select("*").eq(field, value).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"❌ Erro ao buscar por campo em {self.table_name}: {e}")
            return []
    
    def find_one_by_field(self, field: str, value: Any) -> Optional[Dict]:
        """Busca um registro por campo específico"""
        try:
            result = self.table.select("*").eq(field, value).limit(1).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Erro ao buscar um por campo em {self.table_name}: {e}")
            return None
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[Dict]:
        """Atualiza um registro"""
        try:
            result = self.table.update(data).eq("id", id).execute()
            if result.data:
                logger.info(f"✅ Registro atualizado em {self.table_name}: ID {id}")
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar registro em {self.table_name}: {e}")
            raise
    
    def delete(self, id: int) -> bool:
        """Deleta um registro"""
        try:
            result = self.table.delete().eq("id", id).execute()
            logger.info(f"✅ Registro deletado em {self.table_name}: ID {id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao deletar registro em {self.table_name}: {e}")
            return False
    
    def count(self) -> int:
        """Conta total de registros"""
        try:
            result = self.table.select("id", count="exact").execute()
            return result.count if result.count else 0
        except Exception as e:
            logger.error(f"❌ Erro ao contar registros em {self.table_name}: {e}")
            return 0
    
    def exists(self, field: str, value: Any) -> bool:
        """Verifica se existe um registro com determinado valor"""
        try:
            result = self.table.select("id").eq(field, value).limit(1).execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            logger.error(f"❌ Erro ao verificar existência em {self.table_name}: {e}")
            return False