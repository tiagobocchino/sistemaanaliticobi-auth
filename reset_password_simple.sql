-- RESET SIMPLES DE SENHA PARA OS USUÁRIOS SOLICITADOS

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

-- Verificar se funcionou
SELECT
    email,
    '✅ SENHA RESETADA PARA: Admin123!@#' as status
FROM auth.users
WHERE email IN ('tiago.bocchino@4pcapital.com.br', 'tiago.bocchino@gmail.com');
