-- ============================================================
-- PASSO 1: DROPAR VIEWS ANTIGAS
-- Execute ESTE script primeiro
-- ============================================================

DROP MATERIALIZED VIEW IF EXISTS mv_kpis_mensais_vendas CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_top_corretores CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_top_empreendimentos CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_funil_conversao CASCADE;
