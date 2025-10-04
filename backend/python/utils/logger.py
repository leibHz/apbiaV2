"""
Sistema de logging para o APBIA
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from config.settings import settings


class Logger:
    """Classe para gerenciar logs do sistema"""
    
    def __init__(self):
        self.logger = logging.getLogger(settings.PROJECT_NAME)
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Remove handlers existentes para evitar duplicação
        self.logger.handlers = []
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File Handler
        self._setup_file_handler(formatter)
    
    def _setup_file_handler(self, formatter):
        """Configura o handler de arquivo"""
        try:
            # Cria diretório de logs se não existir
            log_dir = settings.LOG_FILE.parent
            log_dir.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(settings.LOG_FILE, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"⚠️  Não foi possível criar arquivo de log: {e}")
    
    def info(self, message: str):
        """Log de informação"""
        self.logger.info(message)
    
    def error(self, message: str):
        """Log de erro"""
        self.logger.error(message)
    
    def warning(self, message: str):
        """Log de aviso"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """Log de debug"""
        self.logger.debug(message)
    
    def critical(self, message: str):
        """Log crítico"""
        self.logger.critical(message)
    
    def log_request(self, user_id: int, endpoint: str, method: str):
        """Log de requisição"""
        self.info(f"REQUEST | User: {user_id} | {method} {endpoint}")
    
    def log_api_call(self, service: str, tokens_used: int = 0):
        """Log de chamada à API externa"""
        self.info(f"API_CALL | Service: {service} | Tokens: {tokens_used}")
    
    def log_error_trace(self, error: Exception, context: str = ""):
        """Log de erro com traceback"""
        import traceback
        error_trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        self.error(f"ERROR | Context: {context}\n{error_trace}")


# Instância global do logger
logger = Logger()