"""
Serviço de gerenciamento de contexto (arquivos TXT da Bragantec)
"""
from typing import List, Optional, Tuple
from services.supabase_service import supabase_service
from config.settings import settings
from utils.logger import logger


class ContextService:
    """Serviço para gerenciar arquivos de contexto da IA"""
    
    def __init__(self):
        self.bucket_name = settings.BUCKET_CONTEXT
        self.contextos_cache = {}  # Cache em memória dos contextos
    
    def carregar_todos_contextos(self) -> Tuple[bool, Optional[List[str]], Optional[str]]:
        """
        Carrega todos os arquivos TXT do bucket de contexto
        
        Returns:
            Tuple[success, lista_de_textos, error_message]
        """
        try:
            # Lista todos os arquivos no bucket
            arquivos = supabase_service.listar_arquivos("", self.bucket_name)
            
            if not arquivos:
                logger.warning("⚠️  Nenhum arquivo de contexto encontrado")
                return True, [], None
            
            contextos = []
            
            for arquivo in arquivos:
                # Processa apenas arquivos TXT
                if arquivo.get('name', '').endswith('.txt'):
                    sucesso, conteudo, erro = self._carregar_arquivo_txt(arquivo['name'])
                    
                    if sucesso and conteudo:
                        contextos.append(conteudo)
                        logger.info(f"✅ Contexto carregado: {arquivo['name']}")
                    else:
                        logger.warning(f"⚠️  Falha ao carregar: {arquivo['name']} - {erro}")
            
            # Atualiza cache
            self.contextos_cache['todos'] = contextos
            
            logger.info(f"✅ Total de {len(contextos)} contextos carregados")
            return True, contextos, None
            
        except Exception as e:
            error_msg = f"Erro ao carregar contextos: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
    
    def carregar_contexto_por_ano(self, ano: int) -> Tuple[bool, Optional[List[str]], Optional[str]]:
        """
        Carrega contextos de um ano específico
        
        Returns:
            Tuple[success, lista_de_textos, error_message]
        """
        try:
            # Lista arquivos do ano
            path_ano = f"edicao_{ano}/"
            arquivos = supabase_service.listar_arquivos(path_ano, self.bucket_name)
            
            if not arquivos:
                return True, [], None
            
            contextos = []
            
            for arquivo in arquivos:
                if arquivo.get('name', '').endswith('.txt'):
                    nome_completo = f"{path_ano}{arquivo['name']}"
                    sucesso, conteudo, erro = self._carregar_arquivo_txt(nome_completo)
                    
                    if sucesso and conteudo:
                        contextos.append(conteudo)
            
            return True, contextos, None
            
        except Exception as e:
            error_msg = f"Erro ao carregar contextos do ano {ano}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
    
    def carregar_contexto_especifico(self, nome_arquivo: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Carrega um arquivo de contexto específico
        
        Returns:
            Tuple[success, texto, error_message]
        """
        try:
            # Verifica cache primeiro
            if nome_arquivo in self.contextos_cache:
                logger.info(f"📦 Contexto recuperado do cache: {nome_arquivo}")
                return True, self.contextos_cache[nome_arquivo], None
            
            # Carrega do Supabase
            sucesso, conteudo, erro = self._carregar_arquivo_txt(nome_arquivo)
            
            if sucesso and conteudo:
                # Adiciona ao cache
                self.contextos_cache[nome_arquivo] = conteudo
                return True, conteudo, None
            else:
                return False, None, erro
            
        except Exception as e:
            error_msg = f"Erro ao carregar contexto específico: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
    
    def _carregar_arquivo_txt(self, file_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Carrega conteúdo de arquivo TXT
        
        Returns:
            Tuple[success, conteudo, error_message]
        """
        try:
            sucesso, file_content, erro = supabase_service.download_arquivo(
                file_path, 
                self.bucket_name
            )
            
            if not sucesso:
                return False, None, erro
            
            # Decodifica bytes para string
            try:
                texto = file_content.decode('utf-8')
            except UnicodeDecodeError:
                # Tenta outros encodings
                try:
                    texto = file_content.decode('latin-1')
                except:
                    texto = file_content.decode('cp1252')
            
            return True, texto, None
            
        except Exception as e:
            error_msg = f"Erro ao carregar arquivo TXT: {str(e)}"
            return False, None, error_msg
    
    def upload_contexto(self, nome_arquivo: str, conteudo: str) -> Tuple[bool, Optional[str]]:
        """
        Faz upload de novo arquivo de contexto
        
        Returns:
            Tuple[success, error_message]
        """
        try:
            # Converte string para bytes
            file_content = conteudo.encode('utf-8')
            
            # Upload
            sucesso, url, erro = supabase_service.upload_arquivo(
                nome_arquivo,
                file_content,
                self.bucket_name
            )
            
            if sucesso:
                # Adiciona ao cache
                self.contextos_cache[nome_arquivo] = conteudo
                logger.info(f"✅ Novo contexto adicionado: {nome_arquivo}")
                return True, None
            else:
                return False, erro
            
        except Exception as e:
            error_msg = f"Erro ao fazer upload de contexto: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def deletar_contexto(self, nome_arquivo: str) -> Tuple[bool, Optional[str]]:
        """
        Deleta arquivo de contexto
        
        Returns:
            Tuple[success, error_message]
        """
        try:
            sucesso, erro = supabase_service.deletar_arquivo(
                nome_arquivo,
                self.bucket_name
            )
            
            if sucesso:
                # Remove do cache
                if nome_arquivo in self.contextos_cache:
                    del self.contextos_cache[nome_arquivo]
                
                logger.info(f"✅ Contexto deletado: {nome_arquivo}")
                return True, None
            else:
                return False, erro
            
        except Exception as e:
            error_msg = f"Erro ao deletar contexto: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def listar_contextos_disponiveis(self) -> List[dict]:
        """Lista todos os contextos disponíveis"""
        try:
            arquivos = supabase_service.listar_arquivos("", self.bucket_name)
            
            # Filtra apenas TXT e formata
            contextos = []
            for arquivo in arquivos:
                if arquivo.get('name', '').endswith('.txt'):
                    contextos.append({
                        'nome': arquivo['name'],
                        'tamanho': arquivo.get('metadata', {}).get('size', 0),
                        'atualizado': arquivo.get('updated_at', '')
                    })
            
            return contextos
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar contextos: {e}")
            return []
    
    def limpar_cache(self):
        """Limpa o cache de contextos"""
        self.contextos_cache = {}
        logger.info("🗑️  Cache de contextos limpo")
    
    def obter_resumo_contextos(self) -> dict:
        """Retorna resumo dos contextos carregados"""
        return {
            'total_cache': len(self.contextos_cache),
            'contextos_em_cache': list(self.contextos_cache.keys())
        }


# Instância global
context_service = ContextService()