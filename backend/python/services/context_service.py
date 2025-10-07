"""
Serviço de gerenciamento de contexto (arquivos TXT da Bragantec)
CORRIGIDO: Agora carrega corretamente os TXTs do bucket Supabase
"""
from typing import List, Optional, Tuple
from config.settings import settings
from config.database import db
from utils.logger import logger


class ContextService:
    """Serviço para gerenciar arquivos de contexto da IA"""
    
    def __init__(self):
        self.bucket_name = settings.BUCKET_CONTEXT
        self.contextos_cache = {}
        self._verificar_bucket()
    
    def _verificar_bucket(self):
        """Verifica se o bucket existe"""
        try:
            bucket = db.client.storage.from_(self.bucket_name)
            # Lista arquivos na raiz do bucket (path vazio)
            result = bucket.list(path='')
            
            if result and len(result) > 0:
                logger.info(f"✅ Bucket '{self.bucket_name}' acessível - {len(result)} arquivo(s) encontrado(s)")
                logger.info("📂 Arquivos no bucket:")
                for arquivo in result:
                    nome = arquivo.get('name', 'sem nome')
                    tamanho = arquivo.get('metadata', {}).get('size', 0)
                    logger.info(f"  - {nome} ({tamanho} bytes)")
            else:
                logger.warning(f"⚠️  Bucket '{self.bucket_name}' está vazio ou inacessível")
                
        except Exception as e:
            logger.warning(f"⚠️  Erro ao acessar bucket '{self.bucket_name}': {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def carregar_todos_contextos(self) -> Tuple[bool, Optional[List[str]], Optional[str]]:
        """
        Carrega todos os arquivos TXT do bucket de contexto
        
        Returns:
            Tuple[success, lista_de_textos, error_message]
        """
        try:
            logger.info(f"📥 Carregando contextos do bucket '{self.bucket_name}'...")
            
            # Verifica se já está em cache
            if 'todos' in self.contextos_cache and self.contextos_cache['todos']:
                logger.info(f"📦 Usando {len(self.contextos_cache['todos'])} contexto(s) do cache")
                return True, self.contextos_cache['todos'], None
            
            # Lista todos os arquivos no bucket - IMPORTANTE: usar path='' para raiz
            bucket = db.client.storage.from_(self.bucket_name)
            arquivos = bucket.list(path='')
            
            if not arquivos or len(arquivos) == 0:
                logger.warning("⚠️  Nenhum arquivo encontrado no bucket de contexto")
                logger.warning(f"⚠️  Verifique se os arquivos estão na RAIZ do bucket '{self.bucket_name}'")
                return True, [], None
            
            logger.info(f"📂 Encontrados {len(arquivos)} arquivo(s) no bucket")
            
            contextos = []
            
            for arquivo in arquivos:
                nome = arquivo.get('name', '')
                
                # Processa apenas arquivos TXT
                if nome.lower().endswith('.txt'):
                    logger.info(f"📄 Processando: {nome}")
                    
                    try:
                        # Download do arquivo - usar nome do arquivo diretamente
                        file_bytes = bucket.download(nome)
                        
                        if file_bytes:
                            # Tenta decodificar com diferentes encodings
                            conteudo = None
                            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                                try:
                                    conteudo = file_bytes.decode(encoding)
                                    logger.info(f"✅ Decodificado com {encoding}: {nome} ({len(conteudo)} chars)")
                                    break
                                except UnicodeDecodeError:
                                    continue
                            
                            if conteudo and conteudo.strip():
                                contextos.append(conteudo.strip())
                                logger.info(f"✅ Contexto carregado: {nome}")
                            else:
                                logger.warning(f"⚠️  Arquivo vazio após decodificação: {nome}")
                        else:
                            logger.warning(f"⚠️  Arquivo vazio: {nome}")
                            
                    except Exception as e:
                        logger.warning(f"⚠️  Erro ao processar {nome}: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                        continue
                else:
                    logger.debug(f"⏭️  Ignorando arquivo não-TXT: {nome}")
            
            # Atualiza cache
            if contextos:
                self.contextos_cache['todos'] = contextos
                total_chars = sum(len(c) for c in contextos)
                logger.info(f"✅ Total de {len(contextos)} contexto(s) carregado(s)")
                logger.info(f"📊 Total de caracteres: {total_chars}")
            else:
                logger.warning("⚠️  Nenhum contexto válido foi carregado")
                logger.warning("⚠️  Verifique se os arquivos TXT estão corretos e na raiz do bucket")
            
            return True, contextos, None
            
        except Exception as e:
            error_msg = f"Erro ao carregar contextos: {str(e)}"
            logger.error(f"❌ {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            return False, None, error_msg
    
    def carregar_contexto_por_ano(self, ano: int) -> Tuple[bool, Optional[List[str]], Optional[str]]:
        """Carrega contextos de um ano específico"""
        try:
            logger.info(f"📥 Carregando contextos do ano {ano}...")
            
            bucket = db.client.storage.from_(self.bucket_name)
            # Lista todos os arquivos da raiz
            arquivos = bucket.list(path='')
            
            if not arquivos:
                return True, [], None
            
            contextos = []
            
            # Busca arquivos que contenham o ano no nome
            for arquivo in arquivos:
                nome = arquivo.get('name', '')
                if nome.lower().endswith('.txt') and str(ano) in nome:
                    try:
                        file_bytes = bucket.download(nome)
                        if file_bytes:
                            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                                try:
                                    conteudo = file_bytes.decode(encoding).strip()
                                    if conteudo:
                                        contextos.append(conteudo)
                                        logger.info(f"✅ Carregado: {nome}")
                                    break
                                except UnicodeDecodeError:
                                    continue
                    except Exception as e:
                        logger.warning(f"⚠️  Erro ao carregar {nome}: {e}")
            
            logger.info(f"✅ {len(contextos)} contexto(s) do ano {ano} carregado(s)")
            return True, contextos, None
            
        except Exception as e:
            return False, None, str(e)
    
    def carregar_contexto_especifico(self, nome_arquivo: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Carrega um arquivo de contexto específico"""
        try:
            # Verifica cache
            if nome_arquivo in self.contextos_cache:
                logger.info(f"📦 Contexto recuperado do cache: {nome_arquivo}")
                return True, self.contextos_cache[nome_arquivo], None
            
            # Carrega do Supabase
            bucket = db.client.storage.from_(self.bucket_name)
            file_bytes = bucket.download(nome_arquivo)
            
            if not file_bytes:
                return False, None, "Arquivo não encontrado ou vazio"
            
            # Tenta decodificar
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    conteudo = file_bytes.decode(encoding).strip()
                    if conteudo:
                        self.contextos_cache[nome_arquivo] = conteudo
                        logger.info(f"✅ Contexto carregado: {nome_arquivo}")
                        return True, conteudo, None
                except UnicodeDecodeError:
                    continue
            
            return False, None, "Não foi possível decodificar o arquivo"
            
        except Exception as e:
            error_msg = f"Erro ao carregar contexto: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
    
    def upload_contexto(self, nome_arquivo: str, conteudo: str) -> Tuple[bool, Optional[str]]:
        """Upload de novo contexto"""
        try:
            logger.info(f"⬆️  Fazendo upload de contexto: {nome_arquivo}")
            
            file_bytes = conteudo.encode('utf-8')
            bucket = db.client.storage.from_(self.bucket_name)
            
            bucket.upload(
                path=nome_arquivo,
                file=file_bytes,
                file_options={"content-type": "text/plain; charset=utf-8"}
            )
            
            # Adiciona ao cache
            self.contextos_cache[nome_arquivo] = conteudo
            
            logger.info(f"✅ Contexto adicionado: {nome_arquivo}")
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def deletar_contexto(self, nome_arquivo: str) -> Tuple[bool, Optional[str]]:
        """Deleta arquivo de contexto"""
        try:
            bucket = db.client.storage.from_(self.bucket_name)
            bucket.remove([nome_arquivo])
            
            if nome_arquivo in self.contextos_cache:
                del self.contextos_cache[nome_arquivo]
            
            logger.info(f"✅ Contexto deletado: {nome_arquivo}")
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def listar_contextos_disponiveis(self) -> List[dict]:
        """Lista todos os contextos disponíveis"""
        try:
            bucket = db.client.storage.from_(self.bucket_name)
            # Lista arquivos na raiz do bucket
            arquivos = bucket.list(path='')
            
            contextos = []
            for arquivo in arquivos:
                nome = arquivo.get('name', '')
                if nome.lower().endswith('.txt'):
                    contextos.append({
                        'nome': nome,
                        'tamanho': arquivo.get('metadata', {}).get('size', 0),
                        'atualizado': arquivo.get('updated_at', '')
                    })
            
            logger.info(f"📋 {len(contextos)} contexto(s) TXT disponível(is)")
            return contextos
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar contextos: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def limpar_cache(self):
        """Limpa o cache de contextos"""
        self.contextos_cache = {}
        logger.info("🗑️  Cache de contextos limpo")
    
    def obter_resumo_contextos(self) -> dict:
        """Retorna resumo dos contextos"""
        return {
            'total_cache': len(self.contextos_cache),
            'contextos_em_cache': list(self.contextos_cache.keys()),
            'total_caracteres': sum(len(str(v)) for v in self.contextos_cache.values())
        }
    
    def testar_conexao_bucket(self) -> Tuple[bool, str]:
        """Testa conexão com o bucket"""
        try:
            bucket = db.client.storage.from_(self.bucket_name)
            # Lista arquivos na raiz
            arquivos = bucket.list(path='')
            
            if arquivos and len(arquivos) > 0:
                msg = f"✅ Conexão OK! {len(arquivos)} arquivo(s) encontrado(s)"
                logger.info(msg)
                logger.info("📂 Arquivos encontrados:")
                for arq in arquivos:
                    logger.info(f"  - {arq.get('name', 'sem nome')}")
                return True, msg
            else:
                msg = "⚠️  Bucket acessível mas vazio"
                logger.warning(msg)
                return True, msg
            
        except Exception as e:
            msg = f"❌ Erro na conexão: {str(e)}"
            logger.error(msg)
            import traceback
            logger.error(traceback.format_exc())
            return False, msg


# Instância global
context_service = ContextService()