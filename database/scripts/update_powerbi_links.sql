-- ===============================================
-- SCRIPT: Atualizar Links dos Dashboards Power BI
-- ===============================================
-- Execute este script no SQL Editor do Supabase
-- após substituir os links pelos URLs reais
-- ===============================================

-- Limpar dados de exemplo (opcional)
-- DELETE FROM public.analyses;

-- ===============================================
-- DASHBOARD 1: SDRs (TV) v2.0
-- ===============================================
-- Substitua 'SEU_LINK_POWERBI_1_AQUI' pelo link real

INSERT INTO public.analyses (
    nome,
    descricao,
    tipo,
    embed_url,
    publico,
    ativo
) VALUES (
    'Dashboard - SDRs (TV) v2.0',
    'Dashboard de acompanhamento dos SDRs de TV',
    'powerbi',
    'SEU_LINK_POWERBI_1_AQUI',
    true,
    true
)
ON CONFLICT (id) DO UPDATE SET
    embed_url = EXCLUDED.embed_url,
    updated_at = NOW();

-- ===============================================
-- DASHBOARD 2: Compras - DW
-- ===============================================
-- Substitua 'SEU_LINK_POWERBI_2_AQUI' pelo link real

INSERT INTO public.analyses (
    nome,
    descricao,
    tipo,
    embed_url,
    publico,
    ativo
) VALUES (
    'Dashboard - Compras - DW',
    'Dashboard de compras do Data Warehouse',
    'powerbi',
    'SEU_LINK_POWERBI_2_AQUI',
    true,
    true
)
ON CONFLICT (id) DO UPDATE SET
    embed_url = EXCLUDED.embed_url,
    updated_at = NOW();

-- ===============================================
-- VERIFICAR DADOS INSERIDOS
-- ===============================================

SELECT
    id,
    nome,
    descricao,
    tipo,
    LEFT(embed_url, 50) as url_preview,
    publico,
    ativo,
    created_at
FROM public.analyses
ORDER BY created_at DESC;

-- ===============================================
-- FORMATO DOS LINKS DO POWER BI
-- ===============================================
--
-- Os links públicos do Power BI geralmente têm este formato:
-- https://app.powerbi.com/view?r=eyJrIjoiXXXXXXXX...
--
-- Para obter o link público no Power BI:
-- 1. Abra seu relatório no Power BI Service
-- 2. Clique em "Arquivo" > "Inserir relatório" > "Site ou portal"
-- 3. Copie o link que aparece na seção "Link"
-- 4. Cole aqui substituindo 'SEU_LINK_POWERBI_X_AQUI'
--
-- ===============================================
