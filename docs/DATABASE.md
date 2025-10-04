# 🗄️ APBIA - Documentação do Banco de Dados

## Visão Geral

O APBIA utiliza **PostgreSQL** através do **Supabase** como banco de dados gerenciado.

## Diagrama Entidade-Relacionamento

```
┌─────────────────┐
│ tipos_usuario   │
│─────────────────│
│ id (PK)         │
│ nome (UNIQUE)   │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────────────────┐
│ usuarios                     │
│──────────────────────────────│
│ id (PK)                      │
│ nome_completo                │
│ email (UNIQUE)               │
│ senha_hash                   │
│ tipo_usuario_id (FK)         │
│ bp (UNIQUE, nullable)        │
│ data_criacao                 │
│ data_atualizacao             │
└─┬──────────────────────────┬┘
  │                          │
  │ N:N                      │ N:N
  │ (participantes)          │ (orientadores)
  │                          │
  │    ┌─────────────────┐   │
  └────┤ projetos        │───┘
       │─────────────────│
       │ id (PK)         │
       │ nome            │
       │ descricao       │
       │ area_projeto    │
       │ ano_edicao      │
       │ data_criacao    │
       └────────┬────────┘
                │
                │ 1:N
                │
       ┌────────▼────────┐       ┌─────────────┐
       │ chats           │───┐   │ tipos_ia    │
       │─────────────────│   │   │─────────────│
       │ id (PK)         │   └──▶│ id (PK)     │
       │ projeto_id (FK) │       │ nome (UNQ)  │
       │ tipo_ia_id (FK) │       └─────────────┘
       │ titulo          │
       │ data_criacao    │
       └────────┬────────┘
                │
                │ 1:N
                │
       ┌────────▼─────────────────┐
       │ mensagens                 │
       │───────────────────────────│
       │ id (PK)                   │
       │ chat_id (FK)              │
       │ usuario_id (FK, nullable) │◀─┐
       │ conteudo                  │  │
       │ e_nota_orientador         │  │
       │ data_envio                │  │
       └────────┬──────────────────┘  │
                │                     │
                │ 1:N                 │ N:1
                │                     │
       ┌────────▼─────────┐           │
       │ arquivos_chat    │           │
       │──────────────────│           │
       │ id (PK)          │           │
       │ mensagem_id (FK) │───────────┘
       │ nome_arquivo     │
       │ url_arquivo      │
       │ tipo_arquivo     │
       │ tamanho_bytes    │
       │ data_upload      │
       └──────────────────┘
```

## Tabelas Detalhadas

### tipos_usuario

Tipos de usuário no sistema.

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| id | bigint | PK, IDENTITY | Identificador único |
| nome | varchar | NOT NULL, UNIQUE | Nome do tipo (participante, orientador, admin) |

**Dados Padrão:**
```sql
- participante
- orientador  
- admin
```

---

### usuarios

Todos os usuários do sistema.

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| id | bigint | PK, IDENTITY | Identificador único |
| nome_completo | varchar | NOT NULL | Nome completo do usuário |
| email | varchar | NOT NULL, UNIQUE | Email de login |
| senha_hash | varchar | nullable | Hash bcrypt da senha |
| tipo_usuario_id | bigint | NOT NULL, FK | Referência ao tipo |
| bp | varchar | UNIQUE, nullable | Prontuário (apenas participantes) |
| data_criacao | timestamptz | DEFAULT NOW() | Data de cadastro |
| data_atualizacao | timestamptz | DEFAULT NOW() | Última atualização |

**Índices:**
- `idx_usuarios_email` em email
- `idx_usuarios_bp` em bp
- `idx_usuarios_tipo` em tipo_usuario_id

**Regras de Negócio:**
- Email deve ser único no sistema
- BP obrigatório apenas para participantes
- BP deve seguir formato: BRGxxxxxxxx (8 dígitos)
- Senha deve ter no mínimo 8 caracteres

---

### projetos

Projetos da feira Bragantec.

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| id | bigint | PK, IDENTITY | Identificador único |
| nome | varchar | NOT NULL | Nome do projeto |
| descricao | text | nullable | Descrição detalhada |
| area_projeto | varchar | NOT NULL | Área científica |
| ano_edicao | integer | NOT NULL | Ano da edição da Bragantec |
| data_criacao | timestamptz | DEFAULT NOW() | Data de criação |

**Índices:**
- `idx_projetos_ano` em ano_edicao

**Áreas Válidas:**
- Ciências Exatas e da Terra
- Ciências Biológicas
- Engenharias
- Ciências da Saúde
- Ciências Agrárias
- Ciências Sociais Aplicadas
- Ciências Humanas
- Linguística, Letras e Artes

---

### participantes_projetos

Relação N:N entre participantes e projetos.

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| participante_id | bigint | PK, FK → usuarios | ID do participante |
| projeto_id | bigint | PK, FK → projetos | ID do projeto |

