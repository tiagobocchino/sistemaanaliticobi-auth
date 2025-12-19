-- ============================================================
-- PASSO 4: CRIAR VIEW - TOP EMPREENDIMENTOS
-- Execute após 002c
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

CREATE UNIQUE INDEX idx_mv_top_empreendimentos_id
ON mv_top_empreendimentos(idempreendimento);

-- Verificar
SELECT COUNT(*) as total_linhas FROM mv_top_empreendimentos;
