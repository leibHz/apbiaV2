"""
Gerenciador de conexão com o banco de dados Supabase
"""
from supabase import create_client, Client
from config.settings import settings
from utils.logger import logger


class Database:
    """Classe Singleton para gerenciar conexão com Supabase"""
    
    _instance = None
    _client: Client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa a conexão com o Supabase"""
        try:
            self._client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            logger.info("✅ Conexão com Supabase estabelecida")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com Supabase: {e}")
            raise
    
    @property
    def client(self) -> Client:
        """Retorna o cliente Supabase"""
        if self._client is None:
            self._initialize()
        return self._client
    
    def health_check(self) -> bool:
        """Verifica se a conexão está saudável"""
        try:
            # Tenta fazer uma query simples
            result = self._client.table("tipos_usuario").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Health check falhou: {e}")
            return False
    
    def get_table(self, table_name: str):
        """Retorna uma referência para uma tabela"""
        return self._client.table(table_name)
    
    def execute_query(self, query: str):
        """Executa uma query SQL direta (usar com cuidado)"""
        try:
            result = self._client.rpc(query).execute()
            return result
        except Exception as e:
            logger.error(f"❌ Erro ao executar query: {e}")
            raise
    
    def get_storage(self):
        """Retorna o cliente de storage do Supabase"""
        return self._client.storage
    
    def get_bucket(self, bucket_name: str):
        """Retorna um bucket específico"""
        return self._client.storage.from_(bucket_name)


# Instância global do database
db = Database()