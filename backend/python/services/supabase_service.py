"""
Serviço de integração com Supabase Storage
"""
from typing import Optional, Tuple
from pathlib import Path
from config.database import db
from config.settings import settings
from utils.logger import logger
from utils.validators import validators


class SupabaseService:
    """Serviço para gerenciar storage do Supabase"""
    
    def __init__(self):
        self.storage = db.get_storage()
    
    def upload_arquivo(self, file_path: str, file_content: bytes, bucket_name: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload de arquivo para o Supabase Storage
        
        Returns:
            Tuple[success, url, error_message]
        """
        try:
            if bucket_name is None:
                bucket_name = settings.BUCKET_NAME
            
            bucket = self.storage.from_(bucket_name)
            
            # Sanitiza nome do arquivo
            filename = validators.sanitize_filename(Path(file_path).name)
            
            # Faz upload
            result = bucket.upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": self._get_content_type(filename)}
            )
            
            # Gera URL pública
            url = bucket.get_public_url(file_path)
            
            logger.info(f"✅ Arquivo enviado: {file_path}")
            return True, url, None
            
        except Exception as e:
            error_msg = f"Erro ao fazer upload: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
    
    def download_arquivo(self, file_path: str, bucket_name: str = None) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Download de arquivo do Supabase Storage
        
        Returns:
            Tuple[success, file_content, error_message]
        """
        try:
            if bucket_name is None:
                bucket_name = settings.BUCKET_NAME
            
            bucket = self.storage.from_(bucket_name)
            
            # Download
            result = bucket.download(file_path)
            
            logger.info(f"✅ Arquivo baixado: {file_path}")
            return True, result, None
            
        except Exception as e:
            error_msg = f"Erro ao baixar arquivo: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
    
    def deletar_arquivo(self, file_path: str, bucket_name: str = None) -> Tuple[bool, Optional[str]]:
        """
        Deleta arquivo do Supabase Storage
        
        Returns:
            Tuple[success, error_message]
        """
        try:
            if bucket_name is None:
                bucket_name = settings.BUCKET_NAME
            
            bucket = self.storage.from_(bucket_name)
            
            # Deleta
            bucket.remove([file_path])
            
            logger.info(f"✅ Arquivo deletado: {file_path}")
            return True, None
            
        except Exception as e:
            error_msg = f"Erro ao deletar arquivo: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def listar_arquivos(self, path: str = "", bucket_name: str = None) -> list:
        """Lista arquivos em um bucket"""
        try:
            if bucket_name is None:
                bucket_name = settings.BUCKET_NAME
            
            bucket = self.storage.from_(bucket_name)
            result = bucket.list(path)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar arquivos: {e}")
            return []
    
    def get_url_publica(self, file_path: str, bucket_name: str = None) -> Optional[str]:
        """Retorna URL pública de um arquivo"""
        try:
            if bucket_name is None:
                bucket_name = settings.BUCKET_NAME
            
            bucket = self.storage.from_(bucket_name)
            url = bucket.get_public_url(file_path)
            
            return url
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar URL pública: {e}")
            return None
    
    def _get_content_type(self, filename: str) -> str:
        """Retorna o content-type baseado na extensão"""
        ext = Path(filename).suffix.lower()
        
        content_types = {
            '.txt': 'text/plain',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif'
        }
        
        return content_types.get(ext, 'application/octet-stream')
    
    def criar_bucket(self, bucket_name: str, public: bool = True) -> bool:
        """Cria um novo bucket"""
        try:
            self.storage.create_bucket(bucket_name, {"public": public})
            logger.info(f"✅ Bucket criado: {bucket_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao criar bucket: {e}")
            return False
    
    def bucket_existe(self, bucket_name: str) -> bool:
        """Verifica se bucket existe"""
        try:
            buckets = self.storage.list_buckets()
            return any(b.name == bucket_name for b in buckets)
        except Exception as e:
            logger.error(f"❌ Erro ao verificar bucket: {e}")
            return False


# Instância global
supabase_service = SupabaseService()