-- ===============================================
-- RLS CORRETO - FINAL
-- ===============================================

-- LIMPAR TUDO
ALTER TABLE IF EXISTS public.usuarios DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.analyses DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.cargos DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.divisoes DISABLE ROW LEVEL SECURITY;

DO $$ 
DECLARE r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE schemaname = 'public' AND tablename = 'usuarios') LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON public.usuarios';
    END LOOP;
    FOR r IN (SELECT policyname FROM pg_policies WHERE schemaname = 'public' AND tablename = 'analyses') LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON public.analyses';
    END LOOP;
    FOR r IN (SELECT policyname FROM pg_policies WHERE schemaname = 'public' AND tablename = 'cargos') LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON public.cargos';
    END LOOP;
    FOR r IN (SELECT policyname FROM pg_policies WHERE schemaname = 'public' AND tablename = 'divisoes') LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON public.divisoes';
    END LOOP;
END $$;

-- PERMITIR NULL
ALTER TABLE public.usuarios ALTER COLUMN cargo_id DROP NOT NULL;
ALTER TABLE public.usuarios ALTER COLUMN divisao_id DROP NOT NULL;
ALTER TABLE public.usuarios ALTER COLUMN id SET NOT NULL;

-- CARGOS
ALTER TABLE public.cargos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "cargos_select" ON public.cargos FOR SELECT TO authenticated USING (ativo = true);

CREATE POLICY "cargos_manage" ON public.cargos FOR ALL TO authenticated USING (
    EXISTS (
        SELECT 1 FROM public.usuarios u
        LEFT JOIN public.cargos c ON u.cargo_id = c.id
        WHERE u.id = auth.uid() AND c.nivel_acesso = 5
    )
);

-- DIVISOES
ALTER TABLE public.divisoes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "divisoes_select" ON public.divisoes FOR SELECT TO authenticated USING (ativo = true);

CREATE POLICY "divisoes_manage" ON public.divisoes FOR ALL TO authenticated USING (
    EXISTS (
        SELECT 1 FROM public.usuarios u
        LEFT JOIN public.cargos c ON u.cargo_id = c.id
        WHERE u.id = auth.uid() AND c.nivel_acesso = 5
    )
);

-- USUARIOS
ALTER TABLE public.usuarios ENABLE ROW LEVEL SECURITY;

CREATE POLICY "usuarios_own" ON public.usuarios FOR SELECT TO authenticated USING (id = auth.uid());

CREATE POLICY "usuarios_high" ON public.usuarios FOR SELECT TO authenticated USING (
    EXISTS (
        SELECT 1 FROM public.usuarios u
        LEFT JOIN public.cargos c ON u.cargo_id = c.id
        WHERE u.id = auth.uid() AND c.nivel_acesso >= 4
    )
);

CREATE POLICY "usuarios_div" ON public.usuarios FOR SELECT TO authenticated USING (
    divisao_id IN (SELECT divisao_id FROM public.usuarios WHERE id = auth.uid())
);

CREATE POLICY "usuarios_upd" ON public.usuarios FOR UPDATE TO authenticated 
USING (id = auth.uid())
WITH CHECK (
    id = auth.uid() AND
    cargo_id = (SELECT cargo_id FROM public.usuarios WHERE id = auth.uid()) AND
    divisao_id = (SELECT divisao_id FROM public.usuarios WHERE id = auth.uid())
);

CREATE POLICY "usuarios_ins" ON public.usuarios FOR INSERT TO authenticated WITH CHECK (
    EXISTS (
        SELECT 1 FROM public.usuarios u
        LEFT JOIN public.cargos c ON u.cargo_id = c.id
        WHERE u.id = auth.uid() AND c.nivel_acesso = 5
    )
);

CREATE POLICY "usuarios_del" ON public.usuarios FOR DELETE TO authenticated USING (
    EXISTS (
        SELECT 1 FROM public.usuarios u
        LEFT JOIN public.cargos c ON u.cargo_id = c.id
        WHERE u.id = auth.uid() AND c.nivel_acesso = 5
    )
);

-- ANALYSES
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "analyses_pub" ON public.analyses FOR SELECT TO authenticated 
USING (publico = true AND ativo = true);

CREATE POLICY "analyses_div" ON public.analyses FOR SELECT TO authenticated USING (
    ativo = true AND
    divisao_restrita_id IS NOT NULL AND
    divisao_restrita_id IN (SELECT divisao_id FROM public.usuarios WHERE id = auth.uid())
);

CREATE POLICY "analyses_high" ON public.analyses FOR SELECT TO authenticated USING (
    ativo = true AND
    EXISTS (
        SELECT 1 FROM public.usuarios u
        LEFT JOIN public.cargos c ON u.cargo_id = c.id
        WHERE u.id = auth.uid() AND c.nivel_acesso >= 4
    )
);

CREATE POLICY "analyses_ins" ON public.analyses FOR INSERT TO authenticated WITH CHECK (
    EXISTS (
        SELECT 1 FROM public.usuarios u
        LEFT JOIN public.cargos c ON u.cargo_id = c.id
        WHERE u.id = auth.uid() AND c.nivel_acesso = 5
    )
);

CREATE POLICY "analyses_upd" ON public.analyses FOR UPDATE TO authenticated USING (
    EXISTS (
        SELECT 1 FROM public.usuarios u
        LEFT JOIN public.cargos c ON u.cargo_id = c.id
        WHERE u.id = auth.uid() AND c.nivel_acesso = 5
    )
);

CREATE POLICY "analyses_del" ON public.analyses FOR DELETE TO authenticated USING (
    EXISTS (
        SELECT 1 FROM public.usuarios u
        LEFT JOIN public.cargos c ON u.cargo_id = c.id
        WHERE u.id = auth.uid() AND c.nivel_acesso = 5
    )
);

-- GRANTS
GRANT SELECT ON public.cargos TO authenticated;
GRANT SELECT ON public.divisoes TO authenticated;
GRANT ALL ON public.usuarios TO authenticated;
GRANT ALL ON public.analyses TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- VERIFICAR
SELECT tablename, policyname, cmd FROM pg_policies
WHERE schemaname = 'public' AND tablename IN ('usuarios', 'analyses', 'cargos', 'divisoes')
ORDER BY tablename, cmd, policyname;
