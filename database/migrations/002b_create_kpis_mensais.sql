-- ============================================================
-- PASSO 2: CRIAR VIEW - KPIs MENSAIS
-- Execute após 002a
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

CREATE UNIQUE INDEX idx_mv_kpis_mensais_vendas_mes
ON mv_kpis_mensais_vendas(mes);

-- Verificar
SELECT COUNT(*) as total_linhas FROM mv_kpis_mensais_vendas;
