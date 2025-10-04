# 🤖 APBIA - Ajudante de Projetos para Bragantec Baseado em IA

Sistema de inteligência artificial para auxiliar estudantes do IFSP Bragança Paulista na feira de ciências Bragantec.

## 📋 Sobre o Projeto

O APBIA é um chatbot inteligente desenvolvido para ajudar participantes da Bragantec (feira de ciências do IFSP) a:

- 💡 Desenvolver projetos científicos de qualidade
- 🎯 Receber ideias criativas e inovadoras
- 📊 Planejar e organizar projetos
- ❓ Esclarecer dúvidas sobre metodologia científica
- ✅ Obter feedback construtivo

### Tecnologias Utilizadas

**Backend:**
- 🐍 Python 3.10+ (Flask)
- 🤖 Google Gemini 2.5 Flash (IA)
- 🗄️ Supabase (PostgreSQL + Storage)

**Frontend:**
- 🌐 HTML5, CSS3, JavaScript
- 🎨 Tailwind CSS
- 💫 Font Awesome (ícones)

**Arquitetura:**
- 🏗️ MVC (Model-View-Controller)
- 🔐 JWT Authentication
- 📦 RESTful API

## 🚀 Instalação

### Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- Conta no Supabase
- API Key do Google AI Studio

### Passo a Passo

1. **Clone o repositório:**
```bash
git clone <seu-repositorio>
cd apbia
```

2. **Crie ambiente virtual:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instale dependências:**
```bash
cd backend/python
pip install -r requirements.txt
```

4. **Configure variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

5. **Configure o banco de dados:**
- Acesse o Supabase
- Execute o script `database/schema.sql`
- Execute o script `database/seeds.sql` (dados iniciais)

6. **Crie buckets no Supabase Storage:**
- Bucket: `bragantec-files` (público)
- Bucket: `context-files` (público)
- Faça upload dos arquivos TXT de contexto para `context-files`

7. **Inicie o servidor:**
```bash
python main.py
```

O servidor estará rodando em `http://localhost:5000`

## 📁 Estrutura do Projeto

```
apbia/
├── backend/
│   └── python/
│       ├── config/          # Configurações
│       ├── controllers/     # Controllers (lógica de negócio)
│       ├── dao/             # Data Access Objects
│       ├── models/          # Models (entidades)
│       ├── services/        # Serviços (IA, auth, etc)
│       ├── utils/           # Utilitários
│       └── main.py          # API Flask
├── frontend/
│   ├── css/                 # Estilos
│   ├── js/                  # JavaScript
│   └── public/              # Páginas HTML
├── database/
│   ├── schema.sql           # Esquema do banco
│   └── seeds.sql            # Dados iniciais
└── docs/                    # Documentação

```

## 🔐 Autenticação

### Tipos de Usuário

1. **Participante:** Estudante que participa da Bragantec
   - Login: Email + Senha + BP (prontuário)
   - Pode criar projetos e conversar com a IA

2. **Orientador:** Professor orientador
   - Login: Email + Senha
   - Pode visualizar projetos dos orientandos
   - Pode adicionar notas às respostas da IA

3. **Administrador:** Gerenciador do sistema
   - Controle total do sistema
   - Cadastro de usuários
   - Monitoramento e relatórios

### Fluxo de Login

```javascript
POST /api/auth/login
{
  "email": "usuario@email.com",
  "senha": "senha123",
  "bp": "BRG12345678"  // Apenas para participantes
}
```

## 🤖 Usando a IA

### Criar Chat

```javascript
POST /api/chat/criar
Authorization: Bearer <token>
{
  "projeto_id": 1,
  "tipo_ia": "gemini",
  "titulo": "Meu Projeto"
}
```

### Enviar Mensagem

```javascript
POST /api/ia/mensagem
Authorization: Bearer <token>
{
  "chat_id": 1,
  "conteudo": "Como posso melhorar meu projeto sobre energia solar?",
  "usar_thinking": false  // true para perguntas complexas
}
```

### Adicionar Nota do Orientador

