"""
Validadores para o sistema APBIA
"""
import re
from typing import Optional


class Validators:
    """Classe com validadores do sistema"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_bp(bp: str) -> bool:
        """
        Valida formato do BP (prontuário)
        Formato esperado: BRGxxxxxxxx (BRG + 8 dígitos)
        """
        if not bp:
            return False
        pattern = r'^BRG\d{8}$'
        return bool(re.match(pattern, bp.upper()))
    
    @staticmethod
    def validate_senha(senha: str) -> tuple[bool, Optional[str]]:
        """
        Valida senha
        Requisitos:
        - Mínimo 8 caracteres
        - Pelo menos uma letra maiúscula
        - Pelo menos uma letra minúscula
        - Pelo menos um número
        """
        if len(senha) < 8:
            return False, "Senha deve ter no mínimo 8 caracteres"
        
        if not re.search(r'[A-Z]', senha):
            return False, "Senha deve conter pelo menos uma letra maiúscula"
        
        if not re.search(r'[a-z]', senha):
            return False, "Senha deve conter pelo menos uma letra minúscula"
        
        if not re.search(r'\d', senha):
            return False, "Senha deve conter pelo menos um número"
        
        return True, None
    
    @staticmethod
    def validate_ano_edicao(ano: int) -> bool:
        """Valida ano de edição da Bragantec"""
        current_year = 2025
        return 2010 <= ano <= current_year + 1
    
    @staticmethod
    def validate_area_projeto(area: str) -> bool:
        """Valida área do projeto"""
        areas_validas = {
            "Ciências Exatas e da Terra",
            "Ciências Biológicas",
            "Engenharias",
            "Ciências da Saúde",
            "Ciências Agrárias",
            "Ciências Sociais Aplicadas",
            "Ciências Humanas",
            "Linguística, Letras e Artes"
        }
        return area in areas_validas
    
    @staticmethod
    def validate_tipo_usuario(tipo: str) -> bool:
        """Valida tipo de usuário"""
        tipos_validos = {"participante", "orientador", "admin"}
        return tipo.lower() in tipos_validos
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
        """Valida extensão de arquivo"""
        from pathlib import Path
        ext = Path(filename).suffix.lower()
        return ext in allowed_extensions
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitiza nome de arquivo"""
        # Remove caracteres especiais, mantém apenas letras, números, pontos e underscores
        return re.sub(r'[^a-zA-Z0-9._-]', '_', filename)


# Instância global
validators = Validators()