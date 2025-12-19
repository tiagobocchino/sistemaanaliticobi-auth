-- ============================================================
-- PASSO 3: CRIAR VIEW - TOP CORRETORES
-- Execute após 002b
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

CREATE UNIQUE INDEX idx_mv_top_corretores_id
ON mv_top_corretores(idcorretor);

-- Verificar
SELECT COUNT(*) as total_linhas FROM mv_top_corretores;
