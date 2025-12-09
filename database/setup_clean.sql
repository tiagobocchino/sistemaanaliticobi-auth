-- =====================================================
-- SETUP LIMPO E SEGURO DO BANCO
-- =====================================================
-- Execute este script ÚNICO para resetar tudo
-- =====================================================

-- =====================================================
-- 1. LIMPAR TUDO COMPLETAMENTE
-- =====================================================

-- Desabilitar RLS temporariamente se existir
ALTER TABLE IF EXISTS public.cargos DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.divisoes DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.usuarios DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.analyses DISABLE ROW LEVEL SECURITY;

-- Remover todas as políticas RLS
DO $$
DECLARE
    policy_record RECORD;
BEGIN
    FOR policy_record IN
        SELECT schemaname, tablename, policyname
        FROM pg_policies
        WHERE schemaname = 'public'
        AND tablename IN ('cargos', 'divisoes', 'usuarios', 'analyses')
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON %I.%I',
                      policy_record.policyname,
                      policy_record.schemaname,
                      policy_record.tablename);
    END LOOP;
END $$;

-- Forçar remoção de constraints e tabelas
DO $$
DECLARE
    table_name text;
    constraint_name text;
BEGIN
    -- Remover foreign key constraints primeiro
    FOR constraint_name IN
        SELECT con.conname
        FROM pg_constraint con
        JOIN pg_class rel ON rel.oid = con.conrelid
        WHERE rel.relname IN ('usuarios', 'analyses')
        AND con.contype = 'f'
    LOOP
        EXECUTE 'ALTER TABLE public.usuarios DROP CONSTRAINT IF EXISTS ' || constraint_name;
        EXECUTE 'ALTER TABLE public.analyses DROP CONSTRAINT IF EXISTS ' || constraint_name;
    END LOOP;

    -- Remover primary key constraints
    FOR table_name IN VALUES ('cargos'), ('divisoes'), ('usuarios'), ('analyses')
    LOOP
        EXECUTE 'ALTER TABLE public.' || table_name || ' DROP CONSTRAINT IF EXISTS ' || table_name || '_pkey';
    END LOOP;
END $$;

-- =====================================================
-- 2. RECRIAR TABELAS (LIMPO)
-- =====================================================

DROP TABLE IF EXISTS public.analyses;
DROP TABLE IF EXISTS public.usuarios;
DROP TABLE IF EXISTS public.divisoes;
DROP TABLE IF EXISTS public.cargos;

-- Criar tabelas do zero
CREATE TABLE public.cargos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    nivel_acesso INTEGER NOT NULL DEFAULT 1 CHECK (nivel_acesso >= 1 AND nivel_acesso <= 5),
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE TABLE public.divisoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    codigo VARCHAR(20) UNIQUE,
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE TABLE public.usuarios (
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

CREATE TABLE public.analyses (
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
-- 3. INSERIR DADOS BÁSICOS
-- =====================================================

INSERT INTO public.cargos (nome, descricao, nivel_acesso) VALUES
    ('Administrador', 'Acesso total ao sistema', 5),
    ('Gerente', 'Acesso gerencial', 4),
    ('Coordenador', 'Coordenação de equipes', 3),
    ('Analista', 'Análise de dados', 2),
    ('Assistente', 'Suporte operacional', 1);

INSERT INTO public.divisoes (nome, descricao, codigo) VALUES
    ('Tecnologia da Informação', 'Departamento de TI', 'TI'),
    ('Recursos Humanos', 'Departamento de RH', 'RH'),
    ('Financeiro', 'Departamento Financeiro', 'FIN'),
    ('Comercial', 'Departamento Comercial', 'COM'),
    ('Operações', 'Departamento de Operações', 'OPS');

-- =====================================================
-- 4. DASHBOARDS POWER BI
-- =====================================================

INSERT INTO public.analyses (nome, descricao, tipo, embed_url, divisao_restrita_id, publico, ativo)
SELECT
    'Dashboard - Compras - DW',
    'Dashboard de compras - Acesso: Diretoria + Financeiro',
    'powerbi',
    'https://app.powerbi.com/reportEmbed?reportId=32dfd7cf-1c98-4667-aac0-792638f9b675&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea',
    d.id, false, true
FROM public.divisoes d WHERE d.codigo = 'FIN';

INSERT INTO public.analyses (nome, descricao, tipo, embed_url, divisao_restrita_id, publico, ativo)
SELECT
    'Dashboard - SDRs (TV) v2.0',
    'Dashboard de SDRs - Acesso: Diretoria + Comercial',
    'powerbi',
    'https://app.powerbi.com/view?r=eyJrIjoiZWFjNWE1M2UtOGJmZi00YmU4LWIzNjAtYmE0OTY3YWIwOGY4IiwidCI6IjU1MjVhN2E4LTNlMzgtNDYwZC04OTY3LWM1MjYwYWY4ZTllYSJ9',
    d.id, false, true
FROM public.divisoes d WHERE d.codigo = 'COM';

INSERT INTO public.analyses (nome, descricao, tipo, embed_url, divisao_restrita_id, publico, ativo)
SELECT
    'Dashboard - Contratos',
    'Dashboard de contratos - Acesso: Diretoria + Comercial',
    'powerbi',
    'https://app.powerbi.com/reportEmbed?reportId=40da54e1-9a7d-466d-8f60-c5efe35bd69e&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea',
    d.id, false, true
FROM public.divisoes d WHERE d.codigo = 'COM';

-- =====================================================
-- 5. ÍNDICES E TRIGGERS
-- =====================================================

CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_cargos_updated_at BEFORE UPDATE ON public.cargos FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_divisoes_updated_at BEFORE UPDATE ON public.divisoes FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON public.usuarios FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_analyses_updated_at BEFORE UPDATE ON public.analyses FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- 6. VERIFICAÇÃO
-- =====================================================

SELECT 'Setup limpo concluído!' as status, NOW() as timestamp;

SELECT 'Cargos:' as tabela, COUNT(*) as total FROM public.cargos
UNION ALL
SELECT 'Divisões:', COUNT(*) FROM public.divisoes
UNION ALL
SELECT 'Dashboards:', COUNT(*) FROM public.analyses;

-- =====================================================
-- FIM DO SETUP LIMPO
-- =====================================================
