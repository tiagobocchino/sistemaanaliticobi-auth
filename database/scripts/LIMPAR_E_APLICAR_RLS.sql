-- ===============================================
-- SCRIPT: LIMPAR E APLICAR RLS DO ZERO
-- ===============================================
-- Este script LIMPA todas as políticas antigas e aplica as novas
-- Execute TUDO de uma vez no SQL Editor do Supabase
-- ===============================================

-- ===============================================
-- PARTE 1: LIMPAR TUDO (REMOVER POLÍTICAS ANTIGAS)
-- ===============================================

-- 1.1: Desabilitar RLS temporariamente
ALTER TABLE IF EXISTS public.usuarios DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.analyses DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.cargos DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.divisoes DISABLE ROW LEVEL SECURITY;

-- 1.2: Remover TODAS as políticas da tabela usuarios
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE schemaname = 'public' AND tablename = 'usuarios') LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON public.usuarios';
    END LOOP;
END $$;

-- 1.3: Remover TODAS as políticas da tabela analyses
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE schemaname = 'public' AND tablename = 'analyses') LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON public.analyses';
    END LOOP;
END $$;

-- 1.4: Remover TODAS as políticas da tabela cargos
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE schemaname = 'public' AND tablename = 'cargos') LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON public.cargos';
    END LOOP;
END $$;

-- 1.5: Remover TODAS as políticas da tabela divisoes
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE schemaname = 'public' AND tablename = 'divisoes') LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON public.divisoes';
    END LOOP;
END $$;

-- Verificar se limpou tudo (deve retornar 0 linhas)
SELECT tablename, policyname FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('usuarios', 'analyses', 'cargos', 'divisoes');

-- ===============================================
-- PARTE 2: APLICAR NOVAS POLÍTICAS
-- ===============================================

-- ===============================================
-- 2.1: TABELA usuarios
-- ===============================================

-- Habilitar RLS
ALTER TABLE public.usuarios ENABLE ROW LEVEL SECURITY;

-- Política 1: Ver próprio perfil
CREATE POLICY "usuarios_select_own"
ON public.usuarios
FOR SELECT
TO authenticated
USING (auth.uid() = id);

-- Política 2: Admins veem todos
CREATE POLICY "usuarios_select_admin"
ON public.usuarios
FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM public.usuarios u
    INNER JOIN public.cargos c ON u.cargo_id = c.id
    WHERE u.id = auth.uid()
      AND c.nivel_acesso >= 5
  )
);

-- Política 3: Apenas admins atualizam
CREATE POLICY "usuarios_update_admin"
ON public.usuarios
FOR UPDATE
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM public.usuarios u
    INNER JOIN public.cargos c ON u.cargo_id = c.id
    WHERE u.id = auth.uid()
      AND c.nivel_acesso >= 5
  )
);

-- Política 4: Apenas admins deletam
CREATE POLICY "usuarios_delete_admin"
ON public.usuarios
FOR DELETE
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM public.usuarios u
    INNER JOIN public.cargos c ON u.cargo_id = c.id
    WHERE u.id = auth.uid()
      AND c.nivel_acesso >= 5
  )
);

-- ===============================================
-- 2.2: TABELA analyses
-- ===============================================

-- Habilitar RLS
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

-- Política 1: Todos veem análises públicas
CREATE POLICY "analyses_select_public"
ON public.analyses
FOR SELECT
TO authenticated
USING (publico = true AND ativo = true);

-- Política 2: Usuários veem análises da própria divisão
CREATE POLICY "analyses_select_divisao"
ON public.analyses
FOR SELECT
TO authenticated
USING (
  ativo = true
  AND divisao_restrita_id IS NOT NULL
  AND divisao_restrita_id IN (
    SELECT divisao_id FROM public.usuarios
    WHERE id = auth.uid()
  )
);

-- Política 3: nivel_acesso >= 4 veem todas
CREATE POLICY "analyses_select_high_level"
ON public.analyses
FOR SELECT
TO authenticated
USING (
  ativo = true
  AND EXISTS (
    SELECT 1 FROM public.usuarios u
    INNER JOIN public.cargos c ON u.cargo_id = c.id
    WHERE u.id = auth.uid()
      AND c.nivel_acesso >= 4
  )
);

