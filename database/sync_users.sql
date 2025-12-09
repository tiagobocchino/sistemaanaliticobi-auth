-- =====================================================
-- SINCRONIZAR USUÁRIOS DO SUPABASE AUTH
-- =====================================================
-- Sincronizar usuários existentes do auth.users para usuarios
-- =====================================================

-- =====================================================
-- 1. VERIFICAR TRIGGER EXISTENTE
-- =====================================================

-- Verificar se o trigger existe
SELECT
    'TRIGGER STATUS:' as status,
    COUNT(*) as triggers_encontrados,
    CASE
        WHEN COUNT(*) > 0 THEN '✅ Trigger ativo'
        ELSE '❌ Trigger não encontrado - será criado'
    END as status_trigger
FROM pg_trigger
WHERE tgname = 'on_auth_user_created';

-- =====================================================
-- 2. CRIAR/RECriar TRIGGER SE NECESSÁRIO
-- =====================================================

-- Remover trigger existente se houver
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Recriar função do trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Inserir novo registro na tabela usuarios
  INSERT INTO public.usuarios (
    id,
    email,
    nome,
    cargo_id,
    divisao_id,
    ativo,
    created_at,
    updated_at
  )
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
    NULLIF((NEW.raw_user_meta_data->>'cargo_id'), '')::uuid,
    NULLIF((NEW.raw_user_meta_data->>'divisao_id'), '')::uuid,
    true,
    NOW(),
    NOW()
  )
  ON CONFLICT (id) DO NOTHING; -- Evitar duplicatas

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Criar trigger
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- =====================================================
-- 3. SINCRONIZAR USUÁRIOS EXISTENTES MANUALMENTE
-- =====================================================

-- Inserir usuários que existem no auth.users mas não na usuarios
INSERT INTO public.usuarios (
    id,
    email,
    nome,
    cargo_id,
    divisao_id,
    ativo,
    created_at,
    updated_at
)
SELECT
    au.id,
    au.email,
    COALESCE(au.raw_user_meta_data->>'full_name', au.email) as nome,
    NULLIF((au.raw_user_meta_data->>'cargo_id'), '')::uuid as cargo_id,
    NULLIF((au.raw_user_meta_data->>'divisao_id'), '')::uuid as divisao_id,
    true as ativo,
    COALESCE(au.created_at, NOW()) as created_at,
    NOW() as updated_at
FROM auth.users au
LEFT JOIN public.usuarios u ON au.id = u.id
WHERE u.id IS NULL  -- Só usuários que não existem na tabela usuarios
  AND au.email IS NOT NULL; -- Só usuários com email válido

-- =====================================================
-- 4. VERIFICAR SINCRONIZAÇÃO
-- =====================================================

-- Verificar quantos usuários foram sincronizados
SELECT
    'SINCRONIZAÇÃO CONCLUÍDA:' as status,
    COUNT(*) as usuarios_sincronizados
FROM public.usuarios;

-- Verificar usuários específicos solicitados
SELECT
    'USUÁRIOS SOLICITADOS:' as status,
    u.id,
    u.email,
    u.nome,
    COALESCE(c.nome, 'Sem cargo') as cargo,
    COALESCE(c.nivel_acesso, 0) as nivel_acesso,
    COALESCE(d.nome, 'Sem divisão') as divisao,
    u.created_at
FROM public.usuarios u
LEFT JOIN public.cargos c ON u.cargo_id = c.id
LEFT JOIN public.divisoes d ON u.divisao_id = d.id
WHERE u.email IN ('tiago.bocchino@4pcapital.com.br', 'tiago.bocchino@gmail.com');

-- Verificar se há usuários no auth.users sem perfil em usuarios
SELECT
    'USUÁRIOS SEM PERFIL:' as status,
    COUNT(*) as usuarios_sem_perfil
FROM auth.users au
LEFT JOIN public.usuarios u ON au.id = u.id
WHERE u.id IS NULL;

-- =====================================================
-- 5. LOG DE SINCRONIZAÇÃO
-- =====================================================

-- Mostrar todos os usuários sincronizados
SELECT
    u.id,
    u.email,
    u.nome,
    COALESCE(c.nome, 'Sem cargo') as cargo,
    COALESCE(d.nome, 'Sem divisão') as divisao,
    u.created_at,
    '✅ Sincronizado' as status
FROM public.usuarios u
LEFT JOIN public.cargos c ON u.cargo_id = c.id
LEFT JOIN public.divisoes d ON u.divisao_id = d.id
ORDER BY u.created_at DESC;

-- =====================================================
-- INSTRUÇÕES:
-- =====================================================
/*
1. Execute este script no SQL Editor do Supabase
2. O script irá:
   - Verificar se o trigger existe
   - Criar/Recriar o trigger se necessário
   - Sincronizar usuários existentes do auth.users
   - Mostrar relatório da sincronização

3. Após execução, os usuários poderão fazer login normalmente
4. Os perfis serão criados automaticamente na tabela usuarios

IMPORTANTE:
- Usuários existentes serão sincronizados automaticamente
- Novos usuários serão criados automaticamente pelo trigger
- Execute apenas uma vez para evitar duplicatas
*/

-- =====================================================
-- FIM DA SINCRONIZAÇÃO
-- =====================================================
