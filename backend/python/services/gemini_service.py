"""
Serviço de integração com Google Gemini AI
"""
import google.generativeai as genai
from typing import Optional, List, Dict, Tuple
from config.settings import settings
from utils.logger import logger
import time


class GeminiService:
    """Serviço para interação com o Gemini AI"""
    
    def __init__(self):
        # Configura API do Gemini
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # Configurações de geração
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # Configurações de segurança
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        # Inicializa modelo
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Inicializa o modelo Gemini"""
        try:
            # Configuração específica para thinking mode
            model_config = {
                "generation_config": self.generation_config,
                "safety_settings": self.safety_settings
            }
            
            # Se thinking mode estiver ativado, adiciona nas instruções do sistema
            system_instruction = self._get_system_instruction()
            
            self.model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
                system_instruction=system_instruction
            )
            
            logger.info(f"✅ Modelo Gemini inicializado: {settings.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar modelo Gemini: {e}")
            raise
    
    def _get_system_instruction(self) -> str:
        """Retorna as instruções do sistema para a IA"""
        instruction = """Você é o APBIA (Ajudante de Projetos para Bragantec Baseado em IA), 
um assistente especializado em auxiliar estudantes do IFSP Bragança Paulista na feira de ciências Bragantec.

Sua função é:
1. Ajudar os estudantes a desenvolver projetos científicos de qualidade
2. Fornecer ideias criativas e inovadoras para projetos
3. Auxiliar no planejamento e organização dos projetos
4. Responder dúvidas sobre metodologia científica
5. Dar feedback construtivo sobre ideias e propostas

Você tem acesso aos cadernos de resumos das edições anteriores da Bragantec como contexto.

Seja sempre:
- Didático e claro em suas explicações
- Encorajador e positivo
- Científico, mas acessível
- Criativo ao sugerir ideias
- Ético e responsável

Se você receber uma pergunta complexa que requer reflexão profunda, use seu modo de pensamento 
para analisar cuidadosamente antes de responder."""

        if settings.GEMINI_THINKING_MODE:
            instruction += "\n\nPara perguntas complexas, pense cuidadosamente antes de responder."
        
        return instruction
    
    def gerar_resposta(self, mensagem: str, contexto: Optional[List[str]] = None, 
                      historico: Optional[List[Dict]] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Gera resposta usando o Gemini
        
        Args:
            mensagem: Mensagem do usuário
            contexto: Lista de textos de contexto (arquivos TXT da Bragantec)
            historico: Histórico de conversas anterior
        
        Returns:
            Tuple[success, resposta, error_message]
        """
        try:
            # Inicia chat
            if historico:
                chat = self.model.start_chat(history=self._format_historico(historico))
            else:
                chat = self.model.start_chat()
            
            # Prepara prompt com contexto
            prompt = self._build_prompt(mensagem, contexto)
            
            # Gera resposta
            logger.info(f"📤 Enviando mensagem para Gemini...")
            response = chat.send_message(prompt)
            
            # Extrai texto da resposta
            resposta_texto = response.text
            
            logger.info(f"✅ Resposta recebida do Gemini")
            logger.log_api_call("Gemini", self._estimate_tokens(prompt + resposta_texto))
            
            return True, resposta_texto, None
            
        except Exception as e:
            error_msg = f"Erro ao gerar resposta: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
    
    def gerar_resposta_com_thinking(self, mensagem: str, contexto: Optional[List[str]] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Gera resposta usando thinking mode para perguntas complexas
        
        Returns:
            Tuple[success, resposta, error_message]
        """
        try:
            # Adiciona instrução para pensar
            prompt_thinking = f"""Esta é uma pergunta que requer reflexão cuidadosa.
Por favor, pense profundamente sobre ela antes de responder.

Pergunta: {mensagem}"""
            
            if contexto:
                prompt_thinking += f"\n\nContexto disponível:\n{self._format_contexto(contexto)}"
            
            # Gera resposta com thinking
            response = self.model.generate_content(
                prompt_thinking,
                generation_config={
                    **self.generation_config,
                    "temperature": 0.9  # Aumenta criatividade para thinking
                }
            )
            
            resposta_texto = response.text
            
            logger.info(f"✅ Resposta com thinking mode gerada")
            return True, resposta_texto, None
            
        except Exception as e:
            error_msg = f"Erro ao gerar resposta com thinking: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
    
    def _build_prompt(self, mensagem: str, contexto: Optional[List[str]] = None) -> str:
        """Constrói o prompt com mensagem e contexto"""
        prompt = ""
        
        if contexto:
            prompt += "=== CONTEXTO (Cadernos de Resumos da Bragantec) ===\n"
            prompt += self._format_contexto(contexto)
            prompt += "\n=== FIM DO CONTEXTO ===\n\n"
        
        prompt += f"Pergunta do estudante: {mensagem}"
        
        return prompt
    
    def _format_contexto(self, contexto: List[str]) -> str:
        """Formata lista de contextos em texto único"""
        return "\n\n---\n\n".join(contexto)
    
    def _format_historico(self, historico: List[Dict]) -> List[Dict]:
        """Formata histórico para o formato do Gemini"""
        formatted = []
        
        for msg in historico:
            role = "user" if msg.get("usuario_id") else "model"
            formatted.append({
                "role": role,
                "parts": [msg.get("conteudo", "")]
            })
        
        return formatted
    
    def _estimate_tokens(self, text: str) -> int:
        """Estima número de tokens (aproximação)"""
        # Aproximação: ~4 caracteres por token
        return len(text) // 4
    
    def upload_arquivo_para_gemini(self, file_path: str, file_content: bytes, mime_type: str) -> Tuple[bool, Optional[any], Optional[str]]:
        """
        Faz upload de arquivo diretamente para o Gemini (para processamento de documentos)
        
        Returns:
            Tuple[success, file_object, error_message]
        """
        try:
            # Salva arquivo temporariamente
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_path).suffix) as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name
            
            # Upload para Gemini
            file = genai.upload_file(tmp_path, mime_type=mime_type)
            
            # Aguarda processamento
            while file.state.name == "PROCESSING":
                time.sleep(2)
                file = genai.get_file(file.name)
            
            if file.state.name == "FAILED":
                raise Exception("Falha ao processar arquivo")
            
            logger.info(f"✅ Arquivo enviado para Gemini: {file_path}")
            return True, file, None
            
        except Exception as e:
            error_msg = f"Erro ao enviar arquivo para Gemini: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
    
    def processar_documento(self, file_object: any, pergunta: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Processa documento com o Gemini
        
        Returns:
            Tuple[success, resposta, error_message]
        """
        try:
            prompt = [file_object, pergunta]
            response = self.model.generate_content(prompt)
            
            logger.info(f"✅ Documento processado")
            return True, response.text, None
            
        except Exception as e:
            error_msg = f"Erro ao processar documento: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg


# Instância global
gemini_service = GeminiService()