# 🚀 APBIA - Guia de Instalação Completo

Este guia fornece instruções passo a passo para configurar o APBIA do zero.

## Índice
- [Pré-requisitos](#pré-requisitos)
- [Instalação do Backend](#instalação-do-backend)
- [Configuração do Supabase](#configuração-do-supabase)
- [Configuração do Google Gemini](#configuração-do-google-gemini)
- [Instalação do Frontend](#instalação-do-frontend)
- [Primeiro Acesso](#primeiro-acesso)
- [Troubleshooting](#troubleshooting)

---

## Pré-requisitos

### Software Necessário

- **Python 3.10 ou superior**
  - [Download Python](https://www.python.org/downloads/)
  - Verifique: `python --version`

- **pip** (gerenciador de pacotes Python)
  - Geralmente vem com Python
  - Verifique: `pip --version`

- **Git** (opcional, mas recomendado)
  - [Download Git](https://git-scm.com/)
  - Verifique: `git --version`

- **Editor de código** (recomendado)
  - VS Code, PyCharm, ou similar

### Contas Necessárias

1. **Supabase**
   - Crie conta gratuita em [supabase.com](https://supabase.com)
   - Crie um novo projeto

2. **Google AI Studio**
   - Acesse [aistudio.google.com](https://aistudio.google.com)
   - Obtenha API Key gratuita

---

## Instalação do Backend

### Passo 1: Clonar/Baixar o Projeto

```bash
# Se usar Git
git clone <url-do-repositorio>
cd apbia

# OU baixe o ZIP e extraia
```

### Passo 2: Criar Ambiente Virtual

```bash
# Windows
cd backend/python
python -m venv venv
venv\Scripts\activate

# Linux/Mac
cd backend/python
python3 -m venv venv
source venv/bin/activate
```

Você verá `(venv)` no terminal quando ativado.

### Passo 3: Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependências instaladas:**
- flask
- flask-cors
- python-dotenv
- supabase
- google-generativeai
- bcrypt
- pyjwt
- requests

### Passo 4: Configurar Variáveis de Ambiente

1. Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

2. Edite `.env` com suas credenciais:
```bash
# Use seu editor preferido
nano .env
# ou
code .env
```

3. Preencha as variáveis (veja seções abaixo).

---

## Configuração do Supabase

### Passo 1: Criar Projeto

1. Acesse [supabase.com](https://supabase.com)
2. Clique em "New Project"
3. Preencha:
   - **Name**: APBIA
   - **Database Password**: Escolha uma senha forte
   - **Region**: Mais próxima de você
4. Aguarde criação (~2 minutos)

### Passo 2: Obter Credenciais

1. No dashboard do projeto, vá em **Settings** → **API**
2. Copie:
   - **Project URL** (SUPABASE_URL)
   - **anon public** key (SUPABASE_ANON_KEY)
   - **service_role** key (SUPABASE_SECRET_KEY)

3. Adicione ao `.env`:
```env
SUPABASE_URL=https://seuprojetoid.supabase.co
SUPABASE_ANON_KEY=sua-anon-key-aqui
SUPABASE_SECRET_KEY=sua-secret-key-aqui
SUPABASE_DB_PASSWORD=sua-senha-do-banco
```

### Passo 3: Criar Schema do Banco

1. No Supabase, vá em **SQL Editor**
2. Clique em "+ New Query"
3. Cole o conteúdo de `database/schema.sql`
4. Clique em "Run" ou pressione Ctrl+Enter
5. Aguarde mensagem de sucesso

### Passo 4: Inserir Dados Iniciais

1. Nova query no SQL Editor
2. crie um novo adiministrador com as credenciais padrao obs: gere a senha com um gerador de hash online
3. Execute
4. **IMPORTANTE**: Anote as credenciais padrão:
   - Email: `admin@apbia.com`
   - Senha: `Admin@2025`

### Passo 5: Criar Buckets de Storage

1. Vá em **Storage** no menu lateral
2. Crie dois buckets:

**Bucket 1: bragantec-files**
- Nome: `bragantec-files`
- Public: ✅ Sim
- Allowed MIME types: Todos

**Bucket 2: context-files**
- Nome: `context-files`
- Public: ✅ Sim
- Allowed MIME types: `text/plain`

### Passo 6: Upload dos Contextos

1. Faça upload dos arquivos TXT no bucket `context-files`:
   - Cadernos de resumos da Bragantec
   - Formato: `.txt`
   - Encoding: UTF-8

---

## Configuração do Google Gemini

### Passo 1: Obter API Key

1. Acesse [Google AI Studio](https://aistudio.google.com)
2. Faça login com conta Google
3. Clique em "Get API Key"
4. Clique em "Create API Key"
5. Copie a chave

### Passo 2: Adicionar ao .env

```env
GOOGLE_API_KEY=sua-api-key-do-gemini-aqui
```

### Passo 3: Verificar Limites

- **Gratuito**: 60 requisições/minuto, 1500/mês
- **Pago**: Limites maiores
- Verifique em [ai.google.dev](https://ai.google.dev)

---

## Instalação do Frontend

### Passo 1: Verificar Estrutura

O frontend é estático (HTML/CSS/JS), não precisa build.

```
frontend/
├── public/       # Páginas HTML
├── js/           # Scripts
├── css/          # Estilos
└── assets/       # Imagens, ícones
```

### Passo 2: Configurar URL da API

Edite `frontend/js/api.js`:

```javascript
// Linha 5
const API_BASE_URL = 'http://localhost:5000/api';

// Para produção, mude para:
// const API_BASE_URL = 'https://seu-dominio.com/api';
```

### Passo 3: Servir o Frontend

**Opção 1: Python SimpleHTTPServer**
```bash
cd frontend
python -m http.server 8000
```
Acesse: http://localhost:8000/public/

**Opção 2: Live Server (VS Code)**
1. Instale extensão "Live Server"
2. Clique direito em `frontend/public/index.html`
3. Selecione "Open with Live Server"

**Opção 3: Nginx (Produção)**
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    root /caminho/para/frontend;
    
    location / {
        try_files $uri $uri/ /public/index.html;
    }
    
    location /api {
        proxy_pass http://localhost:5000;
    }
}
```

---

## Primeiro Acesso

### Passo 1: Iniciar Backend

```bash
cd backend/python
# Ative o venv se não estiver ativo
python main.py
```

Você verá:
```
🚀 Iniciando APBIA v1.0.0
✅ Conexão com Supabase estabelecida
🌐 Servidor: http://0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

### Passo 2: Verificar API

Abra navegador em: http://localhost:5000/api/health

Deve retornar:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "database": "ok",
  "timestamp": "..."
}
```

### Passo 3: Acessar Frontend

1. Abra: http://localhost:8000/public/
2. Faça login com credenciais padrão:
   - **Email**: admin@apbia.com
   - **Senha**: Admin@2025

### Passo 4: Alterar Senha Padrão

1. Clique no ícone de usuário
2. Vá em "Meu Perfil"
3. Altere a senha do admin
4. **IMPORTANTE**: Guarde a nova senha!

### Passo 5: Criar Primeiro Usuário

1. Acesse painel Admin
2. Clique em "Novo Usuário"
3. Preencha dados:
   - Nome completo
   - Email
   - Senha
   - Tipo: Participante
   - BP: BRGxxxxxxxx (8 dígitos)
4. Clique em "Cadastrar"

### Passo 6: Criar Primeiro Projeto

Via SQL Editor do Supabase (manualmente por enquanto):
```sql
INSERT INTO projetos (nome, descricao, area_projeto, ano_edicao)
VALUES (
  'Meu Primeiro Projeto',
  'Descrição do projeto',
  'Engenharias',
  2025
);
```

Vincular participante:
```sql
INSERT INTO participantes_projetos (participante_id, projeto_id)
VALUES (2, 1);  -- Ajuste os IDs conforme necessário
```

### Passo 7: Testar Chat com IA

1. Faça logout
2. Login como participante
3. Clique no projeto
4. Clique em "Criar Nova Conversa"
5. Digite uma pergunta
6. Aguarde resposta da IA

---

## Configurações Adicionais

### Configurar Logging

Edite `backend/python/config/settings.py`:

```python
# Nível de log
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Arquivo de log
LOG_FILE = Path("storage/logs/apbia.log")
```

Crie pasta de logs:
```bash
mkdir -p storage/logs
```

### Configurar Rate Limiting

Em `backend/python/config/settings.py`:

```python
# Quando ativar throttling (%)
API_RATE_LIMIT = 80

# Requisições por minuto
API_MAX_REQUESTS_PER_MINUTE = 60

# Delay quando throttling ativo (segundos)
API_DELAY_SECONDS = 2
```

### Configurar Segurança

**Mudar SECRET_KEY** (IMPORTANTE):
```python
# Gere chave aleatória
import secrets
print(secrets.token_urlsafe(32))
```

Adicione ao `.env`:
```env
SECRET_KEY=sua-chave-secreta-aleatoria-aqui
```

### Configurar CORS

Em `backend/python/main.py`:

```python
# Para desenvolvimento (permite tudo)
CORS(app)

# Para produção (específico)
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://seu-dominio.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

---

## Deploy em Produção

### Preparação

1. **Mudar DEBUG para False**
```env
DEBUG=False
```

2. **Usar SECRET_KEY forte**
```env
SECRET_KEY=chave-aleatoria-muito-forte
```

3. **Configurar CORS restritivo**

4. **Usar HTTPS sempre**

### Deploy Backend (Heroku)

```bash
# Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Criar app
heroku create apbia-backend

# Configurar variáveis
heroku config:set SUPABASE_URL=...
heroku config:set SUPABASE_ANON_KEY=...
heroku config:set GOOGLE_API_KEY=...
# ... outras variáveis

# Deploy
git push heroku main
```

### Deploy Frontend (Netlify/Vercel)

**Netlify:**
1. Arraste pasta `frontend` para netlify.com/drop
2. Configure variável de ambiente `API_BASE_URL`
3. Pronto!

**Vercel:**
```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel
```

### Deploy Backend (VPS/Servidor)

```bash
# Instalar dependências do sistema
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# Clonar projeto
git clone <repo>
cd apbia/backend/python

# Criar venv
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install gunicorn

# Configurar .env
nano .env

# Testar
gunicorn -w 4 -b 0.0.0.0:5000 main:app

# Criar serviço systemd
sudo nano /etc/systemd/system/apbia.service
```

Conteúdo do `apbia.service`:
```ini
[Unit]
Description=APBIA Backend
After=network.target

[Service]
User=seu-usuario
WorkingDirectory=/caminho/para/backend/python
Environment="PATH=/caminho/para/backend/python/venv/bin"
ExecStart=/caminho/para/backend/python/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 main:app

[Install]
WantedBy=multi-user.target
```

Ativar:
```bash
sudo systemctl start apbia
sudo systemctl enable apbia
sudo systemctl status apbia
```

---

## Troubleshooting

### Problema: ModuleNotFoundError

**Erro:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solução:**
```bash
# Verifique se venv está ativado
which python  # Deve mostrar caminho do venv

# Se não estiver ativado
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# Reinstale dependências
pip install -r requirements.txt
```

### Problema: Conexão com Supabase falha

**Erro:**
```
❌ Erro ao conectar com Supabase
```

**Solução:**
1. Verifique URL no `.env`
2. Verifique chaves no `.env`
3. Verifique se projeto Supabase está ativo
4. Teste conexão: https://seu-projeto.supabase.co

### Problema: API Key do Gemini inválida

**Erro:**
```
❌ Erro ao inicializar modelo Gemini
```

**Solução:**
1. Verifique chave no `.env`
2. Teste em [ai.google.dev/aistudio](https://aistudio.google.com)
3. Gere nova chave se necessário
4. Verifique limites de uso

### Problema: CORS Error no navegador

**Erro:**
```
Access to fetch at 'http://localhost:5000/api/auth/login' from origin 'http://localhost:8000' has been blocked by CORS policy
```

**Solução:**
1. Verifique se Flask-CORS está instalado
2. Em `main.py`, confirme: `CORS(app)`
3. Reinicie backend

### Problema: Token inválido

**Erro:**
```
401 Unauthorized: Token inválido
```

**Solução:**
1. Faça logout e login novamente
2. Limpe localStorage: `localStorage.clear()`
3. Verifique SECRET_KEY no `.env`
4. Verifique se backend foi reiniciado

### Problema: Banco de dados vazio

**Solução:**
1. Execute `database/schema.sql`
2. Execute `database/seeds.sql`
3. Verifique no SQL Editor do Supabase:
```sql
SELECT * FROM tipos_usuario;
SELECT * FROM usuarios;
```

---

## Checklist de Instalação

- [ ] Python 3.10+ instalado
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] Arquivo `.env` configurado
- [ ] Projeto Supabase criado
- [ ] Schema do banco executado
- [ ] Seeds inseridos
- [ ] Buckets de storage criados
- [ ] API Key do Gemini obtida
- [ ] Backend iniciando sem erros
- [ ] Frontend acessível
- [ ] Login funcionando
- [ ] Chat com IA funcionando

---

## Próximos Passos

Após instalação completa:

1. **Customize o sistema**
   - Altere cores em Tailwind
   - Adicione logo personalizado
   - Ajuste textos

2. **Adicione contextos**
   - Upload de cadernos da Bragantec
   - Organizar por edição/ano

3. **Cadastre usuários**
   - Participantes
   - Orientadores

4. **Crie projetos**
   - Vincule participantes
   - Vincule orientadores

5. **Monitore uso**
   - Verifique logs
   - Acompanhe uso da API
   - Ajuste rate limits

---

## Suporte

Para dúvidas:
1. Consulte documentação completa
2. Verifique logs em `storage/logs/apbia.log`
3. Entre em contato com administrador

**Boa sorte com o APBIA! 🚀**