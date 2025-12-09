-- =====================================================
-- RESETAR SENHA DE USUÁRIO
-- =====================================================
-- Resetar senha de usuários específicos usando função admin
-- =====================================================

-- =====================================================
-- 1. VERIFICAR USUÁRIOS EXISTENTES
-- =====================================================

-- Ver usuários antes do reset
SELECT
    'USUÁRIOS ANTES DO RESET:' as status,
    id,
    email,
    created_at,
    last_sign_in_at
FROM auth.users
WHERE email IN ('tiago.bocchino@4pcapital.com.br', 'tiago.bocchino@gmail.com');

-- =====================================================
-- 2. RESETAR SENHAS
-- =====================================================

-- IMPORTANTE: Substitua 'NovaSenha123!' pela senha desejada
-- Esta senha será usada para login após o reset

-- Resetar senha para tiago.bocchino@4pcapital.com.br
SELECT auth.admin.update_user_by_id(
    (SELECT id FROM auth.users WHERE email = 'tiago.bocchino@4pcapital.com.br'),
    '{"password": "Admin123!@#"}'::jsonb
);

-- Resetar senha para tiago.bocchino@gmail.com
SELECT auth.admin.update_user_by_id(
    (SELECT id FROM auth.users WHERE email = 'tiago.bocchino@gmail.com'),
    '{"password": "Admin123!@#"}'::jsonb
);

-- =====================================================
-- 3. VERIFICAR RESET
-- =====================================================

-- Ver usuários após o reset
SELECT
    'USUÁRIOS APÓS RESET:' as status,
    id,
    email,
    updated_at,
    '✅ Senha resetada para: Admin123!@#' as nova_senha
FROM auth.users
WHERE email IN ('tiago.bocchino@4pcapital.com.br', 'tiago.bocchino@gmail.com');

-- =====================================================
-- 4. INSTRUÇÕES DE LOGIN
-- =====================================================

/*
SUA NOVA SENHA: Admin123!@#

Para fazer login:

1. Acesse: http://localhost:5173/login
2. Use um dos emails:
   - tiago.bocchino@4pcapital.com.br
   - tiago.bocchino@gmail.com
3. Senha: Admin123!@#

IMPORTANTE:
- Anote esta senha em local seguro
- Mude a senha após o primeiro login se desejar
- Esta senha dá acesso total ao sistema como administrador

TESTE APÓS EXECUTAR:
1. Execute este script no SQL Editor do Supabase
2. Vá para http://localhost:5173/login
3. Faça login com email + senha "Admin123!@#"
4. Acesse http://localhost:5173/analyses para ver os dashboards
*/

-- =====================================================
-- 5. VERIFICAÇÃO DE PERMISSÕES
-- =====================================================

-- Verificar se os usuários têm permissões de admin
SELECT
    'PERMISSÕES DOS USUÁRIOS:' as status,
    u.email,
    COALESCE(c.nome, 'Sem cargo') as cargo,
    COALESCE(c.nivel_acesso, 0) as nivel_acesso,
    COALESCE(d.nome, 'Sem divisão') as divisao
FROM public.usuarios u
LEFT JOIN public.cargos c ON u.cargo_id = c.id
LEFT JOIN public.divisoes d ON u.divisao_id = d.id
WHERE u.email IN ('tiago.bocchino@4pcapital.com.br', 'tiago.bocchino@gmail.com');

-- =====================================================
-- FIM DO RESET DE SENHA
-- =====================================================
