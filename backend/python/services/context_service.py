"""
Serviço de gerenciamento de contexto (arquivos TXT da Bragantec)
"""
from typing import List, Optional, Tuple
from config.settings import settings
from config.database import db
from utils.logger import logger


class ContextService:
    """Serviço para gerenciar arquivos de contexto da IA"""
    
    def __init__(self):
        self.bucket_name = settings.BUCKET_CONTEXT
        self.contextos_cache = {}  # Cache em memória dos contextos
        self._verificar_bucket()
    
    def _verificar_bucket(self):
        """Verifica se o bucket existe"""
        try:
            # Tenta listar arquivos para verificar acesso
            bucket = db.get_storage().from_(self.bucket_name)
            result = bucket.list()
            logger.info(f"✅ Bucket '{self.bucket_name}' acessível - {len(result)} arquivo(s) encontrado(s)")
        except Exception as e:
            logger.warning(f"⚠️  Erro ao acessar bucket '{self.bucket_name}': {e}")
    
    def carregar_todos_contextos(self) -> Tuple[bool, Optional[List[str]], Optional[str]]:
        """
        Carrega todos os arquivos TXT do bucket de contexto
        
        Returns:
            Tuple[success, lista_de_textos, error_message]
        """
        try:
            logger.info(f"📥 Carregando contextos do bucket '{self.bucket_name}'...")
            
            # Lista todos os arquivos no bucket
            bucket = db.get_storage().from_(self.bucket_name)
            arquivos = bucket.list()
            
            if not arquivos:
                logger.warning("⚠️  Nenhum arquivo encontrado no bucket de contexto")
                return True, [], None
            
            logger.info(f"📂 Encontrados {len(arquivos)} arquivo(s) no bucket")
            
            contextos = []
            
            for arquivo in arquivos:
                nome = arquivo.get('name', '')
                
                # Processa apenas arquivos TXT
                if nome.endswith('.txt'):
                    logger.info(f"📄 Processando: {nome}")
                    sucesso, conteudo, erro = self._carregar_arquivo_txt(nome)
                    
                    if sucesso and conteudo:
                        contextos.append(conteudo)
                        logger.info(f"✅ Contexto carregado: {nome} ({len(conteudo)} caracteres)")
                    else:
                        logger.warning(f"⚠️  Falha ao carregar: {nome} - {erro}")
                else:
                    logger.debug(f"⏭️  Ignorando arquivo não-TXT: {nome}")
            
            # Atualiza cache
            self.contextos_cache['todos'] = contextos
            
            logger.info(f"✅ Total de {len(contextos)} contexto(s) carregado(s) com sucesso")
            logger.info(f"📊 Total de caracteres carregados: {sum(len(c) for c in contextos)}")
            
            return True, contextos, None
            
        except Exception as e:
            error_msg = f"Erro ao carregar contextos: {str(e)}"
            logger.error(f"❌ {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            return False, None, error_msg
    
    def carregar_contexto_por_ano(self, ano: int) -> Tuple[bool, Optional[List[str]], Optional[str]]:
        """
        Carrega contextos de um ano específico
        
        Returns:
            Tuple[success, lista_de_textos, error_message]
        """
        try:
            logger.info(f"📥 Carregando contextos do ano {ano}...")
            
            # Lista arquivos do ano
            path_ano = f"edicao_{ano}/"
            bucket = db.get_storage().from_(self.bucket_name)
            arquivos = bucket.list(path_ano)
            
            if not arquivos:
                logger.info(f"ℹ️  Nenhum arquivo encontrado para o ano {ano}")
                return True, [], None
            
            contextos = []
            
            for arquivo in arquivos:
                nome = arquivo.get('name', '')
                if nome.endswith('.txt'):
                    nome_completo = f"{path_ano}{nome}"
                    sucesso, conteudo, erro = self._carregar_arquivo_txt(nome_completo)
                    
                    if sucesso and conteudo:
                        contextos.append(conteudo)
                        logger.info(f"✅ Carregado: {nome_completo}")
            
            logger.info(f"✅ {len(contextos)} contexto(s) do ano {ano} carregado(s)")
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
                logger.info(f"✅ Contexto carregado e adicionado ao cache: {nome_arquivo}")
                return True, conteudo, None
            else:
                return False, None, erro
            
        except Exception as e:
            error_msg = f"Erro ao carregar contexto específico: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
    
    def _carregar_arquivo_txt(self, file_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Carrega conteúdo de arquivo TXT do Supabase
        
        Returns:
            Tuple[success, conteudo, error_message]
        """
        try:
            logger.info(f"⬇️  Baixando arquivo: {file_path}")
            
            bucket = db.get_storage().from_(self.bucket_name)
            
            # Download do arquivo
            file_content = bucket.download(file_path)
            
            if not file_content:
                return False, None, "Arquivo vazio ou não encontrado"
            
            # Decodifica bytes para string
            try:
                texto = file_content.decode('utf-8')
                logger.info(f"✅ Arquivo decodificado (UTF-8): {len(texto)} caracteres")
            except UnicodeDecodeError:
                # Tenta outros encodings
                try:
                    texto = file_content.decode('latin-1')
                    logger.info(f"✅ Arquivo decodificado (Latin-1): {len(texto)} caracteres")
                except:
                    texto = file_content.decode('cp1252')
                    logger.info(f"✅ Arquivo decodificado (CP1252): {len(texto)} caracteres")
            
            # Remove espaços em branco excessivos
            texto = texto.strip()
            
            if not texto:
                return False, None, "Arquivo está vazio após processamento"
            
            return True, texto, None
            
        except Exception as e:
            error_msg = f"Erro ao carregar arquivo TXT '{file_path}': {str(e)}"
            logger.error(f"❌ {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            return False, None, error_msg
    
    def upload_contexto(self, nome_arquivo: str, conteudo: str) -> Tuple[bool, Optional[str]]:
        """
        Faz upload de novo arquivo de contexto
        
        Returns:
            Tuple[success, error_message]
        """
        try:
            logger.info(f"⬆️  Fazendo upload de contexto: {nome_arquivo}")
            
            # Converte string para bytes
            file_content = conteudo.encode('utf-8')
            
            bucket = db.get_storage().from_(self.bucket_name)
            
            # Upload
            bucket.upload(
                path=nome_arquivo,
                file=file_content,
                file_options={"content-type": "text/plain; charset=utf-8"}
            )
            
            # Adiciona ao cache
            self.contextos_cache[nome_arquivo] = conteudo
            
            logger.info(f"✅ Novo contexto adicionado: {nome_arquivo}")
            return True, None
            
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
            bucket = db.get_storage().from_(self.bucket_name)
            bucket.remove([nome_arquivo])
            
            # Remove do cache
            if nome_arquivo in self.contextos_cache:
                del self.contextos_cache[nome_arquivo]
            
            logger.info(f"✅ Contexto deletado: {nome_arquivo}")
            return True, None
            
        except Exception as e:
            error_msg = f"Erro ao deletar contexto: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def listar_contextos_disponiveis(self) -> List[dict]:
        """Lista todos os contextos disponíveis no bucket"""
        try:
            bucket = db.get_storage().from_(self.bucket_name)
            arquivos = bucket.list()
            
            # Filtra apenas TXT e formata
            contextos = []
            for arquivo in arquivos:
                nome = arquivo.get('name', '')
                if nome.endswith('.txt'):
                    contextos.append({
                        'nome': nome,
                        'tamanho': arquivo.get('metadata', {}).get('size', 0),
                        'atualizado': arquivo.get('updated_at', '')
                    })
            
            logger.info(f"📋 {len(contextos)} contexto(s) TXT disponível(is)")
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
            'contextos_em_cache': list(self.contextos_cache.keys()),
            'total_caracteres': sum(len(str(v)) for v in self.contextos_cache.values())
        }
    
    def testar_conexao_bucket(self) -> Tuple[bool, str]:
        """Testa conexão com o bucket"""
        try:
            bucket = db.get_storage().from_(self.bucket_name)
            arquivos = bucket.list()
            
            msg = f"✅ Conexão OK! {len(arquivos)} arquivo(s) encontrado(s)"
            logger.info(msg)
            return True, msg
            
        except Exception as e:
            msg = f"❌ Erro na conexão: {str(e)}"
            logger.error(msg)
            return False, msg


# Instância global
context_service = ContextService()