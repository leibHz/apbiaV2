# 🏗️ APBIA - Arquitetura do Sistema

## Visão Geral

O APBIA é um sistema web full-stack desenvolvido para auxiliar estudantes da Bragantec (feira de ciências do IFSP Bragança Paulista) no desenvolvimento de projetos científicos através de IA.

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐              │
│  │   HTML5   │  │    CSS3   │  │JavaScript │              │
│  │           │  │ Tailwind  │  │ Vanilla   │              │
│  └───────────┘  └───────────┘  └───────────┘              │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
                         │
┌────────────────────────▼────────────────────────────────────┐
│                     BACKEND (Flask)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              API Layer (main.py)                     │   │
│  │  - Rotas HTTP                                        │   │
│  │  - Middleware (Auth, CORS)                           │   │
│  │  - Error Handling                                    │   │
│  └───────────┬──────────────────────────┬────────────┬──┘   │
│              │                          │            │      │
│  ┌───────────▼────────┐  ┌──────────────▼───┐  ┌────▼───┐  │
│  │   CONTROLLERS      │  │    SERVICES      │  │  UTILS │  │
│  │  - Chat            │  │  - Auth          │  │ Logger │  │
│  │  - Gemini          │  │  - Gemini AI     │  │Helpers │  │
│  │  - Admin           │  │  - Context       │  │Validat.│  │
│  │                    │  │  - Supabase      │  │        │  │
│  └───────────┬────────┘  │  - API Monitor   │  └────────┘  │
│              │            └──────────────────┘              │
│  ┌───────────▼────────┐                                     │
│  │       MODELS       │                                     │
│  │  - Usuario         │                                     │
│  │  - Projeto         │                                     │
│  │  - Chat            │                                     │
│  │  - Mensagem        │                                     │
│  └───────────┬────────┘                                     │
│              │                                               │
│  ┌───────────▼────────┐                                     │
│  │        DAO         │                                     │
│  │  Data Access Obj   │                                     │
│  └───────────┬────────┘                                     │
└──────────────┼─────────────────────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌───────▼──────┐
│  Supabase  │    │ Google Gemini│
│  - Auth    │    │      AI      │
│  - Database│    │  - 2.5 Flash │
│  - Storage │    │  - Thinking  │
└────────────┘    └──────────────┘
```

## Camadas da Aplicação

### 1. Frontend (Presentation Layer)

**Tecnologias:**
- HTML5
- Tailwind CSS (via CDN)
- JavaScript Vanilla
- Font Awesome (ícones)

**Estrutura:**
```
frontend/
├── public/          # Páginas HTML
│   ├── index.html   # Login
│   ├── projetos.html
│   ├── chat.html
│   ├── perfil.html
│   └── admin.html
├── js/              # Scripts
│   ├── api.js       # Cliente API
│   ├── auth.js      # Autenticação
│   ├── chat.js      # Chat com IA
│   ├── admin.js     # Painel admin
│   └── utils.js     # Utilitários
└── css/             # Estilos customizados
```

**Características:**
- SPA (Single Page Application) sem framework
- Comunicação via REST API
- Estado gerenciado via localStorage
- Responsivo (mobile-first)

### 2. Backend (Business Logic Layer)

**Tecnologias:**
- Python 3.10+
- Flask (web framework)
- Flask-CORS
- python-dotenv

**Arquitetura MVC:**

#### Models (Entidades)
Representam os dados do sistema:
- `Usuario`: Dados do usuário
- `Projeto`: Projetos da Bragantec
- `Chat`: Conversas com IA
- `Mensagem`: Mensagens trocadas
- `Arquivo`: Arquivos anexados

#### Controllers
Gerenciam a lógica de negócio:
- `ChatController`: CRUD de chats
- `GeminiController`: Interação com IA
- `AdminController`: Funções administrativas

#### Services
Implementam lógica complexa:
- `AuthService`: Autenticação e autorização
- `GeminiService`: Integração com Gemini AI
- `ContextService`: Gerenciamento de contextos
- `SupabaseService`: Operações de storage
- `APIMonitorService`: Monitoramento de uso

#### DAOs (Data Access Objects)
Abstraem acesso ao banco:
- `BaseDAO`: Operações CRUD base
- `UsuarioDAO`, `ProjetoDAO`, etc.

#### Utils
Funções auxiliares:
- `Logger`: Sistema de logs
- `Helpers`: Funções utilitárias
- `Validators`: Validações

### 3. Database Layer

**Supabase (PostgreSQL)**

**Tabelas Principais:**
```
usuarios
├── id (PK)
├── nome_completo
├── email (UNIQUE)
├── senha_hash
├── tipo_usuario_id (FK)
└── bp (UNIQUE)

projetos
├── id (PK)
├── nome
├── descricao
├── area_projeto
└── ano_edicao

chats
├── id (PK)
├── projeto_id (FK)
├── tipo_ia_id (FK)
└── titulo

mensagens
├── id (PK)
├── chat_id (FK)
├── usuario_id (FK, nullable)
├── conteudo
└── e_nota_orientador
```

**Relacionamentos:**
- Usuario N:N Projeto (participantes_projetos)
- Usuario N:N Projeto (orientadores_projetos)
- Projeto 1:N Chat
- Chat 1:N Mensagem
- Mensagem 1:N Arquivo

### 4. External Services

#### Google Gemini AI
- **Modelo**: gemini-2.5-flash
- **Funcionalidades**:
  - Geração de texto
  - Thinking mode
  - Processamento de documentos
  - Contexto multimodal

#### Supabase
- **Database**: PostgreSQL gerenciado
- **Storage**: Armazenamento de arquivos
- **Auth**: (não usado, JWT local)

## Fluxos Principais

### Fluxo de Autenticação

```
1. Usuário → Login (email + senha + BP*)
   ↓