**Constraints:**
- CASCADE on delete (ambos FKs)
- Chave primária composta

---

### orientadores_projetos

Relação N:N entre orientadores e projetos.

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| orientador_id | bigint | PK, FK → usuarios | ID do orientador |
| projeto_id | bigint | PK, FK → projetos | ID do projeto |

**Constraints:**
- CASCADE on delete (ambos FKs)
- Chave primária composta

---

### tipos_ia

Tipos de IA disponíveis.

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| id | bigint | PK, IDENTITY | Identificador único |
| nome | varchar | NOT NULL, UNIQUE | Nome do tipo de IA |

**Dados Padrão:**
```sql
- gemini
```

---

### chats

Conversas com a IA.

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| id | bigint | PK, IDENTITY | Identificador único |
| projeto_id | bigint | NOT NULL, FK → projetos | Projeto relacionado |
| tipo_ia_id | bigint | NOT NULL, FK → tipos_ia | Tipo de IA usado |
| titulo | varchar | NOT NULL | Título da conversa |
| data_criacao | timestamptz | DEFAULT NOW() | Data de criação |

**Índices:**
- `idx_chats_projeto` em projeto_id

**Constraints:**
- CASCADE on delete projeto_id
- RESTRICT on delete tipo_ia_id

---

### mensagens

Mensagens trocadas nos chats.

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| id | bigint | PK, IDENTITY | Identificador único |
| chat_id | bigint | NOT NULL, FK → chats | Chat relacionado |
| usuario_id | bigint | nullable, FK → usuarios | Autor (NULL = IA) |
| conteudo | text | NOT NULL | Conteúdo da mensagem |
| e_nota_orientador | boolean | DEFAULT false | Se é nota do orientador |
| data_envio | timestamptz | DEFAULT NOW() | Data/hora do envio |

**Índices:**
- `idx_mensagens_chat` em chat_id
- `idx_mensagens_usuario` em usuario_id
- `idx_mensagens_data` em data_envio DESC

**Regras:**
- usuario_id NULL = mensagem da IA
- usuario_id != NULL = mensagem de usuário
- e_nota_orientador = true → mensagem de anotação do orientador

**Constraints:**
- CASCADE on delete chat_id
- SET NULL on delete usuario_id

---

### arquivos_chat

Arquivos anexados às mensagens.

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| id | bigint | PK, IDENTITY | Identificador único |
| mensagem_id | bigint | NOT NULL, FK → mensagens | Mensagem relacionada |
| nome_arquivo | varchar | NOT NULL | Nome original do arquivo |
| url_arquivo | varchar | NOT NULL | URL no Supabase Storage |
| tipo_arquivo | varchar | nullable | MIME type |
| tamanho_bytes | bigint | nullable | Tamanho em bytes |
| data_upload | timestamptz | DEFAULT NOW() | Data do upload |

**Constraints:**
- CASCADE on delete mensagem_id

---

### sistema_config

Configurações persistentes do sistema.

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| chave | varchar | PK | Chave da configuração |
| valor | text | NOT NULL | Valor (geralmente JSON) |
| data_atualizacao | timestamptz | DEFAULT NOW() | Última atualização |

**Configurações Armazenadas:**
- `api_monitor_state`: Estado do monitor de API

---

## Funções do Banco

### get_participantes_projeto

Retorna participantes de um projeto.

```sql
CREATE OR REPLACE FUNCTION get_participantes_projeto(p_projeto_id bigint)
RETURNS TABLE (
  id bigint,
  nome_completo character varying,
  email character varying,
  bp character varying
) AS $$
BEGIN
  RETURN QUERY
  SELECT u.id, u.nome_completo, u.email, u.bp
  FROM usuarios u
  INNER JOIN participantes_projetos pp ON u.id = pp.participante_id
  WHERE pp.projeto_id = p_projeto_id;
END;
$$ LANGUAGE plpgsql;
```

**Uso:**
```sql
SELECT * FROM get_participantes_projeto(1);
```

---

### get_orientadores_projeto

Retorna orientadores de um projeto.

```sql
CREATE OR REPLACE FUNCTION get_orientadores_projeto(p_projeto_id bigint)
RETURNS TABLE (
  id bigint,
  nome_completo character varying,
  email character varying
) AS $$
BEGIN
  RETURN QUERY
  SELECT u.id, u.nome_completo, u.email
  FROM usuarios u
  INNER JOIN orientadores_projetos op ON u.id = op.orientador_id
  WHERE op.projeto_id = p_projeto_id;
END;
$$ LANGUAGE plpgsql;
```

**Uso:**
```sql
SELECT * FROM get_orientadores_projeto(1);
```

---

## Queries Comuns

### Buscar usuário completo com tipo
```sql
SELECT 
  u.*,
  tu.nome as tipo_usuario_nome
FROM usuarios u
INNER JOIN tipos_usuario tu ON u.tipo_usuario_id = tu.id
WHERE u.email = 'usuario@email.com';
```

