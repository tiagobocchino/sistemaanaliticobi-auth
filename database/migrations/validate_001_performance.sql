-- ============================================================
-- SCRIPT DE VALIDAÇÃO - 001_performance_optimization.sql
-- ============================================================
-- Este script valida se as tabelas necessárias existem antes
-- de rodar o script de otimização principal
-- ============================================================

-- Verificar se as tabelas CVDW existem
DO $$
DECLARE
    tabelas_necessarias TEXT[] := ARRAY[
        'vendas',
        'reservas',
        'leads',
        'unidades',
        'pessoas',
        'corretores',
        'imobiliarias'
    ];
    tabela TEXT;
    tabela_existe BOOLEAN;
    todas_existem BOOLEAN := TRUE;
BEGIN
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'VALIDAÇÃO DE TABELAS NECESSÁRIAS';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '';

    FOREACH tabela IN ARRAY tabelas_necessarias
    LOOP
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = tabela
        ) INTO tabela_existe;

        IF tabela_existe THEN
            RAISE NOTICE '✓ Tabela "%" encontrada', tabela;
        ELSE
            RAISE WARNING '✗ Tabela "%" NÃO encontrada', tabela;
            todas_existem := FALSE;
        END IF;
    END LOOP;

    RAISE NOTICE '';
    RAISE NOTICE '============================================================';

    IF todas_existem THEN
        RAISE NOTICE '✓ SUCESSO: Todas as tabelas necessárias existem!';
        RAISE NOTICE 'Você pode executar 001_performance_optimization.sql';
    ELSE
        RAISE WARNING '✗ ATENÇÃO: Algumas tabelas estão faltando!';
        RAISE WARNING 'Execute os scripts de criação de tabelas primeiro.';
    END IF;

    RAISE NOTICE '============================================================';
END $$;

-- ============================================================
-- VERIFICAR COLUNAS ESPECÍFICAS DAS TABELAS PRINCIPAIS
-- ============================================================

DO $$
DECLARE
    coluna_existe BOOLEAN;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'VALIDAÇÃO DE COLUNAS DA TABELA VENDAS';
    RAISE NOTICE '============================================================';

    -- Verificar vendas.idcliente (não cliente_id)
    SELECT EXISTS (
        SELECT FROM information_schema.columns
        WHERE table_name = 'vendas'
        AND column_name = 'idcliente'
    ) INTO coluna_existe;

    IF coluna_existe THEN
        RAISE NOTICE '✓ Coluna vendas.idcliente encontrada';
    ELSE
        RAISE WARNING '✗ Coluna vendas.idcliente NÃO encontrada';
    END IF;

    -- Verificar vendas.valor_contrato (não valor_venda)
    SELECT EXISTS (
        SELECT FROM information_schema.columns
        WHERE table_name = 'vendas'
        AND column_name = 'valor_contrato'
    ) INTO coluna_existe;

    IF coluna_existe THEN
        RAISE NOTICE '✓ Coluna vendas.valor_contrato encontrada';
    ELSE
        RAISE WARNING '✗ Coluna vendas.valor_contrato NÃO encontrada';
    END IF;

    -- Verificar vendas.data_venda
    SELECT EXISTS (
        SELECT FROM information_schema.columns
        WHERE table_name = 'vendas'
        AND column_name = 'data_venda'
    ) INTO coluna_existe;

    IF coluna_existe THEN
        RAISE NOTICE '✓ Coluna vendas.data_venda encontrada';
    ELSE
        RAISE WARNING '✗ Coluna vendas.data_venda NÃO encontrada';
    END IF;

    RAISE NOTICE '============================================================';
END $$;

-- ============================================================
-- VERIFICAR EXTENSÕES DISPONÍVEIS
-- ============================================================

DO $$
DECLARE
    pg_trgm_disponivel BOOLEAN;
    pg_stat_disponivel BOOLEAN;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'VALIDAÇÃO DE EXTENSÕES';
    RAISE NOTICE '============================================================';

    -- Verificar se pg_trgm está disponível
    SELECT EXISTS (
        SELECT FROM pg_available_extensions
        WHERE name = 'pg_trgm'
    ) INTO pg_trgm_disponivel;

    IF pg_trgm_disponivel THEN
        RAISE NOTICE '✓ Extensão pg_trgm disponível';
    ELSE
        RAISE WARNING '✗ Extensão pg_trgm NÃO disponível';
    END IF;

    -- Verificar se pg_stat_statements está disponível
    SELECT EXISTS (
        SELECT FROM pg_available_extensions
        WHERE name = 'pg_stat_statements'
    ) INTO pg_stat_disponivel;

    IF pg_stat_disponivel THEN
        RAISE NOTICE '✓ Extensão pg_stat_statements disponível';
    ELSE
        RAISE WARNING '✗ Extensão pg_stat_statements NÃO disponível';
    END IF;

    RAISE NOTICE '============================================================';
END $$;

-- ============================================================
-- CONTAGEM DE REGISTROS
-- ============================================================

DO $$
DECLARE
    count_vendas BIGINT;
    count_reservas BIGINT;
    count_leads BIGINT;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'CONTAGEM DE REGISTROS NAS TABELAS';
    RAISE NOTICE '============================================================';

    -- Contar vendas
    SELECT COUNT(*) INTO count_vendas FROM vendas;
    RAISE NOTICE 'Vendas: % registros', count_vendas;

    -- Contar reservas
    SELECT COUNT(*) INTO count_reservas FROM reservas;
    RAISE NOTICE 'Reservas: % registros', count_reservas;

    -- Contar leads
    SELECT COUNT(*) INTO count_leads FROM leads;
    RAISE NOTICE 'Leads: % registros', count_leads;

    RAISE NOTICE '============================================================';

    IF count_vendas = 0 AND count_reservas = 0 AND count_leads = 0 THEN
        RAISE WARNING 'ATENÇÃO: Todas as tabelas estão vazias!';
        RAISE WARNING 'As materialized views não terão dados para processar.';
    END IF;
END $$;

-- ============================================================
-- FIM DA VALIDAÇÃO
-- ============================================================
