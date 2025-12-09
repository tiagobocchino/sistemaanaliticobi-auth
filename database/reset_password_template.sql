-- =====================================================
-- TEMPLATE PARA RESETAR SENHA
-- =====================================================
-- Use este template para resetar senha de qualquer usuário
-- =====================================================

-- Substitua os valores abaixo:
-- EMAIL_DO_USUARIO: o email do usuário
-- NOVA_SENHA_AQUI: a nova senha desejada

/*
EXEMPLO DE USO:

SELECT auth.admin.update_user_by_id(
    (SELECT id FROM auth.users WHERE email = 'EMAIL_DO_USUARIO'),
    '{"password": "NOVA_SENHA_AQUI"}'::jsonb
);

EXEMPLOS PRÁTICOS:

-- Para tiago.bocchino@4pcapital.com.br
SELECT auth.admin.update_user_by_id(
    (SELECT id FROM auth.users WHERE email = 'tiago.bocchino@4pcapital.com.br'),
    '{"password": "MinhaNovaSenha123!"}'::jsonb
);

-- Para tiago.bocchino@gmail.com
SELECT auth.admin.update_user_by_id(
    (SELECT id FROM auth.users WHERE email = 'tiago.bocchino@gmail.com'),
    '{"password": "SenhaSegura456@"}'::jsonb
);

-- Para qualquer outro usuário
SELECT auth.admin.update_user_by_id(
    (SELECT id FROM auth.users WHERE email = 'outro@email.com'),
    '{"password": "QualquerSenha789#"}'::jsonb
);
*/

-- =====================================================
-- VERIFICAÇÃO APÓS RESET
-- =====================================================

-- Execute após resetar a senha para verificar
SELECT
    email,
    updated_at,
    '✅ Senha resetada - use a nova senha para login' as status
FROM auth.users
WHERE email = 'EMAIL_DO_USUARIO';