### Listar projetos de um participante
```sql
SELECT p.*
FROM projetos p
INNER JOIN participantes_projetos pp ON p.id = pp.projeto_id
WHERE pp.participante_id = 1;
```

### Listar chats de um projeto com contagem de mensagens
```sql
SELECT 
  c.*,
  COUNT(m.id) as total_mensagens
FROM chats c
LEFT JOIN mensagens m ON c.id = m.chat_id
WHERE c.projeto_id = 1
GROUP BY c.id
ORDER BY c.data_criacao DESC;
```

### Buscar histórico de mensagens de um chat
```sql
SELECT 
  m.*,
  u.nome_completo as usuario_nome,
  CASE 
    WHEN m.usuario_id IS NULL THEN 'IA'
    ELSE 'Usuario'
  END as tipo_remetente
FROM mensagens m
LEFT JOIN usuarios u ON m.usuario_id = u.id
WHERE m.chat_id = 5
ORDER BY m.data_envio ASC;
```

### Estatísticas de uso por projeto
```sql
SELECT 
  p.nome as projeto,
  COUNT(DISTINCT c.id) as total_chats,
  COUNT(m.id) as total_mensagens,
  COUNT(DISTINCT m.usuario_id) as usuarios_ativos
FROM projetos p
LEFT JOIN chats c ON p.id = c.projeto_id
LEFT JOIN mensagens m ON c.id = m.chat_id
GROUP BY p.id, p.nome
ORDER BY total_mensagens DESC;
```

---

## Backup e Restore

### Backup Automático (Supabase)
O Supabase realiza backups automáticos diários.

### Backup Manual
```bash
# Via Supabase CLI
supabase db dump > backup.sql

# Via pg_dump
pg_dump -h db.oeuncybwjjtlrnwzedxi.supabase.co \
        -U postgres \
        -d postgres > backup.sql
```

### Restore
```bash
# Via psql
psql -h db.oeuncybwjjtlrnwzedxi.supabase.co \
     -U postgres \
     -d postgres < backup.sql
```

---

## Migrations

### Criando uma Migration

1. Crie arquivo em `database/migrations/`:
```sql
-- 001_add_campo_projeto.sql
ALTER TABLE projetos ADD COLUMN status varchar DEFAULT 'ativo';
```

2. Execute:
```bash
psql -f database/migrations/001_add_campo_projeto.sql
```

### Controle de Versão

Crie tabela de migrations:
```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
  version varchar PRIMARY KEY,
  applied_at timestamptz DEFAULT NOW()
);
```

---

## Otimizações

### Índices Adicionais (se necessário)

```sql
-- Para buscas frequentes de mensagens por data
CREATE INDEX idx_mensagens_chat_data 
ON mensagens(chat_id, data_envio DESC);

-- Para filtros por ano de projeto
CREATE INDEX idx_projetos_ano_area 
ON projetos(ano_edicao, area_projeto);

-- Para buscas de notas de orientador
CREATE INDEX idx_mensagens_notas 
ON mensagens(chat_id, e_nota_orientador) 
WHERE e_nota_orientador = true;
```

### Analyze e Vacuum

```sql
-- Atualiza estatísticas
ANALYZE;

-- Limpa espaço
VACUUM;

-- Completo (requer lock exclusivo)
VACUUM FULL;
```

---

## Segurança

### Row Level Security (RLS)

Supabase suporta RLS. Exemplo:

```sql
-- Habilita RLS
ALTER TABLE mensagens ENABLE ROW LEVEL SECURITY;

-- Política: Usuários só veem mensagens de seus projetos
CREATE POLICY mensagens_policy ON mensagens
FOR SELECT
USING (
  chat_id IN (
    SELECT c.id 
    FROM chats c
    INNER JOIN projetos p ON c.projeto_id = p.id
    INNER JOIN participantes_projetos pp ON p.id = pp.projeto_id
    WHERE pp.participante_id = auth.uid()
  )
);
```

### Conexões Seguras

- Sempre use SSL/TLS
- Credenciais via variáveis de ambiente
- Nunca commite senhas

---

## Monitoramento

### Tamanho do Banco
```sql
SELECT 
  pg_size_pretty(pg_database_size('postgres')) as tamanho_total;
```

### Tamanho por Tabela
```sql
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as tamanho
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Queries Lentas
```sql
SELECT 
  query,
  calls,
  total_time,
  mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

## Troubleshooting

### Problema: Conexão recusada
**Solução:** Verifique credenciais e whitelist de IPs no Supabase.

### Problema: Queries lentas
**Solução:** 
1. Verifique índices com `EXPLAIN ANALYZE`
2. Adicione índices necessários
3. Otimize queries complexas

### Problema: Deadlocks
**Solução:**
1. Identifique com `pg_locks`
2. Revise ordem de aquisição de locks
3. Use transações menores

---

## Referências

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Supabase Database](https://supabase.com/docs/guides/database)
- [SQL Style Guide](https://www.sqlstyle.guide/)