# Instruções: Configurar RLS (Row Level Security)

## O que é RLS?

Row Level Security (RLS) é um recurso do PostgreSQL/Supabase que controla **quais linhas** cada usuário pode ver ou modificar em uma tabela. Com RLS, você define políticas que restringem o acesso aos dados baseado no usuário autenticado.

## Por que configurar RLS?

Sem RLS, **qualquer usuário autenticado** poderia:
- Ver dados de outros usuários
- Editar perfis de outras pessoas
- Acessar análises que não deveria ver
- Deletar registros arbitrariamente

Com RLS configurado:
- ✅ Usuários veem apenas dados que devem ver
- ✅ Apenas admins podem modificar dados sensíveis
- ✅ Análises são filtradas por divisão/cargo automaticamente
- ✅ Segurança implementada no nível do banco de dados

## Passo 1: Acessar o Supabase

1. Acesse [https://app.supabase.com](https://app.supabase.com)
2. Faça login na sua conta
3. Selecione o projeto **Analytics Platform**

## Passo 2: Executar o Script RLS

1. Vá em **SQL Editor** no menu lateral
2. Clique em **"New query"**
3. Copie **TODO** o conteúdo do arquivo `supabase_rls_policies.sql`
4. Cole no editor
5. Clique em **"RUN"**
6. Aguarde: "Success. No rows returned"

## Passo 3: Verificar as Políticas

Execute esta consulta para ver todas as políticas criadas:

```sql
SELECT
  tablename,
  policyname,
  cmd,
  roles
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

Você deve ver aproximadamente **13 políticas** criadas:

### Tabela: usuarios (4 políticas)
- `usuarios_select_own` - SELECT (ver próprio perfil)
- `usuarios_select_admin` - SELECT (admin vê todos)
- `usuarios_update_admin` - UPDATE (apenas admin)
- `usuarios_delete_admin` - DELETE (apenas admin)

### Tabela: analyses (6 políticas)
- `analyses_select_public` - SELECT (todos veem públicas)
- `analyses_select_divisao` - SELECT (ver da própria divisão)
- `analyses_select_admin` - SELECT (admin/master/diretor/gerente veem todas)
- `analyses_insert_admin` - INSERT (apenas admin)
- `analyses_update_admin` - UPDATE (apenas admin)
- `analyses_delete_admin` - DELETE (apenas admin)

### Tabela: cargos (1 política)
- `cargos_select_all` - SELECT (todos podem ler)

### Tabela: divisoes (1 política)
- `divisoes_select_all` - SELECT (todos podem ler)

## Passo 4: Testar as Políticas

### Teste 1: Criar usuário admin

No SQL Editor, execute:

```sql
-- Verificar se você tem um usuário admin
SELECT id, email, nome, role
FROM public.usuarios
WHERE role = 'admin';
```

Se não houver nenhum admin, crie um:

```sql
-- Atualizar usuário existente para admin (substitua o email)
UPDATE public.usuarios
SET role = 'admin'
WHERE email = 'seu@email.com';
```

### Teste 2: Criar usuário comum de teste

1. Vá para `http://localhost:5173/signup`
2. Crie um novo usuário de teste
3. Email: `teste@empresa.com`
4. Senha: `Teste123`

### Teste 3: Testar acesso como usuário comum

1. Faça login com o usuário de teste
2. Vá para a API: `http://localhost:8000/users` (GET)
3. Você deve receber **403 Forbidden** (apenas admin pode listar todos)

### Teste 4: Testar acesso como admin

1. Faça login com o usuário admin
2. Vá para a API: `http://localhost:8000/users` (GET)
3. Você deve receber **200 OK** com lista de usuários

### Teste 5: Verificar análises

1. Crie uma análise pública (como admin)
2. Crie uma análise da divisão X
3. Faça login como usuário da divisão X
4. Verifique que ele vê:
   - ✅ Análises públicas
   - ✅ Análises da própria divisão
   - ❌ Análises de outras divisões (a menos que seja Master/Diretor/Gerente)

## Regras de Acesso Implementadas

### Tabela: usuarios

| Ação | Quem pode? |
|------|------------|
| Ver próprio perfil | Qualquer usuário autenticado |
| Ver todos os perfis | Apenas admin |
| Editar perfil | Apenas admin |
| Deletar perfil | Apenas admin |

### Tabela: analyses

| Ação | Quem pode? |
|------|------------|
| Ver análises públicas | Todos os usuários autenticados |
| Ver análises da divisão | Usuários da mesma divisão |
| Ver todas as análises | Master, Diretor, Gerente, Admin |
| Criar análise | Apenas admin |
| Editar análise | Apenas admin |
| Deletar análise | Apenas admin |

### Tabela: cargos e divisoes

| Ação | Quem pode? |
|------|------------|
| Ver lista | Todos (dados de referência) |

## Hierarquia de Cargos

Assumindo esta estrutura:

1. **Master** (cargo_id = 1) - Acesso total
2. **Diretor** (cargo_id = 2) - Acesso total
3. **Gerente** (cargo_id = 3) - Acesso total
4. **Analista**, **Assistente**, etc. - Acesso restrito à divisão

## Verificar RLS está ativo

Execute no SQL Editor:

```sql
-- Verificar se RLS está habilitado nas tabelas
SELECT
  schemaname,
  tablename,
  rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('usuarios', 'analyses', 'cargos', 'divisoes');
```

Deve retornar `rowsecurity = true` para todas.

## Desabilitar RLS temporariamente (APENAS PARA DEBUG)

**ATENÇÃO**: Isso remove toda a segurança! Use apenas para debug local.

```sql
-- Desabilitar RLS
ALTER TABLE public.usuarios DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses DISABLE ROW LEVEL SECURITY;
```

Para re-habilitar:

```sql
-- Re-habilitar RLS
ALTER TABLE public.usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
```

## Troubleshooting

### Erro: "new row violates row-level security policy"

**Problema**: Tentando inserir dados sem permissão

**Solução**: Certifique-se de estar autenticado como admin ou verificar a política INSERT

### Erro: "permission denied for table"

**Problema**: RLS está bloqueando o acesso

**Solução**:
1. Verifique se o usuário está autenticado (`auth.uid()` não é null)
2. Verifique se a política permite a operação
3. Verifique o role do usuário (deve ser 'admin' para operações privilegiadas)

### Nenhuma linha retornada (mas deveria haver)

**Problema**: Políticas estão filtrando demais

**Solução**:
1. Verifique as políticas com a query de verificação acima
2. Teste se `auth.uid()` retorna o ID esperado:
   ```sql
   SELECT auth.uid();
   ```
3. Verifique se o usuário tem o cargo/divisão esperados:
   ```sql
   SELECT * FROM public.usuarios WHERE id = auth.uid();
   ```

### Query SQL Editor funciona, mas API não

**Problema**: SQL Editor usa credenciais diferentes (service role)

**Solução**:
- SQL Editor ignora RLS por padrão (service_role bypass)
- Para testar RLS no SQL Editor, use:
  ```sql
  SET LOCAL ROLE authenticated;
  SET LOCAL request.jwt.claims.sub = 'user-uuid-aqui';
  ```

## Logs e Auditoria

Para ver quem está acessando o quê:

```sql
-- Ver todas as queries recentes (apenas service_role)
SELECT * FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 20;
```

## Próximos Passos

Após configurar RLS:

1. ✅ Testar login como usuário comum
2. ✅ Testar login como admin
3. ✅ Verificar que análises são filtradas corretamente
4. ✅ Testar criação/edição de análises (apenas admin)
5. ✅ Documentar no README.md

## Referências

- [Supabase RLS Documentation](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL RLS Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
