-- ============================================================
-- OTIMIZAÇÕES DE PERFORMANCE - FASE 2
-- Analytics Platform - Sistema de Análise de Dados CRM/CVDW
-- ============================================================

-- ============================================================
-- 1. ÍNDICES PARA TABELA DE VENDAS
-- ============================================================

-- Índice para consultas por data
CREATE INDEX IF NOT EXISTS idx_vendas_data
ON vendas(data_venda);

-- Índice para consultas por cliente
CREATE INDEX IF NOT EXISTS idx_vendas_cliente
ON vendas(cliente_id);

-- Índice para consultas por valor
CREATE INDEX IF NOT EXISTS idx_vendas_valor
ON vendas(valor_venda);

-- Índice composto para consultas por data e cliente (muito comum)
CREATE INDEX IF NOT EXISTS idx_vendas_data_cliente
ON vendas(data_venda, cliente_id);

-- Índice composto para consultas por data e categoria
CREATE INDEX IF NOT EXISTS idx_vendas_data_categoria
ON vendas(data_venda, categoria_produto);

-- ============================================================
-- 2. ÍNDICES PARA TABELA DE PRODUTOS
-- ============================================================

-- Índice para consultas por categoria
CREATE INDEX IF NOT EXISTS idx_produtos_categoria
ON produtos(categoria);

-- Índice para consultas por nome (busca parcial)
CREATE INDEX IF NOT EXISTS idx_produtos_nome
ON produtos USING gin(nome gin_trgm_ops);

-- ============================================================
-- 3. ÍNDICES PARA TABELA DE CLIENTES
-- ============================================================

-- Índice para consultas por divisão
CREATE INDEX IF NOT EXISTS idx_clientes_divisao
ON clientes(divisao_id);

-- Índice para consultas por status
CREATE INDEX IF NOT EXISTS idx_clientes_status
ON clientes(status);

-- Índice para busca por nome
CREATE INDEX IF NOT EXISTS idx_clientes_nome
ON clientes USING gin(nome gin_trgm_ops);

-- ============================================================
-- 4. ÍNDICES PARA TABELA DE ESTOQUE
-- ============================================================

-- Índice para consultas por produto
CREATE INDEX IF NOT EXISTS idx_estoque_produto
ON estoque(produto_id);

-- ============================================================
-- 5. MATERIALIZED VIEW - KPIs MENSAIS
-- ============================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_kpis_mensais AS
SELECT
    DATE_TRUNC('month', data_venda) as mes,
    COUNT(*) as total_vendas,
    SUM(valor_venda) as receita_total,
    AVG(valor_venda) as ticket_medio,
    COUNT(DISTINCT cliente_id) as clientes_unicos,
    MIN(valor_venda) as menor_venda,
    MAX(valor_venda) as maior_venda,
    STDDEV(valor_venda) as desvio_padrao_valor
FROM vendas
WHERE data_venda >= '2024-01-01'
GROUP BY DATE_TRUNC('month', data_venda)
ORDER BY mes DESC;

-- Índice para a materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_kpis_mensais_mes
ON mv_kpis_mensais(mes);

-- ============================================================
-- 6. MATERIALIZED VIEW - TOP PRODUTOS
-- ============================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_top_produtos AS
WITH produto_stats AS (
    SELECT
        p.id,
        p.nome,
        p.categoria,
        COUNT(pv.id) as quantidade_vendas,
        SUM(pv.valor_total) as receita_total,
        AVG(pv.valor_unitario) as preco_medio,
        SUM(pv.quantidade) as unidades_vendidas,
        MAX(v.data_venda) as ultima_venda
    FROM produtos p
    LEFT JOIN produtos_venda pv ON p.id = pv.produto_id
    LEFT JOIN vendas v ON pv.venda_id = v.id
    WHERE v.data_venda >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY p.id, p.nome, p.categoria
)
SELECT
    *,
    RANK() OVER (ORDER BY receita_total DESC) as ranking_receita,
    RANK() OVER (ORDER BY quantidade_vendas DESC) as ranking_vendas
FROM produto_stats
WHERE receita_total > 0
ORDER BY receita_total DESC
LIMIT 100;

-- Índice para a materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_top_produtos_id
ON mv_top_produtos(id);

-- ============================================================
-- 7. MATERIALIZED VIEW - TOP CLIENTES
-- ============================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_top_clientes AS
WITH cliente_stats AS (
    SELECT
        c.id,
        c.nome,
        c.divisao_id,
        COUNT(v.id) as total_compras,
        SUM(v.valor_venda) as valor_total,
        AVG(v.valor_venda) as ticket_medio,
        MAX(v.data_venda) as ultima_compra,
        MIN(v.data_venda) as primeira_compra,
        EXTRACT(days FROM (MAX(v.data_venda) - MIN(v.data_venda))) as dias_como_cliente
    FROM clientes c
    LEFT JOIN vendas v ON c.id = v.cliente_id
    WHERE v.data_venda >= CURRENT_DATE - INTERVAL '180 days'
    GROUP BY c.id, c.nome, c.divisao_id
)
SELECT
    *,
    RANK() OVER (ORDER BY valor_total DESC) as ranking_valor,
    RANK() OVER (ORDER BY total_compras DESC) as ranking_frequencia,
    CASE
        WHEN EXTRACT(days FROM (CURRENT_DATE - ultima_compra)) <= 30 THEN 'ativo'
        WHEN EXTRACT(days FROM (CURRENT_DATE - ultima_compra)) <= 90 THEN 'regular'
        ELSE 'inativo'
    END as status_atividade
