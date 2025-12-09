-- ===============================================
-- ROW LEVEL SECURITY (RLS) - Analytics Platform
-- ===============================================
-- Políticas de segurança para controle de acesso granular
-- Baseado em cargos.nivel_acesso e divisões
--
-- NÍVEIS DE ACESSO:
-- - nivel_acesso >= 5: Admin (gerenciar usuários, criar análises)
-- - nivel_acesso >= 4: Master/Diretor/Gerente (ver todas análises)
-- - nivel_acesso < 4: Usuário comum (ver análises públicas + própria divisão)
--
-- IMPORTANTE: Execute este script APENAS uma vez no Supabase SQL Editor
-- ===============================================

-- ===============================================
-- LIMPEZA COMPLETA - Execute primeiro para evitar conflitos
-- ===============================================

-- Remover TODAS as políticas existentes das tabelas
DO $$
DECLARE
    policy_record RECORD;
BEGIN
    -- Limpar políticas de todas as tabelas
    FOR policy_record IN
        SELECT schemaname, tablename, policyname
        FROM pg_policies
        WHERE schemaname = 'public'
        AND tablename IN ('usuarios', 'analyses', 'cargos', 'divisoes')
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON %I.%I',
                      policy_record.policyname,
                      policy_record.schemaname,
                      policy_record.tablename);
    END LOOP;

    RAISE NOTICE 'Todas as políticas RLS foram removidas';
END $$;

-- ===============================================
-- TABELA: public.usuarios
-- ===============================================

-- Habilitar RLS na tabela usuarios
ALTER TABLE public.usuarios ENABLE ROW LEVEL SECURITY;

-- Remover políticas existentes (se houver)
DROP POLICY IF EXISTS "usuarios_select_own" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios_select_admin" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios_update_admin" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios_delete_admin" ON public.usuarios;

-- POLÍTICA 1: Usuários podem ver apenas seu próprio perfil
CREATE POLICY "usuarios_select_own"
ON public.usuarios
FOR SELECT
USING (auth.uid() = id);

-- POLÍTICA 2: Admins (nivel_acesso >= 5) podem ver todos os usuários
CREATE POLICY "usuarios_select_admin"
ON public.usuarios
FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.usuarios u
    LEFT JOIN public.cargos c ON u.cargo_id = c.id
    WHERE u.id = auth.uid()
      AND c.nivel_acesso >= 5
  )
);

-- POLÍTICA 3: Apenas admins (nivel_acesso >= 5) podem atualizar usuários
CREATE POLICY "usuarios_update_admin"
ON public.usuarios
FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM public.usuarios u
    LEFT JOIN public.cargos c ON u.cargo_id = c.id
    WHERE u.id = auth.uid()
      AND c.nivel_acesso >= 5
  )
);

-- POLÍTICA 4: Apenas admins (nivel_acesso >= 5) podem deletar usuários
CREATE POLICY "usuarios_delete_admin"
ON public.usuarios
FOR DELETE
USING (
  EXISTS (
    SELECT 1 FROM public.usuarios u
    LEFT JOIN public.cargos c ON u.cargo_id = c.id
    WHERE u.id = auth.uid()
      AND c.nivel_acesso >= 5
  )
);


-- ===============================================
-- TABELA: public.analyses
-- ===============================================

-- Habilitar RLS na tabela analyses
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

-- Remover políticas existentes (se houver)
DROP POLICY IF EXISTS "analyses_select_public" ON public.analyses;
DROP POLICY IF EXISTS "analyses_select_divisao" ON public.analyses;
DROP POLICY IF EXISTS "analyses_select_admin" ON public.analyses;
DROP POLICY IF EXISTS "analyses_insert_admin" ON public.analyses;
DROP POLICY IF EXISTS "analyses_update_admin" ON public.analyses;
DROP POLICY IF EXISTS "analyses_delete_admin" ON public.analyses;

-- POLÍTICA 1: Todos podem ver análises públicas
CREATE POLICY "analyses_select_public"
ON public.analyses
FOR SELECT
USING (publico = true AND ativo = true);

-- POLÍTICA 2: Usuários podem ver análises da sua divisão (não públicas)
CREATE POLICY "analyses_select_divisao"
ON public.analyses
FOR SELECT
USING (
  ativo = true
  AND divisao_restrita_id IS NOT NULL
  AND divisao_restrita_id IN (
    SELECT divisao_id FROM public.usuarios
    WHERE id = auth.uid()
  )
);

-- POLÍTICA 3: Master/Diretor/Gerente (nivel_acesso >= 4) podem ver todas as análises
CREATE POLICY "analyses_select_admin"
ON public.analyses
FOR SELECT
USING (
  ativo = true
  AND EXISTS (
    SELECT 1 FROM public.usuarios u
    LEFT JOIN public.cargos c ON u.cargo_id = c.id
    WHERE u.id = auth.uid()
      AND c.nivel_acesso >= 4
  )
);

-- POLÍTICA 4: Apenas admins (nivel_acesso >= 5) podem criar análises
CREATE POLICY "analyses_insert_admin"
ON public.analyses
FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM public.usuarios u
    LEFT JOIN public.cargos c ON u.cargo_id = c.id
    WHERE u.id = auth.uid()
      AND c.nivel_acesso >= 5
  )
);

