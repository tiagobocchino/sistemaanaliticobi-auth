-- ============================================================
-- RECRIAR MATERIALIZED VIEWS COM FILTROS ATUALIZADOS
-- Execute este script após o 001_performance_optimization.sql
-- ============================================================

-- ============================================================
-- 1. DROPAR VIEWS ANTIGAS
-- ============================================================

DROP MATERIALIZED VIEW IF EXISTS mv_kpis_mensais_vendas CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_top_corretores CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_top_empreendimentos CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_funil_conversao CASCADE;

-- ============================================================
-- 2. RECRIAR MATERIALIZED VIEW - KPIs MENSAIS DE VENDAS
-- ============================================================

CREATE MATERIALIZED VIEW mv_kpis_mensais_vendas AS
SELECT
    DATE_TRUNC('month', data_venda) as mes,
    COUNT(*) as total_vendas,
    SUM(valor_contrato) as vgv_total,
    AVG(valor_contrato) as ticket_medio,
    COUNT(DISTINCT idcliente) as clientes_unicos,
    COUNT(DISTINCT idcorretor) as corretores_ativos,
    COUNT(DISTINCT idempreendimento) as empreendimentos_ativos,
    MIN(valor_contrato) as menor_venda,
    MAX(valor_contrato) as maior_venda,
    STDDEV(valor_contrato) as desvio_padrao_valor
FROM vendas
WHERE data_venda IS NOT NULL
GROUP BY DATE_TRUNC('month', data_venda)
ORDER BY mes DESC;

-- Índice para a materialized view
CREATE UNIQUE INDEX idx_mv_kpis_mensais_vendas_mes
ON mv_kpis_mensais_vendas(mes);

-- ============================================================
-- 3. RECRIAR MATERIALIZED VIEW - TOP CORRETORES
-- ============================================================

CREATE MATERIALIZED VIEW mv_top_corretores AS
WITH corretor_stats AS (
    SELECT
        v.idcorretor,
        v.corretor,
        COUNT(*) as total_vendas,
        SUM(v.valor_contrato) as vgv_total,
        AVG(v.valor_contrato) as ticket_medio,
        MAX(v.data_venda) as ultima_venda,
        MIN(v.data_venda) as primeira_venda,
        COUNT(DISTINCT v.idempreendimento) as empreendimentos_distintos,
        COUNT(DISTINCT v.idcliente) as clientes_distintos
    FROM vendas v
    WHERE v.data_venda IS NOT NULL
      AND v.idcorretor IS NOT NULL
    GROUP BY v.idcorretor, v.corretor
)
SELECT
    *,
    RANK() OVER (ORDER BY vgv_total DESC) as ranking_vgv,
    RANK() OVER (ORDER BY total_vendas DESC) as ranking_quantidade
FROM corretor_stats
WHERE vgv_total > 0
ORDER BY vgv_total DESC
LIMIT 100;

-- Índice para a materialized view
CREATE UNIQUE INDEX idx_mv_top_corretores_id
ON mv_top_corretores(idcorretor);

-- ============================================================
-- 4. RECRIAR MATERIALIZED VIEW - TOP EMPREENDIMENTOS
-- ============================================================

CREATE MATERIALIZED VIEW mv_top_empreendimentos AS
WITH empreendimento_stats AS (
    SELECT
        v.idempreendimento,
        v.empreendimento,
        v.regiao,
        COUNT(*) as total_vendas,
        SUM(v.valor_contrato) as vgv_total,
        AVG(v.valor_contrato) as ticket_medio,
        MAX(v.data_venda) as ultima_venda,
        MIN(v.data_venda) as primeira_venda,
        COUNT(DISTINCT v.idcorretor) as corretores_distintos,
        COUNT(DISTINCT v.idcliente) as clientes_distintos
    FROM vendas v
    WHERE v.data_venda IS NOT NULL
      AND v.idempreendimento IS NOT NULL
    GROUP BY v.idempreendimento, v.empreendimento, v.regiao
)
SELECT
    *,
    RANK() OVER (ORDER BY vgv_total DESC) as ranking_vgv,
    RANK() OVER (ORDER BY total_vendas DESC) as ranking_quantidade,
    CASE
        WHEN EXTRACT(days FROM (CURRENT_DATE - ultima_venda)) <= 30 THEN 'ativo'
        WHEN EXTRACT(days FROM (CURRENT_DATE - ultima_venda)) <= 90 THEN 'regular'
        ELSE 'inativo'
    END as status_atividade
