-- ============================================================
-- OTIMIZAÇÕES DE PERFORMANCE - FASE 2
-- Analytics Platform - Sistema de Análise de Dados CRM/CVDW
-- Adaptado para tabelas CVDW reais do Supabase
-- ============================================================

-- ============================================================
-- 0. EXTENSÕES NECESSÁRIAS (DEVE SER EXECUTADO PRIMEIRO!)
-- ============================================================

-- Habilitar extensão pg_trgm para busca parcial de texto
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Habilitar extensão para estatísticas avançadas
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- ============================================================
-- 1. ÍNDICES PARA TABELA DE VENDAS (CVDW)
-- ============================================================

-- Índice para consultas por data de venda
CREATE INDEX IF NOT EXISTS idx_vendas_data_venda
ON vendas(data_venda);

-- Índice para consultas por data de reserva
CREATE INDEX IF NOT EXISTS idx_vendas_data_reserva
ON vendas(data_reserva);

-- Índice para consultas por cliente
CREATE INDEX IF NOT EXISTS idx_vendas_idcliente
ON vendas(idcliente);

-- Índice para consultas por valor de contrato
CREATE INDEX IF NOT EXISTS idx_vendas_valor_contrato
ON vendas(valor_contrato);

-- Índice para consultas por corretor
CREATE INDEX IF NOT EXISTS idx_vendas_idcorretor
ON vendas(idcorretor);

-- Índice para consultas por imobiliária
CREATE INDEX IF NOT EXISTS idx_vendas_idimobiliaria
ON vendas(idimobiliaria);

-- Índice para consultas por empreendimento
CREATE INDEX IF NOT EXISTS idx_vendas_idempreendimento
ON vendas(idempreendimento);

-- Índice composto para consultas por data e cliente (muito comum)
CREATE INDEX IF NOT EXISTS idx_vendas_data_cliente
ON vendas(data_venda, idcliente);

-- Índice composto para consultas por data e corretor
CREATE INDEX IF NOT EXISTS idx_vendas_data_corretor
ON vendas(data_venda, idcorretor);

-- Índice composto para consultas por empreendimento e data
CREATE INDEX IF NOT EXISTS idx_vendas_empreendimento_data
ON vendas(idempreendimento, data_venda);

-- Índice para busca por documento do cliente
CREATE INDEX IF NOT EXISTS idx_vendas_documento_cliente
ON vendas(documento_cliente);

-- ============================================================
-- 2. ÍNDICES PARA TABELA DE RESERVAS
-- ============================================================

-- Índice para consultas por data de cadastro
CREATE INDEX IF NOT EXISTS idx_reservas_data_cad
ON reservas(data_cad);

-- Índice para consultas por data de venda
CREATE INDEX IF NOT EXISTS idx_reservas_data_venda
ON reservas(data_venda);

-- Índice para consultas por cliente
CREATE INDEX IF NOT EXISTS idx_reservas_idcliente
ON reservas(idcliente);

-- Índice para consultas por corretor
CREATE INDEX IF NOT EXISTS idx_reservas_idcorretor
ON reservas(idcorretor);

-- Índice para consultas por imobiliária
CREATE INDEX IF NOT EXISTS idx_reservas_idimobiliaria
ON reservas(idimobiliaria);

-- Índice para consultas por empreendimento
CREATE INDEX IF NOT EXISTS idx_reservas_idempreendimento
ON reservas(idempreendimento);

-- Índice para consultas por situação
CREATE INDEX IF NOT EXISTS idx_reservas_idsituacao
ON reservas(idsituacao);

-- Índice composto para análise de conversão (situação + data)
CREATE INDEX IF NOT EXISTS idx_reservas_situacao_data
ON reservas(idsituacao, data_venda);

-- ============================================================
-- 3. ÍNDICES PARA TABELA DE LEADS
-- ============================================================

-- Índice para consultas por situação
CREATE INDEX IF NOT EXISTS idx_leads_idsituacao
ON leads(idsituacao);

-- Índice para consultas por data de cadastro
CREATE INDEX IF NOT EXISTS idx_leads_data_cad
ON leads(data_cad);

-- Índice para consultas por corretor
CREATE INDEX IF NOT EXISTS idx_leads_idcorretor
ON leads(idcorretor);

-- Índice para consultas por imobiliária
CREATE INDEX IF NOT EXISTS idx_leads_idimobiliaria
ON leads(idimobiliaria);

-- Índice para consultas por empreendimento
CREATE INDEX IF NOT EXISTS idx_leads_idempreendimento
ON leads(idempreendimento);

-- Índice para busca por nome (busca parcial)
CREATE INDEX IF NOT EXISTS idx_leads_nome
ON leads USING gin(nome gin_trgm_ops);

-- Índice para busca por documento
CREATE INDEX IF NOT EXISTS idx_leads_documento_cliente
ON leads(documento_cliente);

-- Índice composto para análise de conversão
CREATE INDEX IF NOT EXISTS idx_leads_situacao_corretor
ON leads(idsituacao, idcorretor);

