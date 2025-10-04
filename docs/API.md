# 📚 APBIA - Documentação da API

## Índice
- [Autenticação](#autenticação)
- [Chats](#chats)
- [IA / Mensagens](#ia--mensagens)
- [Projetos](#projetos)
- [Usuários](#usuários)
- [Admin](#admin)
- [Códigos de Status](#códigos-de-status)

---

## Base URL
```
http://localhost:5000/api
```

## Formato de Resposta Padrão

### Sucesso
```json
{
  "success": true,
  "message": "Mensagem de sucesso",
  "data": {},
  "timestamp": "2025-01-15T10:30:00"
}
```

### Erro
```json
{
  "success": false,
  "message": "Mensagem de erro",
  "error": "Detalhes do erro",
  "timestamp": "2025-01-15T10:30:00"
}
```

---

## Autenticação

### Login
**POST** `/auth/login`

Realiza login no sistema.

**Body:**
```json
{
  "email": "usuario@email.com",
  "senha": "Senha@123",
  "bp": "BRG12345678"  // Opcional: apenas para participantes
}
```

**Resposta (200):**
```json
{
  "success": true,
  "message": "Login realizado com sucesso",
  "data": {
    "id": 1,
    "nome_completo": "João Silva",
    "email": "joao@email.com",
    "tipo_usuario_nome": "participante",
    "bp": "BRG12345678",
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

### Validar Token
**GET** `/auth/validate`

Valida o token JWT atual.

**Headers:**
```
Authorization: Bearer {token}
```

**Resposta (200):**
```json
{
  "success": true,
  "message": "Token válido",
  "data": {
    "id": 1,
    "nome_completo": "João Silva",
    "email": "joao@email.com"
  }
}
```

### Alterar Senha
**POST** `/auth/alterar-senha`

Altera a senha do usuário logado.

**Headers:**
```
Authorization: Bearer {token}
```

**Body:**
```json
{
  "senha_atual": "SenhaAntiga@123",
  "nova_senha": "SenhaNova@123"
}
```

---

## Chats

### Criar Chat
**POST** `/chat/criar`

Cria uma nova conversa com a IA.

**Headers:**
```
Authorization: Bearer {token}
```

**Body:**
```json
{
  "projeto_id": 1,
  "tipo_ia": "gemini",
  "titulo": "Meu Projeto de Energia Solar"
}
```

**Resposta (201):**
```json
{
  "success": true,
  "message": "Chat criado com sucesso",
  "data": {
    "id": 5,
    "projeto_id": 1,
    "tipo_ia_id": 1,
    "titulo": "Meu Projeto de Energia Solar",
    "data_criacao": "2025-01-15T10:30:00"
  }
}
```

### Buscar Chat
**GET** `/chat/{chat_id}?incluir_mensagens=true`

Busca detalhes de um chat.

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
- `incluir_mensagens` (boolean, opcional): Se deve incluir mensagens. Default: `true`

**Resposta (200):**
```json
{
  "success": true,
  "message": "Chat encontrado",
  "data": {
    "id": 5,
    "titulo": "Meu Projeto",
    "projeto_nome": "Energia Solar",
    "mensagens": [...]
  }
}
```

### Listar Chats de um Projeto
**GET** `/chat/projeto/{projeto_id}`

Lista todos os chats de um projeto.

**Headers:**
```
Authorization: Bearer {token}
```

**Resposta (200):**
```json
{
  "success": true,
  "message": "3 chat(s) encontrado(s)",
  "data": [
    {
      "id": 1,
      "titulo": "Chat 1",
      "total_mensagens": 15
    }
  ]
}
```

### Deletar Chat
**DELETE** `/chat/{chat_id}`

Deleta um chat e todas suas mensagens.

**Headers:**
```
Authorization: Bearer {token}
```

---

## IA / Mensagens

### Enviar Mensagem
**POST** `/ia/mensagem`

Envia mensagem para a IA e recebe resposta.

**Headers:**
```
Authorization: Bearer {token}
```

**Body:**
```json
{
  "chat_id": 5,
  "conteudo": "Como posso melhorar meu projeto de energia solar?",
  "usar_thinking": false
}
```

**Resposta (200):**
```json
{
  "success": true,
  "message": "Resposta gerada com sucesso",
  "data": {
    "mensagem_usuario": {...},
    "mensagem_ia": {
      "id": 42,
      "conteudo": "Para melhorar seu projeto...",
      "data_envio": "2025-01-15T10:31:00"
    },
    "uso_api": {
      "sistema_ativo": true,
      "requisicoes_mes": 45
    }
  }
}
```

### Adicionar Nota do Orientador
**POST** `/ia/nota-orientador`

Adiciona nota do orientador a uma resposta da IA.

**Headers:**
```
Authorization: Bearer {token}
```

**Permissões:** Apenas orientadores e admins

**Body:**
```json
{
  "mensagem_id": 42,
  "nota": "Ótima sugestão! Também considere células fotovoltaicas de terceira geração."
}
```

### Status da API
**GET** `/ia/status`

Retorna status atual da API do Gemini.

**Headers:**
```
Authorization: Bearer {token}
```

**Resposta (200):**
```json
{
  "success": true,
  "data": {
    "sistema_ativo": true,
    "throttling_ativo": false,
    "requisicoes_mes": 45,
    "uso_percentual": 30.5
  }
}
```

---

## Projetos

### Listar Projetos
**GET** `/projetos`

Lista todos os projetos do usuário.

**Headers:**
```
Authorization: Bearer {token}
```

**Resposta (200):**
```json
{
  "success": true,
  "message": "3 projeto(s) encontrado(s)",
  "data": [
    {
      "id": 1,
      "nome": "Energia Solar",
      "descricao": "Projeto sobre energia renovável",
      "area_projeto": "Engenharias",
      "ano_edicao": 2025,
      "participantes": [...],
      "orientadores": [...]
    }
  ]
}
```

### Buscar Projeto
**GET** `/projetos/{projeto_id}`

Busca detalhes de um projeto específico.

**Headers:**
```
Authorization: Bearer {token}
```

---

## Usuários

### Meu Perfil
**GET** `/usuario/perfil`

Retorna perfil do usuário logado.

**Headers:**
```
Authorization: Bearer {token}
```

**Resposta (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "nome_completo": "João Silva",
    "email": "joao@email.com",
    "tipo_usuario_nome": "participante",
    "bp": "BRG12345678",
    "data_criacao": "2025-01-01T00:00:00"
  }
}
```

---

## Admin

**ATENÇÃO:** Todas as rotas admin requerem privilégios de administrador.

### Cadastrar Usuário
**POST** `/admin/cadastrar-usuario`

Cadastra novo usuário no sistema.

**Headers:**
```
Authorization: Bearer {token}
```

**Body:**
```json
{
  "nome_completo": "Maria Santos",
  "email": "maria@email.com",
  "senha": "Senha@123",
  "tipo_usuario": "participante",
  "bp": "BRG87654321"
}
```

### Status do Sistema
**GET** `/admin/sistema/status`

Retorna relatório completo do sistema.

**Headers:**
```
Authorization: Bearer {token}
```

**Resposta (200):**
```json
{
  "success": true,
  "data": {
    "usuarios": {
      "total": 15,
      "por_tipo": {
        "participante": 10,
        "orientador": 4,
        "admin": 1
      }
    },
    "projetos": {
      "total": 8
    },
    "api": {...},
    "sistema": {
      "ativo": true
    }
  }
}
```

### Ativar/Desativar Sistema
**POST** `/admin/sistema/toggle`

Ativa ou desativa o sistema.

**Headers:**
```
Authorization: Bearer {token}
```

**Body:**
```json
{
  "ativar": false,
  "motivo": "Manutenção programada"
}
```

---

## Códigos de Status

| Código | Significado |
|--------|-------------|
| 200 | OK - Requisição bem-sucedida |
| 201 | Created - Recurso criado com sucesso |
| 400 | Bad Request - Dados inválidos |
| 401 | Unauthorized - Token inválido ou ausente |
| 403 | Forbidden - Sem permissão |
| 404 | Not Found - Recurso não encontrado |
| 500 | Internal Server Error - Erro no servidor |
| 503 | Service Unavailable - Sistema em manutenção |

---

## Exemplos de Uso

### JavaScript (Fetch)
```javascript
// Login
const response = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'usuario@email.com',
    senha: 'Senha@123'
  })
});

const data = await response.json();
const token = data.data.token;

// Enviar mensagem
const responseIA = await fetch('http://localhost:5000/api/ia/mensagem', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    chat_id: 1,
    conteudo: 'Minha pergunta...'
  })
});
```

### Python (Requests)
```python
import requests

# Login
response = requests.post('http://localhost:5000/api/auth/login', json={
    'email': 'usuario@email.com',
    'senha': 'Senha@123'
})

token = response.json()['data']['token']

# Enviar mensagem
response = requests.post(
    'http://localhost:5000/api/ia/mensagem',
    json={
        'chat_id': 1,
        'conteudo': 'Minha pergunta...'
    },
    headers={'Authorization': f'Bearer {token}'}
)
```

---

## Notas Importantes

1. **Autenticação**: Todas as rotas (exceto `/auth/login`) requerem token JWT no header `Authorization`
2. **Rate Limiting**: Máximo de 60 requisições por minuto
3. **Throttling**: Sistema ativa delay automático ao atingir 80% do limite mensal
4. **CORS**: Configurado para aceitar requisições do frontend
5. **Timestamps**: Todos os timestamps seguem ISO 8601 format
6. **BP**: Apenas participantes precisam de BP para login