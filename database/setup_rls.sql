-- =====================================================
-- SETUP DE ROW LEVEL SECURITY (RLS)
-- =====================================================
-- Execute este script APÓS o setup_complete.sql
-- =====================================================

-- =====================================================
-- 1. HABILITAR RLS
-- =====================================================

ALTER TABLE public.cargos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.divisoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- 2. POLÍTICAS RLS - CARGOS
-- =====================================================

DROP POLICY IF EXISTS "Cargos são visíveis para todos usuários autenticados" ON public.cargos;
CREATE POLICY "Cargos são visíveis para todos usuários autenticados"
    ON public.cargos FOR SELECT
    TO authenticated
    USING (ativo = true);

DROP POLICY IF EXISTS "Apenas administradores podem gerenciar cargos" ON public.cargos;
CREATE POLICY "Apenas administradores podem gerenciar cargos"
    ON public.cargos FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.usuarios u
            LEFT JOIN public.cargos c ON u.cargo_id = c.id
            WHERE u.id = auth.uid() AND c.nivel_acesso = 5
        )
    );

-- =====================================================
-- 3. POLÍTICAS RLS - DIVISÕES
-- =====================================================

DROP POLICY IF EXISTS "Divisões são visíveis para todos usuários autenticados" ON public.divisoes;
CREATE POLICY "Divisões são visíveis para todos usuários autenticados"
    ON public.divisoes FOR SELECT
    TO authenticated
    USING (ativo = true);

DROP POLICY IF EXISTS "Apenas administradores podem gerenciar divisões" ON public.divisoes;
CREATE POLICY "Apenas administradores podem gerenciar divisões"
    ON public.divisoes FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.usuarios u
            LEFT JOIN public.cargos c ON u.cargo_id = c.id
            WHERE u.id = auth.uid() AND c.nivel_acesso = 5
        )
    );

-- =====================================================
-- 4. POLÍTICAS RLS - USUÁRIOS
-- =====================================================

DROP POLICY IF EXISTS "Usuários podem ver seu próprio perfil" ON public.usuarios;
CREATE POLICY "Usuários podem ver seu próprio perfil"
    ON public.usuarios FOR SELECT
    TO authenticated
    USING (id = auth.uid());

DROP POLICY IF EXISTS "Administradores e gerentes podem ver todos usuários" ON public.usuarios;
CREATE POLICY "Administradores e gerentes podem ver todos usuários"
    ON public.usuarios FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.usuarios u
            LEFT JOIN public.cargos c ON u.cargo_id = c.id
            WHERE u.id = auth.uid() AND c.nivel_acesso >= 4
        )
    );

DROP POLICY IF EXISTS "Usuários podem ver colegas da mesma divisão" ON public.usuarios;
CREATE POLICY "Usuários podem ver colegas da mesma divisão"
    ON public.usuarios FOR SELECT
    TO authenticated
    USING (
        divisao_id IN (
            SELECT divisao_id FROM public.usuarios WHERE id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Usuários podem atualizar seu próprio perfil" ON public.usuarios;
CREATE POLICY "Usuários podem atualizar seu próprio perfil"
    ON public.usuarios FOR UPDATE
    TO authenticated
    USING (id = auth.uid())
    WITH CHECK (
        id = auth.uid() AND
        cargo_id = (SELECT cargo_id FROM public.usuarios WHERE id = auth.uid()) AND
        divisao_id = (SELECT divisao_id FROM public.usuarios WHERE id = auth.uid())
    );

DROP POLICY IF EXISTS "Apenas administradores podem criar usuários" ON public.usuarios;
CREATE POLICY "Apenas administradores podem criar usuários"
    ON public.usuarios FOR INSERT
    TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.usuarios u
            LEFT JOIN public.cargos c ON u.cargo_id = c.id
            WHERE u.id = auth.uid() AND c.nivel_acesso = 5
        )
    );

DROP POLICY IF EXISTS "Apenas administradores podem deletar usuários" ON public.usuarios;
CREATE POLICY "Apenas administradores podem deletar usuários"
    ON public.usuarios FOR DELETE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.usuarios u
            LEFT JOIN public.cargos c ON u.cargo_id = c.id
            WHERE u.id = auth.uid() AND c.nivel_acesso = 5
        )
    );

-- =====================================================
-- 5. POLÍTICAS RLS - ANALYSES
-- =====================================================

DROP POLICY IF EXISTS "Análises públicas são visíveis para todos" ON public.analyses;
CREATE POLICY "Análises públicas são visíveis para todos"
    ON public.analyses FOR SELECT
    TO authenticated
    USING (publico = true AND ativo = true);

DROP POLICY IF EXISTS "Análises da divisão são visíveis para usuários da divisão" ON public.analyses;
CREATE POLICY "Análises da divisão são visíveis para usuários da divisão"
    ON public.analyses FOR SELECT
    TO authenticated
    USING (
        divisao_restrita_id IS NOT NULL AND ativo = true AND
        divisao_restrita_id IN (
            SELECT divisao_id FROM public.usuarios WHERE id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Administradores podem ver todas análises" ON public.analyses;
CREATE POLICY "Administradores podem ver todas análises"
    ON public.analyses FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.usuarios u
            LEFT JOIN public.cargos c ON u.cargo_id = c.id
            WHERE u.id = auth.uid() AND c.nivel_acesso >= 4
        )
    );

DROP POLICY IF EXISTS "Apenas administradores podem gerenciar análises" ON public.analyses;
CREATE POLICY "Apenas administradores podem gerenciar análises"
    ON public.analyses FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.usuarios u
            LEFT JOIN public.cargos c ON u.cargo_id = c.id
            WHERE u.id = auth.uid() AND c.nivel_acesso = 5
        )
    );

-- =====================================================
-- 6. GRANTS - PERMISSÕES
-- =====================================================

GRANT SELECT ON public.cargos TO authenticated;
GRANT SELECT ON public.divisoes TO authenticated;
GRANT ALL ON public.usuarios TO authenticated;
GRANT SELECT ON public.analyses TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- =====================================================
-- 7. VERIFICAÇÃO
-- =====================================================

SELECT 'RLS configurado com sucesso!' as status, NOW() as timestamp;

SELECT schemaname, tablename, COUNT(*) as policies_count
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('cargos', 'divisoes', 'usuarios', 'analyses')
GROUP BY schemaname, tablename
ORDER BY tablename;

-- =====================================================
-- FIM DO SETUP RLS
-- =====================================================