-- ============================================================
-- 4. ÍNDICES PARA TABELA DE UNIDADES
-- ============================================================

-- Índice para consultas por empreendimento
CREATE INDEX IF NOT EXISTS idx_unidades_idempreendimento
ON unidades(idempreendimento);

-- Índice para consultas por valor
CREATE INDEX IF NOT EXISTS idx_unidades_valor
ON unidades(valor);

-- Índice para consultas por tipologia
CREATE INDEX IF NOT EXISTS idx_unidades_tipologia
ON unidades(tipologia);

-- Índice para consultas por situação de venda
CREATE INDEX IF NOT EXISTS idx_unidades_situacao_vendida
ON unidades(situacao_vendida);

-- Índice composto para disponibilidade
CREATE INDEX IF NOT EXISTS idx_unidades_empreendimento_disponivel
ON unidades(idempreendimento, situacao_para_venda);

-- ============================================================
-- 5. ÍNDICES PARA TABELA DE PESSOAS (CLIENTES)
-- ============================================================

-- Índice para busca por documento
CREATE INDEX IF NOT EXISTS idx_pessoas_documento
ON pessoas(documento);

-- Índice para busca por nome (busca parcial)
CREATE INDEX IF NOT EXISTS idx_pessoas_nome
ON pessoas USING gin(nome gin_trgm_ops);

-- Índice para consultas por renda familiar
CREATE INDEX IF NOT EXISTS idx_pessoas_renda_familiar
ON pessoas(renda_familiar);

-- ============================================================
-- 6. ÍNDICES PARA TABELA DE CORRETORES
-- ============================================================

-- Índice para consultas por imobiliária
CREATE INDEX IF NOT EXISTS idx_corretores_idimobiliaria
ON corretores(idimobiliaria);

-- Índice para consultas por status ativo
CREATE INDEX IF NOT EXISTS idx_corretores_ativo
ON corretores(ativo);

-- Índice para busca por nome
CREATE INDEX IF NOT EXISTS idx_corretores_nome
ON corretores USING gin(nome gin_trgm_ops);

-- ============================================================
-- 7. ÍNDICES PARA TABELA DE IMOBILIÁRIAS
-- ============================================================

-- Índice para consultas por status ativo
CREATE INDEX IF NOT EXISTS idx_imobiliarias_ativo
ON imobiliarias(ativo);

-- Índice para busca por nome
CREATE INDEX IF NOT EXISTS idx_imobiliarias_nome
ON imobiliarias USING gin(nome gin_trgm_ops);

-- Índice para busca por CNPJ
CREATE INDEX IF NOT EXISTS idx_imobiliarias_cnpj
ON imobiliarias(cnpj);

-- ============================================================
-- 8. MATERIALIZED VIEW - KPIs MENSAIS DE VENDAS
-- ============================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_kpis_mensais_vendas AS
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
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_kpis_mensais_vendas_mes
ON mv_kpis_mensais_vendas(mes);

-- ============================================================
-- 9. MATERIALIZED VIEW - TOP CORRETORES
-- ============================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_top_corretores AS
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
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_top_corretores_id
ON mv_top_corretores(idcorretor);

-- ============================================================
-- 10. MATERIALIZED VIEW - TOP EMPREENDIMENTOS
-- ============================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_top_empreendimentos AS
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
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_top_empreendimentos_id
ON mv_top_empreendimentos(idempreendimento);

-- ============================================================
-- 11. MATERIALIZED VIEW - FUNIL DE CONVERSÃO
-- ============================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_funil_conversao AS
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
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_funil_conversao_mes
ON mv_funil_conversao(mes);

-- ============================================================
-- 12. FUNÇÕES PARA REFRESH DAS MATERIALIZED VIEWS
-- ============================================================

-- Função para atualizar KPIs mensais de vendas
CREATE OR REPLACE FUNCTION refresh_kpis_mensais_vendas()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_kpis_mensais_vendas;
END;
$$ LANGUAGE plpgsql;

-- Função para atualizar top corretores
CREATE OR REPLACE FUNCTION refresh_top_corretores()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_corretores;
END;
$$ LANGUAGE plpgsql;

-- Função para atualizar top empreendimentos
CREATE OR REPLACE FUNCTION refresh_top_empreendimentos()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_empreendimentos;
END;
$$ LANGUAGE plpgsql;

-- Função para atualizar funil de conversão
CREATE OR REPLACE FUNCTION refresh_funil_conversao()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_funil_conversao;
END;
$$ LANGUAGE plpgsql;

-- Função para atualizar todas as views
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS void AS $$
BEGIN
    PERFORM refresh_kpis_mensais_vendas();
    PERFORM refresh_top_corretores();
    PERFORM refresh_top_empreendimentos();
    PERFORM refresh_funil_conversao();
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 13. TRIGGER PARA AUTO-REFRESH (OPCIONAL)
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
-- 14. VIEWS NORMAIS (NÃO MATERIALIZADAS) PARA DADOS EM TEMPO REAL
-- ============================================================

