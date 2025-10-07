"""
Serviço de integração com Google Gemini AI
CORRIGIDO: Agora usa corretamente os contextos TXT
"""
import google.generativeai as genai
from typing import Optional, List, Dict, Tuple
from config.settings import settings
from utils.logger import logger


class GeminiService:
    """Serviço para interação com o Gemini AI"""
    
    def __init__(self):
        # Configura API
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
        
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Inicializa o modelo Gemini"""
        try:
            system_instruction = self._get_system_instruction()
            
            self.model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
                system_instruction=system_instruction
            )
            
            logger.info(f"✅ Modelo Gemini inicializado: {settings.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Gemini: {e}")
            raise
    
    def _get_system_instruction(self) -> str:
        """Instruções do sistema para a IA"""
        return """Você é o APBIA (Ajudante de Projetos para Bragantec Baseado em IA), 
um assistente especializado em auxiliar estudantes do IFSP Bragança Paulista na feira de ciências Bragantec.

Sua personalidade deve ser:
- Humana e empática, não robotizada
- Entusiasmada e motivadora
- Paciente e didática
- Criativa e inovadora
- Científica mas acessível

Suas funções principais:
1. Ajudar a desenvolver projetos científicos de qualidade
2. Fornecer ideias criativas e inovadoras
3. Auxiliar no planejamento e organização
4. Responder dúvidas sobre metodologia científica
5. Dar feedback construtivo

Você tem acesso aos cadernos de resumos das edições anteriores da Bragantec como contexto.
Use essas informações para inspirar e orientar os estudantes com base em projetos reais de sucesso.

IMPORTANTE: 
- Sempre seja encorajador e positivo
- Explique conceitos complexos de forma simples
- Use exemplos práticos sempre que possível
- Se não souber algo, seja honesto
- Para perguntas complexas, pense cuidadosamente antes de responder"""
    
    def gerar_resposta(self, mensagem: str, contexto: Optional[List[str]] = None, 
                      historico: Optional[List[Dict]] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Gera resposta usando o Gemini com contextos TXT
        """
        try:
            logger.info(f"🤖 Gerando resposta para: {mensagem[:50]}...")
            
            # Prepara o prompt com contexto
            prompt_completo = self._build_prompt_com_contexto(mensagem, contexto)
            
            logger.info(f"📝 Prompt construído com {len(prompt_completo)} caracteres")
            if contexto:
                logger.info(f"📚 Usando {len(contexto)} contexto(s) da Bragantec")
            
            # Se tem histórico, usa chat
            if historico:
                chat = self.model.start_chat(history=self._format_historico(historico))
                response = chat.send_message(prompt_completo)
            else:
                # Senão, gera resposta direta
                response = self.model.generate_content(prompt_completo)
            
            resposta_texto = response.text
            
            logger.info(f"✅ Resposta gerada ({len(resposta_texto)} caracteres)")
            logger.log_api_call("Gemini", self._estimate_tokens(prompt_completo + resposta_texto))
            
            return True, resposta_texto, None
            
        except Exception as e:
            error_msg = f"Erro ao gerar resposta: {str(e)}"
            logger.error(f"❌ {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            return False, None, error_msg
    
    def gerar_resposta_com_thinking(self, mensagem: str, contexto: Optional[List[str]] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Gera resposta com modo de pensamento profundo (thinking mode)
        """
        try:
            logger.info(f"🧠 Modo THINKING ativado para pergunta complexa")
            
            # Prompt especial para thinking
            prompt_thinking = f"""Esta é uma pergunta que requer reflexão profunda e análise cuidadosa.
Por favor, pense sobre todos os aspectos antes de responder.

Pergunta do estudante: {mensagem}"""
            
            # Adiciona contexto se disponível
            if contexto and len(contexto) > 0:
                prompt_thinking += "\n\n=== CONTEXTO (Projetos anteriores da Bragantec) ===\n"
                prompt_thinking += self._format_contexto(contexto)
                prompt_thinking += "\n=== FIM DO CONTEXTO ===\n\n"
                prompt_thinking += "Use as informações do contexto para fundamentar sua resposta."
            
            # Gera com configuração para pensamento mais profundo
            response = self.model.generate_content(
                prompt_thinking,
                generation_config={
                    **self.generation_config,
                    "temperature": 0.9,  # Mais criatividade
                    "top_p": 0.98
                }
            )
            
            resposta_texto = response.text
            
            logger.info(f"✅ Resposta com thinking gerada ({len(resposta_texto)} chars)")
            return True, resposta_texto, None
            
        except Exception as e:
            error_msg = f"Erro no thinking mode: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
    
    def _build_prompt_com_contexto(self, mensagem: str, contexto: Optional[List[str]] = None) -> str:
        """
        Constrói prompt completo com contextos da Bragantec
        """
        prompt = ""
        
        # Adiciona contextos se existirem
        if contexto and len(contexto) > 0:
            prompt += "=== CONTEXTO: Cadernos de Resumos da Bragantec (Edições Anteriores) ===\n\n"
            prompt += "Você tem acesso aos seguintes projetos e informações de edições passadas da Bragantec:\n\n"
            
            # Adiciona cada contexto separadamente
            for i, ctx in enumerate(contexto, 1):
                # Limita o tamanho de cada contexto para não exceder o limite do modelo
                ctx_limitado = ctx[:15000] if len(ctx) > 15000 else ctx
                prompt += f"--- Documento {i} ---\n{ctx_limitado}\n\n"
            
            prompt += "=== FIM DO CONTEXTO ===\n\n"
            prompt += "Use as informações acima para inspirar e orientar o estudante, mencionando exemplos relevantes quando apropriado.\n\n"
        
        # Adiciona a pergunta do usuário
        prompt += f"Pergunta do estudante:\n{mensagem}\n\n"
        prompt += "Responda de forma clara, didática e encorajadora, usando os exemplos do contexto quando relevante:"
        
        return prompt
    
    def _format_contexto(self, contexto: List[str]) -> str:
        """Formata lista de contextos"""
        resultado = ""
        for i, ctx in enumerate(contexto, 1):
            ctx_limitado = ctx[:15000] if len(ctx) > 15000 else ctx
            resultado += f"\n--- Documento {i} ---\n{ctx_limitado}\n"
        return resultado
    
    def _format_historico(self, historico: List[Dict]) -> List[Dict]:
        """Formata histórico para o Gemini"""
        formatted = []
        
        for msg in historico:
            # Se usuario_id é None, é mensagem da IA
            role = "model" if msg.get("usuario_id") is None else "user"
            
            formatted.append({
                "role": role,
                "parts": [msg.get("conteudo", "")]
            })
        
        return formatted
    
    def _estimate_tokens(self, text: str) -> int:
        """Estima tokens (aproximação: 4 chars = 1 token)"""
        return len(text) // 4
    
    def processar_documento_txt(self, conteudo_txt: str, pergunta: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Processa documento TXT com o Gemini
        """
        try:
            prompt = f"""Documento fornecido:
{conteudo_txt}

Pergunta sobre o documento:
{pergunta}

Responda com base no conteúdo do documento acima:"""
            
            response = self.model.generate_content(prompt)
            
            logger.info(f"✅ Documento TXT processado")
            return True, response.text, None
            
        except Exception as e:
            return False, None, str(e)


# Instância global
gemini_service = GeminiService()