```javascript
POST /api/ia/nota-orientador
Authorization: Bearer <token>
{
  "mensagem_id": 123,
  "nota": "Boa sugestão da IA. Recomendo também pesquisar sobre células fotovoltaicas de terceira geração."
}
```

## 📊 Painel Administrativo

O administrador tem acesso a:

- 📈 Relatório de uso da API
- 👥 Gerenciamento de usuários
- 📁 Gerenciamento de projetos
- 🔄 Status do servidor
- ⚙️ Controle do sistema (ativar/desativar IA)

### Endpoints Admin

```javascript
// Status do Sistema
GET /api/admin/sistema/status

// Ativar/Desativar Sistema
POST /api/admin/sistema/toggle
{
  "ativar": true,  // ou false
  "motivo": "Manutenção programada"
}

// Cadastrar Usuário
POST /api/admin/cadastrar-usuario
{
  "nome_completo": "João Silva",
  "email": "joao@email.com",
  "senha": "Senha@123",
  "tipo_usuario": "participante",
  "bp": "BRG12345678"
}
```

## 🎯 Funcionalidades da IA

### Thinking Mode

Para perguntas complexas, a IA usa o "Thinking Mode" do Gemini 2.5 Flash, que permite reflexão profunda antes de responder.

```javascript
// Ativa thinking mode
{
  "usar_thinking": true
}
```

### Contexto Automático

A IA tem acesso aos cadernos de resumos das edições anteriores da Bragantec, carregados automaticamente como contexto.

### Rate Limiting

- Limite: 60 requisições por minuto
- Ao atingir 80% do uso mensal, sistema ativa throttling (delay de 2s)
- Ao atingir 100%, sistema desativa IA automaticamente

## 🔧 Configuração Avançada

### Modificar Limites da API

Edite `backend/python/config/settings.py`:

```python
API_RATE_LIMIT = 80  # % para ativar throttling
API_MAX_REQUESTS_PER_MINUTE = 60
API_DELAY_SECONDS = 2
```

### Personalizar IA

Edite `backend/python/services/gemini_service.py`:

```python
self.generation_config = {
    "temperature": 0.7,  # Criatividade (0-1)
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}
```

## 📱 Frontend

### Páginas Disponíveis

- `index.html` - Página de login
- `chat.html` - Interface de chat
- `projetos.html` - Gerenciamento de projetos
- `perfil.html` - Perfil do usuário
- `admin.html` - Painel administrativo

### Estrutura CSS

Usando Tailwind CSS via CDN. Classes principais:

- `bg-blue-600` - Cor azul padrão
- `hover:bg-blue-700` - Hover states
- `rounded-lg` - Bordas arredondadas
- `shadow-lg` - Sombras

## 🐛 Troubleshooting

### Erro: "Módulo não encontrado"
```bash
pip install -r requirements.txt
```

### Erro: "Conexão com banco de dados falhou"
- Verifique as credenciais do Supabase no `.env`
- Confirme que o banco está ativo no Supabase

### Erro: "API Key inválida"
- Verifique a `GOOGLE_API_KEY` no `.env`
- Confirme que a key está ativa no Google AI Studio

### IA não responde
- Verifique se sistema está ativo: `GET /api/ia/status`
- Verifique se não atingiu limite da API
- Admin pode reativar em `/api/admin/sistema/toggle`

## 📚 Documentação Adicional

- [API.md](docs/API.md) - Documentação completa da API
- [DATABASE.md](docs/DATABASE.md) - Estrutura do banco de dados
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitetura do sistema
- [SETUP.md](docs/SETUP.md) - Guia detalhado de instalação

## 🔒 Segurança

**⚠️ IMPORTANTE:**

1. **NUNCA** commite o arquivo `.env` com credenciais reais
2. Use senhas fortes para todos os usuários
3. Mantenha as API Keys em segredo
4. Configure CORS adequadamente para produção
5. Use HTTPS em produção

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é desenvolvido para o IFSP Bragança Paulista.

## 👥 Autores

Desenvolvido para a Bragantec - Feira de Ciências do IFSP

## 📞 Suporte

Para dúvidas e suporte, contate o administrador do sistema.

---

**APBIA** - Auxiliando a inovação na Bragantec 🚀🔬