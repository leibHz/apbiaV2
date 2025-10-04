"""
Configurações do sistema APBIA
Gerencia variáveis de ambiente e configurações globais
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Carrega variáveis de ambiente
load_dotenv()

class Settings:
    """Classe de configurações do sistema"""
    
    # Configurações do Projeto
    PROJECT_NAME = "APBIA"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Configurações do Servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    
    # Configurações do Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
    SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
    
    # Configurações do Google Gemini
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL = "gemini-2.5-flash"
    GEMINI_THINKING_MODE = True
    
    # Configurações de Rate Limiting
    API_RATE_LIMIT = 80  # Porcentagem para começar throttling
    API_MAX_REQUESTS_PER_MINUTE = 60
    API_DELAY_SECONDS = 2  # Delay quando atingir 80%
    
    # Configurações de Segurança
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    BCRYPT_ROUNDS = 12
    
    # Configurações de Upload
    UPLOAD_FOLDER = Path("uploads")
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {".txt", ".pdf", ".doc", ".docx"}
    
    # Configurações de Buckets Supabase
    BUCKET_NAME = "bragantec-files"
    BUCKET_CONTEXT = "context-files"
    
    # Configurações de Log
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = Path("storage/logs/apbia.log")
    
    # Configurações de Sistema
    SISTEMA_ATIVO = True  # Admin pode desativar
    MANUTENCAO = False
    
    @classmethod
    def validate(cls):
        """Valida se todas as configurações obrigatórias estão presentes"""
        required = [
            "SUPABASE_URL",
            "SUPABASE_KEY",
            "GOOGLE_API_KEY"
        ]
        
        missing = []
        for var in required:
            if not getattr(cls, var):
                missing.append(var)
        
        if missing:
            raise ValueError(f"Variáveis de ambiente obrigatórias faltando: {', '.join(missing)}")
        
        return True
    
    @classmethod
    def get_gemini_config(cls):
        """Retorna configuração do Gemini"""
        return {
            "api_key": cls.GOOGLE_API_KEY,
            "model": cls.GEMINI_MODEL,
            "thinking_mode": cls.GEMINI_THINKING_MODE
        }
    
    @classmethod
    def get_supabase_config(cls):
        """Retorna configuração do Supabase"""
        return {
            "url": cls.SUPABASE_URL,
            "key": cls.SUPABASE_KEY,
            "secret_key": cls.SUPABASE_SECRET_KEY
        }


# Instância global das configurações
settings = Settings()

# Valida configurações ao importar
if __name__ != "__main__":
    try:
        settings.validate()
    except ValueError as e:
        print(f"⚠️  AVISO: {e}")