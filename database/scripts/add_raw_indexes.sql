-- ============================================================================
-- Script: Adicionar índices GIN para otimizar queries em colunas RAW (JSONB)
-- Data: 2025-12-16
-- Descrição: Cria índices GIN nas colunas 'raw' de 8 tabelas para melhorar
--            performance de consultas JSON via agente IA
-- ============================================================================

-- Índice para tabela leads
CREATE INDEX IF NOT EXISTS idx_leads_raw
ON leads USING GIN (raw);

-- Índice para tabela vendas
CREATE INDEX IF NOT EXISTS idx_vendas_raw
ON vendas USING GIN (raw);

-- Índice para tabela reservas
CREATE INDEX IF NOT EXISTS idx_reservas_raw
ON reservas USING GIN (raw);

-- Índice para tabela unidades
CREATE INDEX IF NOT EXISTS idx_unidades_raw
ON unidades USING GIN (raw);

-- Índice para tabela corretores
CREATE INDEX IF NOT EXISTS idx_corretores_raw
ON corretores USING GIN (raw);

-- Índice para tabela pessoas
CREATE INDEX IF NOT EXISTS idx_pessoas_raw
ON pessoas USING GIN (raw);

-- Índice para tabela imobiliarias
CREATE INDEX IF NOT EXISTS idx_imobiliarias_raw
ON imobiliarias USING GIN (raw);

-- Índice para tabela repasses
CREATE INDEX IF NOT EXISTS idx_repasses_raw
ON repasses USING GIN (raw);

-- ============================================================================
-- Verificar índices criados:
-- SELECT tablename, indexname, indexdef
-- FROM pg_indexes
-- WHERE indexname LIKE 'idx_%_raw';
-- ============================================================================
