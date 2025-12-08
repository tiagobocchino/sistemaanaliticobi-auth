# Database Setup - Analytics Platform

## Como Executar os Scripts no Supabase

### Opção 1: SQL Editor (Recomendado)

1. Acesse o Dashboard do Supabase: https://supabase.com/dashboard
2. Selecione seu projeto
3. No menu lateral, clique em **SQL Editor**
4. Clique em **New Query**
5. Copie e cole o conteúdo do arquivo `migrations/001_create_base_tables.sql`
6. Clique em **Run** (ou pressione Ctrl+Enter)
7. Aguarde a execução completar

### Opção 2: Via CLI do Supabase

```bash
# Instalar Supabase CLI (se ainda não tiver)
npm install -g supabase

# Login
supabase login

# Link com seu projeto
supabase link --project-ref seu-project-ref

# Executar migration
supabase db push
```

## Estrutura das Tabelas

### 1. `cargos` (Funções/Posições)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Chave primária |
| nome | VARCHAR(100) | Nome do cargo (único) |
| descricao | TEXT | Descrição do cargo |
| nivel_acesso | INTEGER | Nível de acesso (1-5) |
| ativo | BOOLEAN | Cargo ativo |
| created_at | TIMESTAMP | Data de criação |
| updated_at | TIMESTAMP | Data de atualização |

**Cargos iniciais**:
- Administrador (nível 5)
- Gerente (nível 4)
- Coordenador (nível 3)
- Analista (nível 2)
- Assistente (nível 1)

### 2. `divisoes` (Departamentos)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Chave primária |
| nome | VARCHAR(100) | Nome da divisão (único) |
| descricao | TEXT | Descrição da divisão |
| codigo | VARCHAR(20) | Código/sigla (único) |
| ativo | BOOLEAN | Divisão ativa |
| created_at | TIMESTAMP | Data de criação |
| updated_at | TIMESTAMP | Data de atualização |

**Divisões iniciais**:
- TI - Tecnologia da Informação
- RH - Recursos Humanos
- FIN - Financeiro
- COM - Comercial
- OPS - Operações

### 3. `usuarios` (Perfis de Usuário)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | FK para auth.users |
| email | VARCHAR(255) | Email (único) |
| nome | VARCHAR(255) | Nome completo |
| cargo_id | UUID | FK para cargos |
| divisao_id | UUID | FK para divisoes |
| ativo | BOOLEAN | Usuário ativo |
| avatar_url | TEXT | URL do avatar |
| telefone | VARCHAR(20) | Telefone |
| created_at | TIMESTAMP | Data de criação |
| updated_at | TIMESTAMP | Data de atualização |

## Row Level Security (RLS)

### Políticas Implementadas

#### Cargos
- ✅ Leitura: Todos usuários autenticados veem cargos ativos
- ✅ Escrita: Apenas administradores (nível 5)

#### Divisões
- ✅ Leitura: Todos usuários autenticados veem divisões ativas
- ✅ Escrita: Apenas administradores (nível 5)

#### Usuários
- ✅ Usuários veem seu próprio perfil
- ✅ Administradores e gerentes (nível >= 4) veem todos
- ✅ Usuários veem colegas da mesma divisão
- ✅ Usuários podem atualizar seu perfil (exceto cargo e divisão)
- ✅ Apenas administradores criam/deletam usuários

## Triggers Automáticos

- ✅ `updated_at` é atualizado automaticamente em cada UPDATE
- ✅ Validação de integridade referencial

## Verificar Instalação

Execute no SQL Editor:

```sql
-- Verificar tabelas criadas
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('cargos', 'divisoes', 'usuarios');

-- Verificar cargos inseridos
SELECT * FROM public.cargos ORDER BY nivel_acesso DESC;

-- Verificar divisões inseridas
SELECT * FROM public.divisoes ORDER BY nome;

-- Verificar RLS habilitado
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('cargos', 'divisoes', 'usuarios');
```

## Próximos Passos

Após executar as migrations:

1. ✅ Tabelas criadas e populadas com dados iniciais
2. ⏳ Atualizar backend para usar as novas tabelas
3. ⏳ Criar endpoints para gestão de cargos e divisões
4. ⏳ Modificar signup para criar perfil na tabela usuarios
5. ⏳ Implementar interface de administração

## Problemas Comuns

### Erro: "relation already exists"
Se as tabelas já existirem, você pode:
- Ignorar o erro (o script usa `IF NOT EXISTS`)
- Ou dropar as tabelas antes: `DROP TABLE IF EXISTS public.usuarios CASCADE;`

### Erro: "permission denied"
Certifique-se de estar usando o role correto no Supabase (postgres ou service_role)

### RLS bloqueando acesso
Para testar sem RLS temporariamente:
```sql
ALTER TABLE public.usuarios DISABLE ROW LEVEL SECURITY;
```

## Rollback

Para desfazer as mudanças:

```sql
-- Remover tabelas (cuidado: apaga todos os dados!)
DROP TABLE IF EXISTS public.usuarios CASCADE;
DROP TABLE IF EXISTS public.divisoes CASCADE;
DROP TABLE IF EXISTS public.cargos CASCADE;
DROP FUNCTION IF EXISTS public.update_updated_at_column() CASCADE;
```
