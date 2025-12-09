-- =====================================================
-- DASHBOARDS POWER BI - VERSÃO SIMPLIFICADA
-- =====================================================
-- Execute este script se o outro falhar
-- =====================================================

-- Criar tabela divisoes se não existir (simplificada)
CREATE TABLE IF NOT EXISTS public.divisoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    codigo VARCHAR(20) UNIQUE,
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Inserir divisões se não existirem
INSERT INTO public.divisoes (nome, descricao, codigo) VALUES
    ('Financeiro', 'Departamento Financeiro', 'FIN'),
    ('Comercial', 'Departamento Comercial', 'COM')
ON CONFLICT (nome) DO NOTHING;

-- Criar tabela analyses se não existir
CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50) NOT NULL,
    embed_url TEXT NOT NULL,
    divisao_restrita_id UUID REFERENCES public.divisoes(id),
    publico BOOLEAN NOT NULL DEFAULT true,
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Limpar dashboards existentes
DELETE FROM public.analyses WHERE tipo = 'powerbi';

-- Inserir dashboards com NULL temporário (será atualizado depois)
INSERT INTO public.analyses (
    nome,
    descricao,
    tipo,
    embed_url,
    divisao_restrita_id,
    publico,
    ativo
) VALUES
    (
        'Dashboard - Compras - DW',
        'Dashboard de compras do Data Warehouse - Acesso: Diretoria + Financeiro',
        'powerbi',
        'https://app.powerbi.com/reportEmbed?reportId=32dfd7cf-1c98-4667-aac0-792638f9b675&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea',
        NULL, -- Será atualizado
        false,
        true
    ),
    (
        'Dashboard - SDRs (TV) v2.0',
        'Dashboard de SDRs - Acesso: Diretoria + Comercial',
        'powerbi',
        'https://app.powerbi.com/view?r=eyJrIjoiZWFjNWE1M2UtOGJmZi00YmU4LWIzNjAtYmE0OTY3YWIwOGY4IiwidCI6IjU1MjVhN2E4LTNlMzgtNDYwZC04OTY3LWM1MjYwYWY4ZTllYSJ9',
        NULL, -- Será atualizado
        false,
        true
    ),
    (
        'Dashboard - Contratos',
        'Dashboard de contratos e pastas - Acesso: Diretoria + Comercial',
        'powerbi',
        'https://app.powerbi.com/reportEmbed?reportId=40da54e1-9a7d-466d-8f60-c5efe35bd69e&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea',
        NULL, -- Será atualizado
        false,
        true
    );

-- Atualizar referências das divisões
UPDATE public.analyses
SET divisao_restrita_id = (SELECT id FROM public.divisoes WHERE codigo = 'FIN' LIMIT 1)
WHERE nome = 'Dashboard - Compras - DW';

UPDATE public.analyses
SET divisao_restrita_id = (SELECT id FROM public.divisoes WHERE codigo = 'COM' LIMIT 1)
WHERE nome IN ('Dashboard - SDRs (TV) v2.0', 'Dashboard - Contratos');

-- Verificar resultado
SELECT
    a.nome,
    a.descricao,
    a.tipo,
    COALESCE(d.nome, 'Não configurado') as divisao,
    COALESCE(d.codigo, 'N/A') as codigo,
    a.publico,
    a.ativo
FROM public.analyses a
LEFT JOIN public.divisoes d ON a.divisao_restrita_id = d.id
WHERE a.tipo = 'powerbi'
ORDER BY a.nome;