-- Política 4: Apenas admins criam
CREATE POLICY "analyses_insert_admin"
ON public.analyses
FOR INSERT
TO authenticated
WITH CHECK (
  EXISTS (
    SELECT 1 FROM public.usuarios u
    INNER JOIN public.cargos c ON u.cargo_id = c.id
    WHERE u.id = auth.uid()
      AND c.nivel_acesso >= 5
  )
);

-- Política 5: Apenas admins atualizam
CREATE POLICY "analyses_update_admin"
ON public.analyses
FOR UPDATE
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM public.usuarios u
    INNER JOIN public.cargos c ON u.cargo_id = c.id
    WHERE u.id = auth.uid()
      AND c.nivel_acesso >= 5
  )
);

-- Política 6: Apenas admins deletam
CREATE POLICY "analyses_delete_admin"
ON public.analyses
FOR DELETE
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM public.usuarios u
    INNER JOIN public.cargos c ON u.cargo_id = c.id
    WHERE u.id = auth.uid()
      AND c.nivel_acesso >= 5
  )
);

-- ===============================================
-- 2.3: TABELA cargos
-- ===============================================

-- Habilitar RLS
ALTER TABLE public.cargos ENABLE ROW LEVEL SECURITY;

-- Política: Todos podem ler cargos
CREATE POLICY "cargos_select_all"
ON public.cargos
FOR SELECT
TO authenticated
USING (true);

-- ===============================================
-- 2.4: TABELA divisoes
-- ===============================================

-- Habilitar RLS
ALTER TABLE public.divisoes ENABLE ROW LEVEL SECURITY;

-- Política: Todos podem ler divisões
CREATE POLICY "divisoes_select_all"
ON public.divisoes
FOR SELECT
TO authenticated
USING (true);

-- ===============================================
-- PARTE 3: VERIFICAÇÃO
-- ===============================================

-- Ver todas as políticas criadas
SELECT
  tablename,
  policyname,
  cmd as comando,
  CASE
    WHEN cmd = 'SELECT' THEN 'Leitura'
    WHEN cmd = 'INSERT' THEN 'Criar'
    WHEN cmd = 'UPDATE' THEN 'Atualizar'
    WHEN cmd = 'DELETE' THEN 'Deletar'
    ELSE cmd
  END as tipo
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('usuarios', 'analyses', 'cargos', 'divisoes')
ORDER BY tablename, cmd, policyname;

-- Deve retornar:
-- usuarios: 4 políticas (1 SELECT own, 1 SELECT admin, 1 UPDATE, 1 DELETE)
-- analyses: 6 políticas (3 SELECT, 1 INSERT, 1 UPDATE, 1 DELETE)
-- cargos: 1 política (SELECT)
-- divisoes: 1 política (SELECT)
-- TOTAL: 12 políticas

-- ===============================================
-- PARTE 4: TESTES RÁPIDOS
-- ===============================================

-- Teste 1: Ver seu próprio perfil (deve funcionar)
SELECT id, email, nome, cargo_id, divisao_id
FROM public.usuarios
WHERE id = auth.uid();

-- Teste 2: Ver cargos (deve funcionar para todos)
SELECT id, nome, nivel_acesso
FROM public.cargos
ORDER BY nivel_acesso DESC;

-- Teste 3: Ver divisões (deve funcionar para todos)
SELECT id, nome, codigo
FROM public.divisoes;

-- ===============================================
-- FIM DO SCRIPT
-- ===============================================

/*
RESULTADO ESPERADO:

✅ Todas as políticas antigas removidas
✅ 12 novas políticas criadas
✅ RLS habilitado em todas as tabelas
✅ Sistema de permissões baseado em cargos.nivel_acesso

NÍVEIS DE ACESSO:
- 5: Admin (gerenciar usuários e análises)
- 4: Master/Diretor/Gerente (ver todas análises)
- 3: Gerente Júnior
- 2: Analista
- 1: Assistente
- 0: Sem acesso

IMPORTANTE:
- Usuários SEM cargo_id só verão seu próprio perfil e análises públicas
- Admin deve atribuir cargo_id aos usuários via /users endpoint
*/
