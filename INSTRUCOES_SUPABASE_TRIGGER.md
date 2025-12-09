# Instruções: Configurar Trigger no Supabase

## Problema Identificado

O sistema **NÃO** está criando registros na tabela `public.usuarios` quando usuários fazem signup porque:

1. O frontend (Signup.jsx) não envia `cargo_id` e `divisao_id`
2. O backend só cria o perfil SE `cargo_id` e `divisao_id` forem fornecidos
3. Não existe trigger no Supabase para criar automaticamente

## Solução: Criar Trigger Automático

### Passo 1: Acessar o Supabase

1. Acesse [https://app.supabase.com](https://app.supabase.com)
2. Faça login na sua conta
3. Selecione o projeto **Analytics Platform**

### Passo 2: Abrir SQL Editor

1. No menu lateral esquerdo, clique em **"SQL Editor"**
2. Clique em **"New query"** para criar uma nova consulta

### Passo 3: Executar o Script

1. Copie **TODO** o conteúdo do arquivo `supabase_trigger_create_user.sql`
2. Cole no editor SQL do Supabase
3. Clique em **"RUN"** (botão no canto inferior direito)
4. Aguarde a confirmação: "Success. No rows returned"

### Passo 4: Verificar o Trigger

Execute esta consulta para verificar se o trigger foi criado:

```sql
-- Verificar se a função existe
SELECT proname, prosrc
FROM pg_proc
WHERE proname = 'handle_new_user';

-- Verificar se o trigger existe
on_auth_user_created
```

Você deve ver:
- 1 linha retornada para a função `handle_new_user`
- 1 linha retornada para o trigger `on_auth_user_created`

## O Que o Trigger Faz

Quando um novo usuário faz signup:

1. **Supabase Auth** cria o usuário em `auth.users`
2. **Trigger dispara** automaticamente
3. **Função `handle_new_user()`** executa
4. **Perfil criado** em `public.usuarios` com:
   - `id`: mesmo ID de auth.users
   - `email`: email do usuário
   - `nome`: full_name do metadata (ou email como fallback)
   - `cargo_id`: null (pode ser atualizado depois)
   - `divisao_id`: null (pode ser atualizado depois)
   - `ativo`: true
   - `created_at` e `updated_at`: timestamp atual

## Testar o Sistema

Após criar o trigger:

1. Vá para `http://localhost:5173/signup`
2. Crie um novo usuário de teste
3. Faça login com esse usuário
4. No Supabase, vá em **Table Editor** > **usuarios**
5. Verifique se o registro foi criado automaticamente

## Verificar Dados

No SQL Editor do Supabase, execute:

```sql
-- Ver todos os usuários criados
SELECT
  u.id,
  u.email,
  u.nome,
  u.cargo_id,
  u.divisao_id,
  u.ativo,
  u.created_at
FROM public.usuarios u
ORDER BY u.created_at DESC;

-- Ver usuários do auth que NÃO têm perfil (problema!)
SELECT
  a.id,
  a.email,
  a.created_at
FROM auth.users a
LEFT JOIN public.usuarios u ON a.id = u.id
WHERE u.id IS NULL;
```

Se a segunda consulta retornar registros, significa que existem usuários sem perfil (criados antes do trigger).

## Criar Perfis para Usuários Antigos (Opcional)

Se houver usuários sem perfil, execute:

```sql
-- Criar perfis para usuários que não têm
```

## Troubleshooting

### Erro: "permission denied for table usuarios"

Solução: Certifique-se de que a função tem `SECURITY DEFINER`:

```sql
ALTER FUNCTION public.handle_new_user() SECURITY DEFINER;
```

### Erro: "column does not exist"

Solução: Verifique se a tabela `public.usuarios` tem todas as colunas necessárias:

```sql
-- Ver estrutura da tabela
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'usuarios'
ORDER BY ordinal_position;
```

Colunas obrigatórias:
- `id` (uuid, PK)
- `email` (text/varchar)
- `nome` (text/varchar)
- `cargo_id` (uuid, nullable)
- `divisao_id` (uuid, nullable)
- `ativo` (boolean)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### Trigger não está disparando

1. Verifique se o trigger está habilitado:

```sql
SELECT tgenabled FROM pg_trigger WHERE tgname = 'on_auth_user_created';
```

Deve retornar: `O` (enabled)

2. Se estiver desabilitado (`D`), habilite:

```sql
ALTER TABLE auth.users ENABLE TRIGGER on_auth_user_created;
```

## Próximos Passos

Após configurar o trigger:

1. ✅ Teste o signup
2. ✅ Verifique se perfis são criados automaticamente
3. ✅ Configure RLS (Row Level Security) na tabela usuarios
4. ✅ Teste o sistema de login completo

## Suporte

Se encontrar problemas:
1. Verifique os logs no Supabase Dashboard > Logs
2. Execute as consultas de troubleshooting acima
3. Certifique-se de que você tem permissões de admin no projeto Supabase
