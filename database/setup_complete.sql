-- =====================================================
-- SETUP COMPLETO DO BANCO DE DADOS
-- =====================================================
-- Execute este script ÚNICO para configurar tudo
-- =====================================================

-- =====================================================
-- 1. SETUP BÁSICO (Tabelas + Dados)
-- =====================================================

-- Criar tabelas básicas
CREATE TABLE IF NOT EXISTS public.cargos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    nivel_acesso INTEGER NOT NULL DEFAULT 1,
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.divisoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    codigo VARCHAR(20) UNIQUE,
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.usuarios (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    cargo_id UUID REFERENCES public.cargos(id) ON DELETE RESTRICT,
    divisao_id UUID REFERENCES public.divisoes(id) ON DELETE RESTRICT,
    ativo BOOLEAN NOT NULL DEFAULT true,
    avatar_url TEXT,
    telefone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Inserir dados básicos
INSERT INTO public.cargos (nome, descricao, nivel_acesso) VALUES
    ('Administrador', 'Acesso total ao sistema', 5),
    ('Gerente', 'Acesso gerencial', 4),
    ('Coordenador', 'Coordenação de equipes', 3),
    ('Analista', 'Análise de dados', 2),
    ('Assistente', 'Suporte operacional', 1)
ON CONFLICT (nome) DO NOTHING;

INSERT INTO public.divisoes (nome, descricao, codigo) VALUES
    ('Tecnologia da Informação', 'Departamento de TI', 'TI'),
    ('Recursos Humanos', 'Departamento de RH', 'RH'),
    ('Financeiro', 'Departamento Financeiro', 'FIN'),
    ('Comercial', 'Departamento Comercial', 'COM'),
    ('Operações', 'Departamento de Operações', 'OPS')
ON CONFLICT (nome) DO NOTHING;

-- =====================================================
-- 2. TABELA ANALYSES (Dashboards)
-- =====================================================

CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50) NOT NULL DEFAULT 'powerbi',
    embed_url TEXT NOT NULL,
    divisao_restrita_id UUID REFERENCES public.divisoes(id),
    publico BOOLEAN NOT NULL DEFAULT true,
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- =====================================================
-- 3. DASHBOARDS POWER BI
-- =====================================================

-- Limpar dashboards existentes
DELETE FROM public.analyses WHERE tipo = 'powerbi';

-- Inserir dashboards com controle de acesso
INSERT INTO public.analyses (nome, descricao, tipo, embed_url, divisao_restrita_id, publico, ativo)
SELECT
    'Dashboard - Compras - DW',
    'Dashboard de compras do Data Warehouse - Acesso: Diretoria + Financeiro',
    'powerbi',
    'https://app.powerbi.com/reportEmbed?reportId=32dfd7cf-1c98-4667-aac0-792638f9b675&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea',
    d.id,
    false,
    true
FROM public.divisoes d WHERE d.codigo = 'FIN';

INSERT INTO public.analyses (nome, descricao, tipo, embed_url, divisao_restrita_id, publico, ativo)
SELECT
    'Dashboard - SDRs (TV) v2.0',
    'Dashboard de SDRs - Acesso: Diretoria + Comercial',
    'powerbi',
    'https://app.powerbi.com/view?r=eyJrIjoiZWFjNWE1M2UtOGJmZi00YmU4LWIzNjAtYmE0OTY3YWIwOGY4IiwidCI6IjU1MjVhN2E4LTNlMzgtNDYwZC04OTY3LWM1MjYwYWY4ZTllYSJ9',
    d.id,
    false,
    true
FROM public.divisoes d WHERE d.codigo = 'COM';

INSERT INTO public.analyses (nome, descricao, tipo, embed_url, divisao_restrita_id, publico, ativo)
SELECT
    'Dashboard - Contratos',
    'Dashboard de contratos e pastas - Acesso: Diretoria + Comercial',
    'powerbi',
    'https://app.powerbi.com/reportEmbed?reportId=40da54e1-9a7d-466d-8f60-c5efe35bd69e&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea',
    d.id,
    false,
    true
FROM public.divisoes d WHERE d.codigo = 'COM';

-- =====================================================
-- 4. FUNÇÕES E TRIGGERS
-- =====================================================

CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_cargos_updated_at ON public.cargos;
CREATE TRIGGER update_cargos_updated_at
    BEFORE UPDATE ON public.cargos
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_divisoes_updated_at ON public.divisoes;
CREATE TRIGGER update_divisoes_updated_at
    BEFORE UPDATE ON public.divisoes
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_usuarios_updated_at ON public.usuarios;
CREATE TRIGGER update_usuarios_updated_at
    BEFORE UPDATE ON public.usuarios
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_analyses_updated_at ON public.analyses;
CREATE TRIGGER update_analyses_updated_at
    BEFORE UPDATE ON public.analyses
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- 5. ÍNDICES
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_cargos_ativo ON public.cargos(ativo);
CREATE INDEX IF NOT EXISTS idx_cargos_nivel_acesso ON public.cargos(nivel_acesso);
CREATE INDEX IF NOT EXISTS idx_divisoes_ativo ON public.divisoes(ativo);
CREATE INDEX IF NOT EXISTS idx_divisoes_codigo ON public.divisoes(codigo);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON public.usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_cargo_id ON public.usuarios(cargo_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_divisao_id ON public.usuarios(divisao_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_ativo ON public.usuarios(ativo);
CREATE INDEX IF NOT EXISTS idx_analyses_tipo ON public.analyses(tipo);
CREATE INDEX IF NOT EXISTS idx_analyses_divisao_restrita_id ON public.analyses(divisao_restrita_id);
CREATE INDEX IF NOT EXISTS idx_analyses_publico ON public.analyses(publico);
CREATE INDEX IF NOT EXISTS idx_analyses_ativo ON public.analyses(ativo);

-- =====================================================
-- 6. VERIFICAÇÃO FINAL
-- =====================================================

SELECT
    'Setup concluído com sucesso!' as status,
    NOW() as timestamp;

SELECT 'Cargos:' as tabela, COUNT(*) as registros FROM public.cargos
UNION ALL
SELECT 'Divisões:', COUNT(*) FROM public.divisoes
UNION ALL
SELECT 'Dashboards Power BI:', COUNT(*) FROM public.analyses WHERE tipo = 'powerbi';

-- =====================================================
-- FIM DO SETUP COMPLETO
-- =====================================================