-- POLÍTICA 5: Apenas admins (nivel_acesso >= 5) podem atualizar análises
CREATE POLICY "analyses_update_admin"
ON public.analyses
FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM public.usuarios u
    LEFT JOIN public.cargos c ON u.cargo_id = c.id
    WHERE u.id = auth.uid()
      AND c.nivel_acesso >= 5
  )
);

-- POLÍTICA 6: Apenas admins (nivel_acesso >= 5) podem deletar análises
CREATE POLICY "analyses_delete_admin"
ON public.analyses
FOR DELETE
USING (
  EXISTS (
    SELECT 1 FROM public.usuarios u
    LEFT JOIN public.cargos c ON u.cargo_id = c.id
    WHERE u.id = auth.uid()
      AND c.nivel_acesso >= 5
  )
);


-- ===============================================
-- TABELA: public.cargos (se existir)
-- ===============================================

-- Habilitar RLS na tabela cargos
ALTER TABLE public.cargos ENABLE ROW LEVEL SECURITY;

-- Remover políticas existentes
DROP POLICY IF EXISTS "cargos_select_all" ON public.cargos;

-- POLÍTICA: Todos usuários autenticados podem ler cargos (lista de referência)
CREATE POLICY "cargos_select_all"
ON public.cargos
FOR SELECT
TO authenticated
USING (true);


-- ===============================================
-- TABELA: public.divisoes (se existir)
-- ===============================================

-- Habilitar RLS na tabela divisoes
ALTER TABLE public.divisoes ENABLE ROW LEVEL SECURITY;

-- Remover políticas existentes
DROP POLICY IF EXISTS "divisoes_select_all" ON public.divisoes;

-- POLÍTICA: Todos usuários autenticados podem ler divisões (lista de referência)
CREATE POLICY "divisoes_select_all"
ON public.divisoes
FOR SELECT
TO authenticated
USING (true);


-- ===============================================
-- VERIFICAÇÃO DAS POLÍTICAS
-- ===============================================

-- Ver todas as políticas criadas
SELECT
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('usuarios', 'analyses', 'cargos', 'divisoes')
ORDER BY tablename, policyname;


-- ===============================================
-- TESTES DE PERMISSÃO
-- ===============================================

-- Teste 1: Ver perfil próprio (deve funcionar para todos)
SELECT * FROM public.usuarios WHERE id = auth.uid();

-- Teste 2: Ver todos os usuários (deve funcionar apenas para admin nivel_acesso >= 5)
SELECT u.id, u.email, u.nome, c.nome as cargo, c.nivel_acesso
FROM public.usuarios u
LEFT JOIN public.cargos c ON u.cargo_id = c.id;

-- Teste 3: Ver análises públicas (deve funcionar para todos)
SELECT * FROM public.analyses WHERE publico = true;

-- Teste 4: Ver todas as análises (deve funcionar apenas para nivel_acesso >= 4)
SELECT a.*, c.nivel_acesso
FROM public.analyses a, public.usuarios u
LEFT JOIN public.cargos c ON u.cargo_id = c.id
WHERE u.id = auth.uid();


-- ===============================================
-- RESUMO DAS REGRAS DE ACESSO
-- ===============================================

/*
TABELA: usuarios
- SELECT (ver próprio perfil): qualquer usuário autenticado
- SELECT (ver todos): apenas nivel_acesso >= 5
- UPDATE: apenas nivel_acesso >= 5
- DELETE: apenas nivel_acesso >= 5

TABELA: analyses
- SELECT (análises públicas): todos
- SELECT (análises da divisão): usuários da mesma divisão
- SELECT (todas as análises): nivel_acesso >= 4
- INSERT: apenas nivel_acesso >= 5
- UPDATE: apenas nivel_acesso >= 5
- DELETE: apenas nivel_acesso >= 5

TABELA: cargos
- SELECT: todos (dados de referência)

TABELA: divisoes
- SELECT: todos (dados de referência)

HIERARQUIA DE NÍVEIS:
- 5: Admin (pode gerenciar usuários e análises)
- 4: Master/Diretor/Gerente (pode ver tudo, mas não gerenciar)
- 3: Gerente Júnior
- 2: Analista
- 1: Assistente
- 0: Sem acesso
*/


-- ===============================================
-- NOTAS IMPORTANTES
-- ===============================================

/*
1. Estas políticas usam auth.uid() para identificar o usuário atual
2. O auth.uid() retorna o ID do usuário autenticado no Supabase Auth
3. As políticas são avaliadas em TODAS as queries (SELECT, INSERT, UPDATE, DELETE)
4. Se nenhuma política permitir, a operação é NEGADA
5. Políticas podem ser combinadas com OR (se qualquer uma permitir, ok)

6. IMPORTANTE: Usuários SEM cargo_id (NULL) terão nivel_acesso = 0
   Eles só poderão:
   - Ver seu próprio perfil
   - Ver análises públicas

   Admin deve atribuir cargo_id via /users endpoint

7. Para testar as políticas:
   - Faça login como usuário comum (sem cargo)
   - Faça login como usuário com cargo nivel_acesso = 3
   - Faça login como admin (nivel_acesso = 5)
   - Tente acessar dados que não deveria ter acesso
   - Verifique os logs no Supabase

8. Para desabilitar RLS temporariamente (NÃO RECOMENDADO em produção):
   ALTER TABLE public.usuarios DISABLE ROW LEVEL SECURITY;
   ALTER TABLE public.analyses DISABLE ROW LEVEL SECURITY;
*/