2. Backend valida credenciais
   ↓
3. Gera JWT Token
   ↓
4. Retorna Token + Dados do usuário
   ↓
5. Frontend armazena em localStorage
   ↓
6. Token enviado em todas requisições
```

### Fluxo de Chat com IA

```
1. Usuário envia mensagem
   ↓
2. Frontend → POST /api/ia/mensagem
   ↓
3. Backend:
   - Verifica rate limit
   - Salva mensagem do usuário
   - Carrega contextos da Bragantec
   - Carrega histórico do chat
   ↓
4. Gemini AI processa e gera resposta
   ↓
5. Backend salva resposta da IA
   ↓
6. Retorna ambas mensagens
   ↓
7. Frontend exibe no chat
```

### Fluxo de Monitoramento

```
API Monitor Service (em memória + persistente)
   ↓
1. Registra cada requisição
   ↓
2. Calcula uso percentual
   ↓
3. Se >= 80% → Ativa throttling
   ↓
4. Se >= 100% → Desativa sistema
   ↓
5. Admin pode reativar manualmente
```

## Padrões de Projeto Utilizados

### 1. MVC (Model-View-Controller)
- **Model**: Entidades + DAOs
- **View**: Frontend (HTML/JS)
- **Controller**: Controllers do Flask

### 2. DAO (Data Access Object)
- Abstração do acesso ao banco de dados
- Operações CRUD genéricas no BaseDAO
- DAOs específicos estendem BaseDAO

### 3. Service Layer
- Lógica de negócio complexa separada
- Reutilização entre controllers
- Testabilidade

### 4. Singleton
- Database connection
- Services (auth, gemini, context)
- API Monitor

### 5. Factory Pattern
- Criação de modelos a partir de dicts
- `from_dict()` methods

## Segurança

### Autenticação
- **JWT (JSON Web Tokens)**
- Algoritmo: HS256
- Expiração: 24 horas
- Payload: user_id, tipo_usuario

### Senhas
- **bcrypt** para hashing
- 12 rounds (BCRYPT_ROUNDS)
- Validação: min 8 chars, maiúsc, minúsc, número

### Autorização
- Middleware `@require_auth`
- Middleware `@require_admin`
- Verificação de permissões em controllers

### Validações
- Email: regex pattern
- BP: BRGxxxxxxxx (8 dígitos)
- Senha: complexidade mínima
- Inputs: sanitização e escape

### CORS
- Configurado via Flask-CORS
- Headers permitidos
- Métodos permitidos

## Performance

### Caching
- Contextos em memória (ContextService)
- Evita reler arquivos TXT repetidamente

### Rate Limiting
- 60 requisições/minuto por IP
- Throttling automático em 80%
- Sistema desativa em 100%

### Database
- Índices em campos frequentes
- Foreign keys com CASCADE
- Funções PL/pgSQL para queries complexas

### Frontend
- Assets via CDN (Tailwind, Font Awesome)
- Lazy loading de imagens
- Debounce em inputs

## Escalabilidade

### Horizontal
- Backend stateless (JWT)
- Pode rodar múltiplas instâncias
- Load balancer na frente

### Vertical
- Supabase gerenciado (auto-scale)
- Gemini AI gerenciado (sem limites de infra)

### Limitações Atuais
- API Monitor em memória (usar Redis/Memcached)
- Context cache em memória (usar Redis)
- Sem fila de mensagens

## Monitoramento

### Logs
- Sistema de logging estruturado
- Níveis: INFO, WARNING, ERROR, CRITICAL
- Arquivo: `storage/logs/apbia.log`
- Console output

### Métricas
- Requisições totais
- Requisições por minuto
- Uso da API (percentual)
- Sistema ativo/inativo

### Health Checks
- `/api/health` - Status geral
- Database health check
- API availability

## Deploy

### Ambiente de Desenvolvimento
```bash
# Backend
cd backend/python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Frontend
# Servir com qualquer servidor web estático
# Ex: python -m http.server 8000
```

### Ambiente de Produção
```bash
# Backend com Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app

# Frontend com Nginx
# Servir pasta frontend/ como static files
```

### Variáveis de Ambiente
Ver arquivo `.env` para configurações necessárias.

## Melhorias Futuras

### Backend
- [ ] Redis para cache distribuído
- [ ] Celery para tasks assíncronas
- [ ] WebSockets para chat em tempo real
- [ ] API versioning
- [ ] Rate limiting por usuário (não IP)
- [ ] Logs estruturados (JSON)
- [ ] Metrics export (Prometheus)

### Frontend
- [ ] Migrar para React/Vue
- [ ] PWA (Progressive Web App)
- [ ] Offline mode
- [ ] Service Workers
- [ ] Notificações push

### Infraestrutura
- [ ] Docker containers
- [ ] Kubernetes orchestration
- [ ] CI/CD pipeline
- [ ] Automated tests
- [ ] Load testing

### Features
- [ ] Upload de imagens para IA
- [ ] Export de conversas em PDF
- [ ] Sugestões automáticas de projetos
- [ ] Dashboard com analytics
- [ ] Integração com calendário escolar