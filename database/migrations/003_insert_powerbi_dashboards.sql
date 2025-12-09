-- =====================================================
-- Analytics Platform - Insert Power BI Dashboards
-- =====================================================
-- Insere os dashboards do Power BI com as regras de acesso específicas
-- =====================================================

-- =====================================================
-- 1. VERIFICAR E CRIAR TABELA DIVISOES (se necessário)
-- =====================================================

-- Criar tabela divisoes se não existir
CREATE TABLE IF NOT EXISTS public.divisoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    codigo VARCHAR(20) UNIQUE,
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Inserir divisões padrão se não existirem
INSERT INTO public.divisoes (nome, descricao, codigo) VALUES
    ('Tecnologia da Informação', 'Departamento de TI', 'TI'),
    ('Recursos Humanos', 'Departamento de RH', 'RH'),
    ('Financeiro', 'Departamento Financeiro', 'FIN'),
    ('Comercial', 'Departamento Comercial', 'COM'),
    ('Operações', 'Departamento de Operações', 'OPS')
ON CONFLICT (nome) DO NOTHING;

-- =====================================================
-- 2. LIMPAR DADOS EXISTENTES (se necessário)
-- =====================================================

-- Remover dashboards existentes para reinserir com configurações atualizadas
DELETE FROM public.analyses WHERE tipo = 'powerbi';

-- =====================================================
-- 2. VERIFICAÇÃO DE PRÉ-REQUISITOS
-- =====================================================

-- Verificar se as divisões existem antes de inserir
DO $$
BEGIN
    -- Verificar se existem divisões
    IF NOT EXISTS (SELECT 1 FROM public.divisoes WHERE codigo IN ('FIN', 'COM')) THEN
        RAISE EXCEPTION 'Divisões necessárias não encontradas. Execute primeiro: database/migrations/001_create_base_tables.sql';
    END IF;
END $$;

-- =====================================================
-- 3. INSERIR DASHBOARDS COM REGRAS DE ACESSO
-- =====================================================

-- Dashboard Compras - DW (Financeiro + Diretoria)
-- Acesso: Diretoria (nivel_acesso >= 4) + Divisão Financeiro
INSERT INTO public.analyses (
    nome,
    descricao,
    tipo,
    embed_url,
    divisao_restrita_id,
    publico,
    ativo
) SELECT
    'Dashboard - Compras - DW',
    'Dashboard de compras do Data Warehouse - Acesso restrito para diretoria e setor financeiro',
    'powerbi',
    'https://app.powerbi.com/reportEmbed?reportId=32dfd7cf-1c98-4667-aac0-792638f9b675&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea',
    d.id,
    false,  -- Não é público
    true    -- Está ativo
FROM public.divisoes d
WHERE d.codigo = 'FIN';

-- Dashboard SDR's (TV) v2.0 (Comercial + Diretoria)
-- Acesso: Diretoria (nivel_acesso >= 4) + Divisão Comercial
INSERT INTO public.analyses (
    nome,
    descricao,
    tipo,
    embed_url,
    divisao_restrita_id,
    publico,
    ativo
) SELECT
    'Dashboard - SDRs (TV) v2.0',
    'Dashboard de acompanhamento dos SDRs de TV - Acesso restrito para diretoria e setor comercial',
    'powerbi',
    'https://app.powerbi.com/view?r=eyJrIjoiZWFjNWE1M2UtOGJmZi00YmU4LWIzNjAtYmE0OTY3YWIwOGY4IiwidCI6IjU1MjVhN2E4LTNlMzgtNDYwZC04OTY3LWM1MjYwYWY4ZTllYSJ9',
    d.id,
    false,  -- Não é público
    true    -- Está ativo
FROM public.divisoes d
WHERE d.codigo = 'COM';

-- Dashboard Contratos/Pastas (Comercial + Diretoria)
-- Acesso: Diretoria (nivel_acesso >= 4) + Divisão Comercial
INSERT INTO public.analyses (
    nome,
    descricao,
    tipo,
    embed_url,
    divisao_restrita_id,
    publico,
    ativo
) SELECT
    'Dashboard - Contratos',
    'Dashboard de contratos e pastas - Acesso restrito para diretoria e setor comercial',
    'powerbi',
    'https://app.powerbi.com/reportEmbed?reportId=40da54e1-9a7d-466d-8f60-c5efe35bd69e&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea',
    d.id,
    false,  -- Não é público
    true    -- Está ativo
FROM public.divisoes d
WHERE d.codigo = 'COM';

-- =====================================================
-- 3. VERIFICAÇÃO DOS DADOS INSERIDOS
-- =====================================================

-- Verificar dashboards inseridos
SELECT
    a.nome,
    a.descricao,
    a.tipo,
    COALESCE(d.nome, 'Diretoria (acesso irrestrito)') as divisao_nome,
    COALESCE(d.codigo, 'N/A') as divisao_codigo,
    a.publico,
    a.ativo
FROM public.analyses a
LEFT JOIN public.divisoes d ON a.divisao_restrita_id = d.id
WHERE a.tipo = 'powerbi'
ORDER BY a.nome;

-- =====================================================
-- 4. NOTAS IMPORTANTES
-- =====================================================
/*
REGRAS DE ACESSO IMPLEMENTADAS:

1. Dashboard Compras - DW:
   - Diretoria (nivel_acesso >= 4): ✅ Acesso total
   - Divisão Financeiro (FIN): ✅ Acesso permitido
   - Outras divisões: ❌ Bloqueado

2. Dashboard SDR's (TV) v2.0:
   - Diretoria (nivel_acesso >= 4): ✅ Acesso total
   - Divisão Comercial (COM): ✅ Acesso permitido
   - Outras divisões: ❌ Bloqueado

3. Dashboard Contratos:
   - Diretoria (nivel_acesso >= 4): ✅ Acesso total
   - Divisão Comercial (COM): ✅ Acesso permitido
   - Outras divisões: ❌ Bloqueado

NOTAS TÉCNICAS:
- Os dashboards não são públicos (publico = false)
- Cada dashboard está restrito a uma divisão específica
- A RLS garante que apenas usuários autorizados vejam os dashboards
- Diretoria tem acesso irrestrito independente da divisão
*/

-- =====================================================
-- FIM DO SCRIPT
-- =====================================================
