"""
Serviço de monitoramento de uso da API
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from config.settings import settings
from config.database import db
from utils.logger import logger
import time


class APIMonitorService:
    """Serviço para monitorar e controlar uso da API do Gemini"""
    
    def __init__(self):
        self.uso_atual = {
            'requisicoes_total': 0,
            'requisicoes_mes': 0,
            'tokens_usados': 0,
            'ultima_requisicao': None,
            'requisicoes_por_minuto': [],
            'sistema_ativo': True,
            'throttling_ativo': False
        }
        
        # Limites configuráveis
        self.limite_requisicoes_minuto = settings.API_MAX_REQUESTS_PER_MINUTE
        self.threshold_throttling = settings.API_RATE_LIMIT  # 80%
        self.delay_throttling = settings.API_DELAY_SECONDS
        
        # Carrega estado persistente
        self._carregar_estado()
    
    def registrar_requisicao(self, tokens: int = 0):
        """Registra uma nova requisição à API"""
        agora = datetime.now()
        
        # Incrementa contadores
        self.uso_atual['requisicoes_total'] += 1
        self.uso_atual['requisicoes_mes'] += 1
        self.uso_atual['tokens_usados'] += tokens
        self.uso_atual['ultima_requisicao'] = agora.isoformat()
        
        # Adiciona ao tracking de requisições por minuto
        self.uso_atual['requisicoes_por_minuto'].append(agora)
        
        # Remove requisições antigas (mais de 1 minuto)
        um_minuto_atras = agora - timedelta(minutes=1)
        self.uso_atual['requisicoes_por_minuto'] = [
            req for req in self.uso_atual['requisicoes_por_minuto']
            if isinstance(req, datetime) and req > um_minuto_atras
        ]
        
        # Salva estado
        self._salvar_estado()
        
        logger.info(f"📊 Requisição registrada | Tokens: {tokens} | Total mês: {self.uso_atual['requisicoes_mes']}")
    
    def verificar_rate_limit(self) -> tuple[bool, Optional[str]]:
        """
        Verifica se pode fazer requisição
        
        Returns:
            Tuple[pode_fazer_requisicao, mensagem_erro]
        """
        # Verifica se sistema está ativo
        if not self.uso_atual['sistema_ativo']:
            return False, "Sistema está em manutenção. IA temporariamente desativada."
        
        # Verifica limite por minuto
        agora = datetime.now()
        um_minuto_atras = agora - timedelta(minutes=1)
        
        requisicoes_ultimo_minuto = len([
            req for req in self.uso_atual['requisicoes_por_minuto']
            if isinstance(req, datetime) and req > um_minuto_atras
        ])
        
        if requisicoes_ultimo_minuto >= self.limite_requisicoes_minuto:
            return False, f"Limite de {self.limite_requisicoes_minuto} requisições por minuto atingido. Aguarde alguns segundos."
        
        # Aplica throttling se necessário
        if self.uso_atual['throttling_ativo']:
            logger.info(f"⏳ Throttling ativo - aguardando {self.delay_throttling}s")
            time.sleep(self.delay_throttling)
        
        return True, None
    
    def calcular_uso_percentual(self, limite_mensal: int = 1500) -> float:
        """
        Calcula percentual de uso em relação ao limite mensal
        
        Args:
            limite_mensal: Limite de requisições por mês (default: 1500)
        
        Returns:
            Percentual de uso (0-100)
        """
        if limite_mensal == 0:
            return 0.0
        
        percentual = (self.uso_atual['requisicoes_mes'] / limite_mensal) * 100
        
        # Ativa/desativa throttling baseado no percentual
        if percentual >= self.threshold_throttling:
            if not self.uso_atual['throttling_ativo']:
                self.uso_atual['throttling_ativo'] = True
                logger.warning(f"⚠️  Throttling ATIVADO - Uso em {percentual:.1f}%")
                self._salvar_estado()
        
        # Desativa sistema se atingir 100%
        if percentual >= 100:
            self.desativar_sistema("Limite mensal de API atingido")
        
        return percentual
    
    def ativar_sistema(self):
        """Ativa o sistema manualmente"""
        self.uso_atual['sistema_ativo'] = True
        self._salvar_estado()
        logger.info("✅ Sistema ATIVADO manualmente")
    
    def desativar_sistema(self, motivo: str = "Desativado pelo administrador"):
        """Desativa o sistema manualmente"""
        self.uso_atual['sistema_ativo'] = False
        self._salvar_estado()
        logger.warning(f"❌ Sistema DESATIVADO: {motivo}")
    
    def resetar_contador_mensal(self):
        """Reseta contador mensal (executar no início de cada mês)"""
        self.uso_atual['requisicoes_mes'] = 0
        self.uso_atual['throttling_ativo'] = False
        self._salvar_estado()
        logger.info("🔄 Contador mensal resetado")
    
    def obter_relatorio(self) -> Dict:
        """Retorna relatório detalhado de uso"""
        agora = datetime.now()
        um_minuto_atras = agora - timedelta(minutes=1)
        
        requisicoes_ultimo_minuto = len([
            req for req in self.uso_atual['requisicoes_por_minuto']
            if isinstance(req, datetime) and req > um_minuto_atras
        ])
        
        return {
            'sistema_ativo': self.uso_atual['sistema_ativo'],
            'throttling_ativo': self.uso_atual['throttling_ativo'],
            'requisicoes_total': self.uso_atual['requisicoes_total'],
            'requisicoes_mes': self.uso_atual['requisicoes_mes'],
            'requisicoes_ultimo_minuto': requisicoes_ultimo_minuto,
            'tokens_usados': self.uso_atual['tokens_usados'],
            'ultima_requisicao': self.uso_atual['ultima_requisicao'],
            'limite_minuto': self.limite_requisicoes_minuto,
            'uso_percentual': self.calcular_uso_percentual(),
            'timestamp': agora.isoformat()
        }
    
    def obter_estatisticas_periodo(self, dias: int = 7) -> Dict:
        """Retorna estatísticas de um período"""
        # Por enquanto retorna stats básicas
        # Pode ser expandido para buscar do banco de dados
        return {
            'periodo_dias': dias,
            'media_requisicoes_dia': self.uso_atual['requisicoes_mes'] / 30,
            'total_periodo': self.uso_atual['requisicoes_mes'],
            'pico_requisicoes_minuto': max(len(self.uso_atual['requisicoes_por_minuto']), 1)
        }
    
    def _carregar_estado(self):
        """Carrega estado persistente do banco de dados"""
        try:
            # Tenta carregar estado salvo
            result = db.client.table('sistema_config').select('*').eq('chave', 'api_monitor_state').execute()
            
            if result.data:
                import json
                estado_salvo = json.loads(result.data[0]['valor'])
                
                # Atualiza apenas campos persistentes
                self.uso_atual['requisicoes_total'] = estado_salvo.get('requisicoes_total', 0)
                self.uso_atual['requisicoes_mes'] = estado_salvo.get('requisicoes_mes', 0)
                self.uso_atual['tokens_usados'] = estado_salvo.get('tokens_usados', 0)
                self.uso_atual['sistema_ativo'] = estado_salvo.get('sistema_ativo', True)
                self.uso_atual['throttling_ativo'] = estado_salvo.get('throttling_ativo', False)
                
                logger.info("📥 Estado do monitor carregado")
        except Exception as e:
            logger.warning(f"⚠️  Não foi possível carregar estado: {e}")
    
    def _salvar_estado(self):
        """Salva estado persistente no banco de dados"""
        try:
            import json
            
            estado = {
                'requisicoes_total': self.uso_atual['requisicoes_total'],
                'requisicoes_mes': self.uso_atual['requisicoes_mes'],
                'tokens_usados': self.uso_atual['tokens_usados'],
                'sistema_ativo': self.uso_atual['sistema_ativo'],
                'throttling_ativo': self.uso_atual['throttling_ativo'],
                'ultima_atualizacao': datetime.now().isoformat()
            }
            
            estado_json = json.dumps(estado)
            
            # Upsert no banco
            db.client.table('sistema_config').upsert({
                'chave': 'api_monitor_state',
                'valor': estado_json
            }).execute()
            
        except Exception as e:
            logger.warning(f"⚠️  Não foi possível salvar estado: {e}")


# Instância global
api_monitor = APIMonitorService()