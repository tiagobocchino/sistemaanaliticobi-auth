-- ============================================================
-- PASSO 5: CRIAR VIEW - FUNIL DE CONVERSÃO (SIMPLIFICADO)
-- Execute após 002d
-- ============================================================
-- NOTA: Versão simplificada sem JOINs complexos para evitar timeout

CREATE MATERIALIZED VIEW mv_funil_conversao AS
WITH monthly_leads AS (
    SELECT
        DATE_TRUNC('month', data_cad) as mes,
        COUNT(DISTINCT idlead) as total_leads
    FROM leads
    WHERE data_cad IS NOT NULL
    GROUP BY DATE_TRUNC('month', data_cad)
),
monthly_reservas AS (
    SELECT
        DATE_TRUNC('month', data_cad) as mes,
        COUNT(DISTINCT idreserva) as total_reservas,
        SUM(valor_contrato) as vgv_reservas
    FROM reservas
    WHERE data_cad IS NOT NULL
    GROUP BY DATE_TRUNC('month', data_cad)
),
monthly_vendas AS (
    SELECT
        DATE_TRUNC('month', data_venda) as mes,
        COUNT(DISTINCT idreserva) as total_vendas,
        SUM(valor_contrato) as vgv_vendas
    FROM vendas
    WHERE data_venda IS NOT NULL
    GROUP BY DATE_TRUNC('month', data_venda)
)
SELECT
    COALESCE(l.mes, r.mes, v.mes) as mes,
    COALESCE(l.total_leads, 0) as total_leads,
    COALESCE(r.total_reservas, 0) as total_reservas,
    COALESCE(v.total_vendas, 0) as total_vendas,
    COALESCE(r.vgv_reservas, 0) as vgv_reservas,
    COALESCE(v.vgv_vendas, 0) as vgv_vendas,
    CASE
        WHEN COALESCE(l.total_leads, 0) > 0
        THEN ROUND((COALESCE(r.total_reservas, 0)::numeric / l.total_leads::numeric * 100), 2)
        ELSE 0
    END as taxa_conversao_lead_reserva,
    CASE
        WHEN COALESCE(r.total_reservas, 0) > 0
        THEN ROUND((COALESCE(v.total_vendas, 0)::numeric / r.total_reservas::numeric * 100), 2)
        ELSE 0
    END as taxa_conversao_reserva_venda,
    CASE
        WHEN COALESCE(l.total_leads, 0) > 0
        THEN ROUND((COALESCE(v.total_vendas, 0)::numeric / l.total_leads::numeric * 100), 2)
        ELSE 0
    END as taxa_conversao_total
FROM monthly_leads l
FULL OUTER JOIN monthly_reservas r ON l.mes = r.mes
FULL OUTER JOIN monthly_vendas v ON COALESCE(l.mes, r.mes) = v.mes
ORDER BY mes DESC;

CREATE UNIQUE INDEX idx_mv_funil_conversao_mes
ON mv_funil_conversao(mes);

-- Verificar
SELECT COUNT(*) as total_linhas FROM mv_funil_conversao;
