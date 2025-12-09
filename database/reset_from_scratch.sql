-- =====================================================
-- SETUP COMPLETO - RESET TOTAL + AUTENTICAÇÃO
-- =====================================================
-- Apaga tudo e recria completamente:
-- ✅ Tabelas (cargos, divisoes, usuarios, analyses)
-- ✅ Dados (5 cargos, 5 divisões, 3 dashboards)
-- ✅ Trigger de criação automática de usuários
-- ✅ Row Level Security (RLS) completo
-- ✅ Políticas de acesso baseadas em cargos/divisões
-- ✅ Grants de permissão
-- =====================================================

-- Primeiro, vamos ver o que existe
SELECT schemaname, tablename
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- Remover TUDO que existir
DROP TABLE IF EXISTS public.analyses CASCADE;
DROP TABLE IF EXISTS public.usuarios CASCADE;
DROP TABLE IF EXISTS public.divisoes CASCADE;
DROP TABLE IF EXISTS public.cargos CASCADE;

-- Verificar se foi removido
SELECT 'Tabelas restantes:' as status, COUNT(*) as quantidade
FROM pg_tables
WHERE schemaname = 'public';

-- =====================================================
-- CRIAR TABELAS DO ZERO
-- =====================================================

-- 1. Cargos
CREATE TABLE public.cargos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    nivel_acesso INTEGER NOT NULL DEFAULT 1 CHECK (nivel_acesso >= 1 AND nivel_acesso <= 5),
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Divisões
CREATE TABLE public.divisoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    codigo VARCHAR(20) UNIQUE,
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Usuários
CREATE TABLE public.usuarios (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    cargo_id UUID REFERENCES public.cargos(id) ON DELETE RESTRICT,
    divisao_id UUID REFERENCES public.divisoes(id) ON DELETE RESTRICT,
    ativo BOOLEAN NOT NULL DEFAULT true,
    avatar_url TEXT,
    telefone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Análises
CREATE TABLE public.analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50) NOT NULL DEFAULT 'powerbi',
    embed_url TEXT NOT NULL,
    divisao_restrita_id UUID REFERENCES public.divisoes(id),
    publico BOOLEAN NOT NULL DEFAULT true,
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INSERIR DADOS
-- =====================================================

-- Cargos
INSERT INTO public.cargos (nome, descricao, nivel_acesso) VALUES
('Administrador', 'Acesso total ao sistema', 5),
('Gerente', 'Acesso gerencial', 4),
('Coordenador', 'Coordenação de equipes', 3),
('Analista', 'Análise de dados', 2),
('Assistente', 'Suporte operacional', 1);

-- Divisões
INSERT INTO public.divisoes (nome, descricao, codigo) VALUES
('Tecnologia da Informação', 'Departamento de TI', 'TI'),
('Recursos Humanos', 'Departamento de RH', 'RH'),
('Financeiro', 'Departamento Financeiro', 'FIN'),
('Comercial', 'Departamento Comercial', 'COM'),
('Operações', 'Departamento de Operações', 'OPS');

-- Dashboards Power BI
INSERT INTO public.analyses (nome, descricao, tipo, embed_url, divisao_restrita_id, publico)
SELECT
    'Dashboard - Compras - DW',
    'Dashboard de compras - Acesso: Diretoria + Financeiro',
    'powerbi',
    'https://app.powerbi.com/reportEmbed?reportId=32dfd7cf-1c98-4667-aac0-792638f9b675&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea',
    d.id,
    false
FROM public.divisoes d WHERE d.codigo = 'FIN';

INSERT INTO public.analyses (nome, descricao, tipo, embed_url, divisao_restrita_id, publico)
SELECT
    'Dashboard - SDRs (TV) v2.0',
    'Dashboard de SDRs - Acesso: Diretoria + Comercial',
    'powerbi',
    'https://app.powerbi.com/view?r=eyJrIjoiZWFjNWE1M2UtOGJmZi00YmU4LWIzNjAtYmE0OTY3YWIwOGY4IiwidCI6IjU1MjVhN2E4LTNlMzgtNDYwZC04OTY3LWM1MjYwYWY4ZTllYSJ9',
    d.id,
    false
FROM public.divisoes d WHERE d.codigo = 'COM';

INSERT INTO public.analyses (nome, descricao, tipo, embed_url, divisao_restrita_id, publico)
SELECT
    'Dashboard - Contratos',
    'Dashboard de contratos - Acesso: Diretoria + Comercial',
    'powerbi',
    'https://app.powerbi.com/reportEmbed?reportId=40da54e1-9a7d-466d-8f60-c5efe35bd69e&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea',
    d.id,
    false
FROM public.divisoes d WHERE d.codigo = 'COM';

-- =====================================================
-- TRIGGERS PARA UPDATED_AT
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_cargos_updated_at BEFORE UPDATE ON public.cargos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_divisoes_updated_at BEFORE UPDATE ON public.divisoes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON public.usuarios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_analyses_updated_at BEFORE UPDATE ON public.analyses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- TRIGGER DE CRIAÇÃO AUTOMÁTICA DE USUÁRIOS
-- =====================================================

-- Função que será executada pelo trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Inserir novo registro na tabela usuarios
  INSERT INTO public.usuarios (
    id,
    email,
    nome,
    cargo_id,
    divisao_id,
    ativo,
    created_at,
    updated_at
  )
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
    NULLIF((NEW.raw_user_meta_data->>'cargo_id'), '')::uuid,  -- NULL se vazio
    NULLIF((NEW.raw_user_meta_data->>'divisao_id'), '')::uuid, -- NULL se vazio
    true,
    NOW(),
    NOW()
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Remover trigger existente se houver
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Criar trigger
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- =====================================================
-- ROW LEVEL SECURITY (RLS) - CONFIGURAÇÃO COMPLETA
-- =====================================================

-- Habilitar RLS nas tabelas
ALTER TABLE public.cargos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.divisoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- POLÍTICAS RLS - CARGOS
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
-- POLÍTICAS RLS - DIVISÕES
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
-- POLÍTICAS RLS - USUÁRIOS
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
-- POLÍTICAS RLS - ANALYSES
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
-- GRANTS - PERMISSÕES
-- =====================================================

GRANT SELECT ON public.cargos TO authenticated;
GRANT SELECT ON public.divisoes TO authenticated;
GRANT ALL ON public.usuarios TO authenticated;
GRANT SELECT ON public.analyses TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- =====================================================
-- VERIFICAÇÃO FINAL
-- =====================================================

SELECT 'SETUP CONCLUÍDO!' as status, NOW() as timestamp;

-- Verificar tabelas criadas
SELECT
    'Cargos' as tabela, COUNT(*) as registros FROM public.cargos
UNION ALL
SELECT 'Divisões', COUNT(*) FROM public.divisoes
UNION ALL
SELECT 'Dashboards', COUNT(*) FROM public.analyses;

-- Verificar políticas RLS criadas
SELECT
    schemaname,
    tablename,
    COUNT(*) as policies_count
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('cargos', 'divisoes', 'usuarios', 'analyses')
GROUP BY schemaname, tablename
ORDER BY tablename;

-- Verificar estrutura das tabelas
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN ('cargos', 'divisoes', 'usuarios', 'analyses')
ORDER BY table_name, ordinal_position;

-- =====================================================
-- SETUP COMPLETO REALIZADO COM SUCESSO!
-- =====================================================
-- ✅ Tabelas criadas e populadas
-- ✅ Trigger de usuários automático configurado
-- ✅ Row Level Security (RLS) aplicado
-- ✅ Políticas de acesso configuradas
-- ✅ Grants de permissão concedidos
-- =====================================================
