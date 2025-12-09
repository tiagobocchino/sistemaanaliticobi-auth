-- =====================================================
-- VERIFICAR USUÁRIOS NO SUPABASE AUTH
-- =====================================================
-- Verificar usuários cadastrados no auth.users
-- (Senhas ficam criptografadas e não podem ser visualizadas)
-- =====================================================

-- =====================================================
-- 1. VERIFICAR USUÁRIOS NO AUTH.USERS
-- =====================================================

-- Ver todos os usuários no auth.users
SELECT
    'USUÁRIOS NO AUTH:' as status,
    id,
    email,
    email_confirmed_at,
    created_at,
    last_sign_in_at,
    raw_user_meta_data
FROM auth.users
ORDER BY created_at DESC;

-- =====================================================
-- 2. VERIFICAR USUÁRIOS SOLICITADOS
-- =====================================================

-- Ver especificamente os usuários solicitados
SELECT
    'USUÁRIOS SOLICITADOS NO AUTH:' as status,
    id,
    email,
    CASE
        WHEN email_confirmed_at IS NOT NULL THEN '✅ Email confirmado'
        ELSE '❌ Email não confirmado'
    END as status_email,
    created_at,
    last_sign_in_at,
    raw_user_meta_data->>'full_name' as nome_cadastrado
FROM auth.users
WHERE email IN ('tiago.bocchino@4pcapital.com.br', 'tiago.bocchino@gmail.com');

-- =====================================================
-- 3. VERIFICAR PERFIS NA TABELA USUARIOS
-- =====================================================

-- Ver perfis sincronizados
SELECT
    'PERFIS SINCRONIZADOS:' as status,
    u.id,
    u.email,
    u.nome,
    COALESCE(c.nome, 'Sem cargo') as cargo,
    COALESCE(c.nivel_acesso, 0) as nivel_acesso,
    COALESCE(d.nome, 'Sem divisão') as divisao
FROM public.usuarios u
LEFT JOIN public.cargos c ON u.cargo_id = c.id
LEFT JOIN public.divisoes d ON u.divisao_id = d.id
WHERE u.email IN ('tiago.bocchino@4pcapital.com.br', 'tiago.bocchino@gmail.com');

-- =====================================================
-- 4. INSTRUÇÕES SOBRE SENHAS
-- =====================================================

/*
IMPORTANTE SOBRE SENHAS:
========================

❌ AS SENHAS NÃO PODEM SER VISUALIZADAS
- As senhas ficam criptografadas no Supabase Auth
- Por segurança, não há como recuperar senhas originais
- Esta é uma prática de segurança padrão

✅ COMO VERIFICAR ACESSO:
1. Tentar fazer login com o email
2. Se não lembrar a senha, usar "Esqueci minha senha"
3. Resetar senha via email

✅ SENHAS PADRÃO SUGERIDAS:
- Se os usuários foram criados recentemente, podem ter usado:
  - "123456" ou "password"
  - "Master123#" (se foi criado pelo create_admin.py)
  - Ou qualquer senha definida no momento do cadastro

✅ PARA TESTAR:
1. Acesse: http://localhost:5173/login
2. Use um dos emails listados acima
3. Tente diferentes senhas ou use "Esqueci minha senha"

✅ SE PRECISAR RESETAR:
- Vá para http://localhost:5173/login
- Clique em "Esqueci minha senha"
- Digite o email
- Verifique o email para link de reset
*/

-- =====================================================
-- 5. VERIFICAÇÃO DE DASHBOARDS DISPONÍVEIS
-- =====================================================

-- Verificar dashboards que os usuários podem acessar
SELECT
    'DASHBOARDS DISPONÍVEIS PARA ADMINS:' as status,
    a.nome as dashboard,
    a.descricao,
    COALESCE(d.nome, 'Qualquer divisão') as divisao_requerida
FROM public.analyses a
LEFT JOIN public.divisoes d ON a.divisao_restrita_id = d.id
WHERE a.tipo = 'powerbi'
ORDER BY a.nome;

-- =====================================================
-- FIM DA VERIFICAÇÃO
-- =====================================================