FROM cliente_stats
WHERE valor_total > 0
ORDER BY valor_total DESC
LIMIT 100;

-- Índice para a materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_top_clientes_id
ON mv_top_clientes(id);

-- ============================================================
-- 8. FUNÇÕES PARA REFRESH DAS MATERIALIZED VIEWS
-- ============================================================

-- Função para atualizar KPIs mensais
CREATE OR REPLACE FUNCTION refresh_kpis_mensais()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_kpis_mensais;
END;
$$ LANGUAGE plpgsql;

-- Função para atualizar top produtos
CREATE OR REPLACE FUNCTION refresh_top_produtos()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_produtos;
END;
$$ LANGUAGE plpgsql;

-- Função para atualizar top clientes
CREATE OR REPLACE FUNCTION refresh_top_clientes()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_clientes;
END;
$$ LANGUAGE plpgsql;

-- Função para atualizar todas as views
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS void AS $$
BEGIN
    PERFORM refresh_kpis_mensais();
    PERFORM refresh_top_produtos();
    PERFORM refresh_top_clientes();
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 9. TRIGGER PARA AUTO-REFRESH (OPCIONAL)
-- ============================================================

-- Criar tabela para controle de refresh
CREATE TABLE IF NOT EXISTS mv_refresh_log (
    id SERIAL PRIMARY KEY,
    view_name VARCHAR(100) NOT NULL,
    refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_ms INTEGER,
    status VARCHAR(20)
);

-- Função para log de refresh
CREATE OR REPLACE FUNCTION log_mv_refresh(
    p_view_name VARCHAR(100),
    p_duration_ms INTEGER,
    p_status VARCHAR(20)
)
RETURNS void AS $$
BEGIN
    INSERT INTO mv_refresh_log (view_name, duration_ms, status)
    VALUES (p_view_name, p_duration_ms, p_status);
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 10. VIEWS NORMAIS (NÃO MATERIALIZADAS) PARA DADOS EM TEMPO REAL
-- ============================================================

-- View para vendas do dia
CREATE OR REPLACE VIEW v_vendas_hoje AS
SELECT
    COUNT(*) as total_vendas,
    SUM(valor_venda) as receita_total,
    AVG(valor_venda) as ticket_medio,
    COUNT(DISTINCT cliente_id) as clientes_unicos,
    MAX(data_venda) as ultima_venda
FROM vendas
WHERE DATE(data_venda) = CURRENT_DATE;

-- View para alertas de estoque
CREATE OR REPLACE VIEW v_alertas_estoque AS
SELECT
    p.id,
    p.nome,
    p.categoria,
    COALESCE(SUM(e.quantidade), 0) as estoque_atual,
    CASE
        WHEN COALESCE(SUM(e.quantidade), 0) = 0 THEN 'CRÍTICO'
        WHEN COALESCE(SUM(e.quantidade), 0) < 10 THEN 'BAIXO'
        WHEN COALESCE(SUM(e.quantidade), 0) < 50 THEN 'ATENÇÃO'
        ELSE 'OK'
    END as status_estoque
FROM produtos p
LEFT JOIN estoque e ON p.id = e.produto_id
GROUP BY p.id, p.nome, p.categoria
ORDER BY estoque_atual ASC;

-- ============================================================
-- 11. EXTENSÕES NECESSÁRIAS
-- ============================================================

-- Habilitar extensão pg_trgm para busca parcial de texto
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Habilitar extensão para estatísticas avançadas
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- ============================================================
-- 12. ANÁLISE E VACUUM
-- ============================================================

-- Atualizar estatísticas das tabelas
ANALYZE vendas;
ANALYZE produtos;
ANALYZE clientes;
ANALYZE estoque;

-- Comentários úteis
COMMENT ON MATERIALIZED VIEW mv_kpis_mensais IS 'KPIs mensais agregados para performance - Refresh diário recomendado';
COMMENT ON MATERIALIZED VIEW mv_top_produtos IS 'Top 100 produtos por receita nos últimos 90 dias - Refresh semanal recomendado';
COMMENT ON MATERIALIZED VIEW mv_top_clientes IS 'Top 100 clientes por valor nos últimos 180 dias - Refresh semanal recomendado';

-- ============================================================
-- FIM DO SCRIPT
-- ============================================================
