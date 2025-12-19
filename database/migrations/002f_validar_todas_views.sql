-- ============================================================
-- PASSO 6: VALIDAR TODAS AS VIEWS
-- Execute após 002e para verificar se tudo está OK
-- ============================================================

-- Contagem de linhas em todas as views
SELECT
    'mv_kpis_mensais_vendas' as view_name,
    COUNT(*) as total_linhas
FROM mv_kpis_mensais_vendas

UNION ALL

SELECT
    'mv_top_corretores',
    COUNT(*)
FROM mv_top_corretores

UNION ALL

SELECT
    'mv_top_empreendimentos',
    COUNT(*)
FROM mv_top_empreendimentos

UNION ALL

SELECT
    'mv_funil_conversao',
    COUNT(*)
FROM mv_funil_conversao;

-- Ver exemplos de dados de cada view
-- KPIs mensais (últimos 3 meses)
SELECT 'KPIs Mensais' as view_name, * FROM mv_kpis_mensais_vendas ORDER BY mes DESC LIMIT 3;

-- Top 3 corretores
SELECT 'Top Corretores' as view_name, corretor, total_vendas, vgv_total FROM mv_top_corretores LIMIT 3;

-- Top 3 empreendimentos
SELECT 'Top Empreendimentos' as view_name, empreendimento, total_vendas, vgv_total FROM mv_top_empreendimentos LIMIT 3;

-- Funil últimos 3 meses
SELECT 'Funil Conversão' as view_name, * FROM mv_funil_conversao ORDER BY mes DESC LIMIT 3;
