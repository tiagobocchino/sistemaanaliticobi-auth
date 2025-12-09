-- ===============================================
-- LIMPEZA COMPLETA DE POLÍTICAS RLS
-- ===============================================
-- Execute este script PRIMEIRO se estiver tendo problemas
-- com políticas conflitantes ou erros de RLS
-- ===============================================

-- Remover TODAS as políticas existentes das tabelas
DO $$
DECLARE
    policy_record RECORD;
BEGIN
    -- Limpar políticas de todas as tabelas
    FOR policy_record IN
        SELECT schemaname, tablename, policyname
        FROM pg_policies
        WHERE schemaname = 'public'
        AND tablename IN ('usuarios', 'analyses', 'cargos', 'divisoes')
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON %I.%I',
                      policy_record.policyname,
                      policy_record.schemaname,
                      policy_record.tablename);
        RAISE NOTICE 'Removida política: %.%', policy_record.tablename, policy_record.policyname;
    END LOOP;

    RAISE NOTICE '✅ Todas as políticas RLS foram removidas com sucesso!';
END $$;

-- Verificar se limpeza foi bem-sucedida
SELECT
    schemaname,
    tablename,
    policyname,
    'POLÍTICA ENCONTRADA - Execute limpeza novamente' as status
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('usuarios', 'analyses', 'cargos', 'divisoes')
ORDER BY tablename, policyname;