FROM empreendimento_stats
WHERE vgv_total > 0
ORDER BY vgv_total DESC
LIMIT 100;

-- Índice para a materialized view
CREATE UNIQUE INDEX idx_mv_top_empreendimentos_id
ON mv_top_empreendimentos(idempreendimento);

-- ============================================================
-- 5. RECRIAR MATERIALIZED VIEW - FUNIL DE CONVERSÃO
-- ============================================================

CREATE MATERIALIZED VIEW mv_funil_conversao AS
WITH monthly_funnel AS (
    SELECT
        DATE_TRUNC('month', l.data_cad) as mes,
        COUNT(DISTINCT l.idlead) as total_leads,
        COUNT(DISTINCT CASE WHEN r.idreserva IS NOT NULL THEN l.idlead END) as leads_com_reserva,
        COUNT(DISTINCT CASE WHEN v.idreserva IS NOT NULL THEN l.idlead END) as leads_com_venda,
        COUNT(DISTINCT r.idreserva) as total_reservas,
        COUNT(DISTINCT v.idreserva) as total_vendas,
        SUM(CASE WHEN v.idreserva IS NOT NULL THEN v.valor_contrato ELSE 0 END) as vgv_vendas
    FROM leads l
    LEFT JOIN reservas r ON (
        r.idlead = l.idlead::text
        OR r.idlead LIKE l.idlead::text || ',%'
        OR r.idlead LIKE '%,' || l.idlead::text || ',%'
        OR r.idlead LIKE '%,' || l.idlead::text
    )
    LEFT JOIN vendas v ON l.idlead = v.idlead
    WHERE l.data_cad IS NOT NULL
    GROUP BY DATE_TRUNC('month', l.data_cad)
)
SELECT
    mes,
    total_leads,
    leads_com_reserva,
    leads_com_venda,
    total_reservas,
    total_vendas,
    vgv_vendas,
    CASE
        WHEN total_leads > 0 THEN ROUND((leads_com_reserva::numeric / total_leads::numeric * 100), 2)
        ELSE 0
    END as taxa_conversao_lead_reserva,
    CASE
        WHEN leads_com_reserva > 0 THEN ROUND((leads_com_venda::numeric / leads_com_reserva::numeric * 100), 2)
        ELSE 0
    END as taxa_conversao_reserva_venda,
    CASE
        WHEN total_leads > 0 THEN ROUND((leads_com_venda::numeric / total_leads::numeric * 100), 2)
        ELSE 0
    END as taxa_conversao_total
FROM monthly_funnel
ORDER BY mes DESC;

-- Índice para a materialized view
CREATE UNIQUE INDEX idx_mv_funil_conversao_mes
ON mv_funil_conversao(mes);

-- ============================================================
-- 6. FAZER PRIMEIRA CARGA DAS VIEWS
-- ============================================================

-- Não precisa fazer REFRESH pois as views já são criadas com dados
-- Mas se quiser forçar um refresh:
-- SELECT refresh_all_materialized_views();

-- ============================================================
-- 7. VALIDAR CRIAÇÃO
-- ============================================================

-- Verificar contagem de registros
SELECT
    'mv_kpis_mensais_vendas' as view_name,
    COUNT(*) as total_linhas
FROM mv_kpis_mensais_vendas
UNION ALL
SELECT 'mv_top_corretores', COUNT(*) FROM mv_top_corretores
UNION ALL
SELECT 'mv_top_empreendimentos', COUNT(*) FROM mv_top_empreendimentos
UNION ALL
SELECT 'mv_funil_conversao', COUNT(*) FROM mv_funil_conversao;

-- ============================================================
-- FIM DO SCRIPT
-- ============================================================