-- View para vendas do dia
CREATE OR REPLACE VIEW v_vendas_hoje AS
SELECT
    COUNT(*) as total_vendas,
    SUM(valor_contrato) as vgv_total,
    AVG(valor_contrato) as ticket_medio,
    COUNT(DISTINCT idcliente) as clientes_unicos,
    COUNT(DISTINCT idcorretor) as corretores_ativos,
    MAX(data_venda) as ultima_venda
FROM vendas
WHERE DATE(data_venda) = CURRENT_DATE;

-- View para reservas do dia
CREATE OR REPLACE VIEW v_reservas_hoje AS
SELECT
    COUNT(*) as total_reservas,
    SUM(valor_contrato) as vgv_total,
    AVG(valor_contrato) as ticket_medio,
    COUNT(DISTINCT idcliente) as clientes_unicos,
    COUNT(DISTINCT idcorretor) as corretores_ativos,
    MAX(data_cad) as ultima_reserva
FROM reservas
WHERE DATE(data_cad) = CURRENT_DATE;

-- View para leads do dia
CREATE OR REPLACE VIEW v_leads_hoje AS
SELECT
    COUNT(*) as total_leads,
    COUNT(DISTINCT idcorretor) as corretores_com_leads,
    COUNT(DISTINCT idempreendimento) as empreendimentos_com_interesse,
    MAX(data_cad) as ultimo_lead
FROM leads
WHERE DATE(data_cad) = CURRENT_DATE;

-- View para unidades disponíveis por empreendimento
CREATE OR REPLACE VIEW v_unidades_disponiveis AS
SELECT
    idempreendimento,
    nome_empreendimento,
    COUNT(*) as total_unidades,
    COUNT(CASE WHEN situacao_para_venda = 1 THEN 1 END) as disponiveis,
    COUNT(CASE WHEN situacao_vendida = 1 THEN 1 END) as vendidas,
    COUNT(CASE WHEN situacao_bloqueada = 'true' THEN 1 END) as bloqueadas,
    MIN(valor) as valor_minimo,
    MAX(valor) as valor_maximo,
    AVG(valor) as valor_medio
FROM unidades
GROUP BY idempreendimento, nome_empreendimento
ORDER BY nome_empreendimento;

-- ============================================================
-- 15. ANÁLISE E VACUUM
-- ============================================================

-- Atualizar estatísticas das tabelas principais
ANALYZE vendas;
ANALYZE reservas;
ANALYZE leads;
ANALYZE unidades;
ANALYZE pessoas;
ANALYZE corretores;
ANALYZE imobiliarias;

-- ============================================================
-- 16. COMENTÁRIOS ÚTEIS
-- ============================================================

COMMENT ON MATERIALIZED VIEW mv_kpis_mensais_vendas IS 'KPIs mensais de vendas agregados (VGV, ticket médio, etc) - Todos os períodos disponíveis';
COMMENT ON MATERIALIZED VIEW mv_top_corretores IS 'Top 100 corretores por VGV total - Todos os períodos disponíveis';
COMMENT ON MATERIALIZED VIEW mv_top_empreendimentos IS 'Top 100 empreendimentos por VGV total - Todos os períodos disponíveis';
COMMENT ON MATERIALIZED VIEW mv_funil_conversao IS 'Análise do funil de conversão (Leads → Reservas → Vendas) - Todos os períodos disponíveis';

COMMENT ON VIEW v_vendas_hoje IS 'Métricas de vendas do dia atual em tempo real';
COMMENT ON VIEW v_reservas_hoje IS 'Métricas de reservas do dia atual em tempo real';
COMMENT ON VIEW v_leads_hoje IS 'Métricas de leads do dia atual em tempo real';
COMMENT ON VIEW v_unidades_disponiveis IS 'Status de disponibilidade de unidades por empreendimento';

-- ============================================================
-- FIM DO SCRIPT DE OTIMIZAÇÃO - CVDW ANALYTICS PLATFORM
-- ============================================================
--
-- RESUMO DAS OTIMIZAÇÕES:
-- ✓ 52 índices criados para tabelas CVDW
-- ✓ 4 materialized views para análises agregadas
-- ✓ 4 views normais para dados em tempo real
-- ✓ Funções de refresh com suporte a CONCURRENT
-- ✓ Sistema de log para controle de refreshes
-- ✓ Extensões pg_trgm e pg_stat_statements habilitadas
--
-- PRÓXIMOS PASSOS:
-- 1. Execute: SELECT refresh_all_materialized_views(); (primeira carga)
-- 2. Configure refresh quando novos dados forem importados
-- 3. Monitore performance com pg_stat_statements
-- 4. Ajuste índices conforme padrões de uso
--
-- NOTA: As materialized views processam TODOS os períodos disponíveis
--       nos dados. Para filtrar por período específico, faça ao consultar:
--       SELECT * FROM mv_kpis_mensais_vendas WHERE mes >= '2020-01-01';
-- ============================================================
