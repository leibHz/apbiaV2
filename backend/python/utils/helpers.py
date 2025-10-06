"""
Funções auxiliares para o sistema APBIA
"""
import hashlib
import secrets
import bcrypt
from datetime import datetime, timedelta
import jwt
from config.settings import settings
from typing import Optional, Dict, Any


class Helpers:
    """Classe com funções auxiliares"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Gera hash de senha usando bcrypt"""
        salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verifica se a senha corresponde ao hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def generate_token(user_id: int, tipo_usuario: str) -> str:
        """Gera JWT token"""
        payload = {
            'user_id': user_id,
            'tipo_usuario': tipo_usuario,
            'exp': datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return token
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """Decodifica JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """Gera nome de arquivo seguro e único"""
        from pathlib import Path
        ext = Path(original_filename).suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_str = secrets.token_hex(8)
        return f"{timestamp}_{random_str}{ext}"
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str:
        """Formata datetime para string"""
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            except:
                return dt
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_datetime(dt_str: str) -> Optional[datetime]:
        """Converte string para datetime"""
        if not dt_str or not isinstance(dt_str, str):
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return None
    
    @staticmethod
    def calculate_file_hash(file_content: bytes) -> str:
        """Calcula hash SHA256 de um arquivo"""
        return hashlib.sha256(file_content).hexdigest()
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Formata tamanho de arquivo em formato legível"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Trunca texto longo"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def create_response(success: bool, message: str, data: Any = None, error: str = None) -> Dict:
        """Cria resposta padronizada da API"""
        response = {
            "success": success,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if data is not None:
            response["data"] = data
        
        if error is not None:
            response["error"] = error
        
        return response


# Instância global
helpers = Helpers()