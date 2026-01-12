-- ============================================================
-- VERIFICAÇÃO DE TABELAS EXISTENTES NO SUPABASE
-- ============================================================

-- Listar todas as tabelas no schema public
SELECT
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Verificar colunas das tabelas principais
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name IN ('vendas', 'clientes', 'produtos', 'estoque', 'produtos_venda',
                   'reservas', 'unidades', 'leads', 'corretores', 'imobiliarias')
ORDER BY table_name, ordinal_position;

-- Verificar se existe coluna cliente_id na tabela vendas
SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'vendas'
ORDER BY ordinal_position;

-- Verificar índices existentes
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Verificar materialized views existentes
SELECT
    schemaname,
    matviewname,
    definition
FROM pg_matviews
WHERE schemaname = 'public';
