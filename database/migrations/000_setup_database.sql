-- =====================================================
-- SETUP INICIAL DO BANCO DE DADOS
-- =====================================================
-- Script básico para criar tabelas e dados essenciais
-- Execute este ANTES dos outros scripts
-- =====================================================

-- =====================================================
-- 1. CRIAR TABELAS BÁSICAS (SEM RLS)
-- =====================================================

-- Preparar tabela cargos para evitar conflitos
DO $$
BEGIN
    -- Remover constraint de check se existir
    IF EXISTS (
        SELECT 1 FROM information_schema.check_constraints
        WHERE constraint_schema = 'public'
        AND constraint_name = 'cargos_nivel_acesso_check'
    ) THEN
        ALTER TABLE public.cargos DROP CONSTRAINT cargos_nivel_acesso_check;
        RAISE NOTICE 'Constraint cargos_nivel_acesso_check removida';
    END IF;

    -- Se a tabela já existe, garantir que não há dados conflitantes
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'cargos'
    ) THEN
        -- Remover dados existentes que podem conflitar
        DELETE FROM public.cargos WHERE nivel_acesso > 5 OR nivel_acesso < 1;
        RAISE NOTICE 'Dados conflitantes removidos da tabela cargos';
    END IF;
END $$;

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

-- =====================================================
-- 2. INSERIR DADOS BÁSICOS
-- =====================================================

-- Cargos
INSERT INTO public.cargos (nome, descricao, nivel_acesso) VALUES
    ('Administrador', 'Acesso total ao sistema', 5),
    ('Gerente', 'Acesso gerencial', 4),
    ('Coordenador', 'Coordenação de equipes', 3),
    ('Analista', 'Análise de dados', 2),
    ('Assistente', 'Suporte operacional', 1)
ON CONFLICT (nome) DO NOTHING;

-- Divisões
INSERT INTO public.divisoes (nome, descricao, codigo) VALUES
    ('Tecnologia da Informação', 'Departamento de TI', 'TI'),
    ('Recursos Humanos', 'Departamento de RH', 'RH'),
    ('Financeiro', 'Departamento Financeiro', 'FIN'),
    ('Comercial', 'Departamento Comercial', 'COM'),
    ('Operações', 'Departamento de Operações', 'OPS')
ON CONFLICT (nome) DO NOTHING;

-- =====================================================
-- 3. VERIFICAÇÃO
-- =====================================================

SELECT 'Cargos criados:' as info, COUNT(*) as total FROM public.cargos
UNION ALL
SELECT 'Divisões criadas:', COUNT(*) FROM public.divisoes;

-- =====================================================
-- FIM DO SETUP BÁSICO
-- =====================================================
