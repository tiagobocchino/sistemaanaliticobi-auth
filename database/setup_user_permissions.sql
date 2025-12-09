-- =====================================================
-- CONFIGURAR PERMISSÕES DOS USUÁRIOS
-- =====================================================
-- Atribuir cargos e divisões aos usuários específicos
-- =====================================================

-- =====================================================
-- 1. VERIFICAR USUÁRIOS SINCRONIZADOS
-- =====================================================

-- Executar sincronização primeiro se necessário
-- (Importante: execute database/sync_users.sql antes se os usuários não aparecerem)

-- Ver usuários cadastrados
SELECT
    u.id,
    u.email,
    u.nome,
    COALESCE(c.nome, 'Sem cargo') as cargo,
    COALESCE(c.nivel_acesso, 0) as nivel_acesso,
    COALESCE(d.nome, 'Sem divisão') as divisao,
    COALESCE(d.codigo, 'N/A') as divisao_codigo,
    u.created_at
FROM public.usuarios u
LEFT JOIN public.cargos c ON u.cargo_id = c.id
LEFT JOIN public.divisoes d ON u.divisao_id = d.id
ORDER BY u.created_at DESC;

-- =====================================================
-- 2. ATRIBUIR PERMISSÕES ADMINISTRADOR
-- =====================================================

-- Atribuir cargo Administrador (nivel_acesso = 5) aos usuários específicos
UPDATE public.usuarios
SET
    cargo_id = (SELECT id FROM public.cargos WHERE nome = 'Administrador' LIMIT 1),
    divisao_id = (SELECT id FROM public.divisoes WHERE codigo = 'COM' LIMIT 1), -- Divisão Comercial
    updated_at = NOW()
WHERE email IN ('tiago.bocchino@4pcapital.com.br', 'tiago.bocchino@gmail.com');

-- =====================================================
-- 3. VERIFICAR PERMISSÕES ATRIBUÍDAS
-- =====================================================

-- Verificar permissões dos usuários atualizados
SELECT
    'PERMISSÕES ATRIBUÍDAS:' as status,
    u.id,
    u.email,
    u.nome,
    c.nome as cargo,
    c.nivel_acesso,
    d.nome as divisao,
    d.codigo as divisao_codigo,
    u.updated_at
FROM public.usuarios u
LEFT JOIN public.cargos c ON u.cargo_id = c.id
LEFT JOIN public.divisoes d ON u.divisao_id = d.id
WHERE u.email IN ('tiago.bocchino@4pcapital.com.br', 'tiago.bocchino@gmail.com');

-- =====================================================
-- 4. VERIFICAR DASHBOARDS DISPONÍVEIS
-- =====================================================

-- Verificar dashboards que os usuários agora podem acessar
SELECT
    'DASHBOARDS DISPONÍVEIS PARA ADMINS:' as status,
    a.nome as dashboard_nome,
    a.descricao,
    d.nome as divisao_permitida,
    d.codigo as divisao_codigo
FROM public.analyses a
LEFT JOIN public.divisoes d ON a.divisao_restrita_id = d.id
WHERE a.tipo = 'powerbi'
ORDER BY a.nome;

-- =====================================================
-- 5. INSTRUÇÕES PARA LOGIN
-- =====================================================

/*
INSTRUÇÕES PARA OS USUÁRIOS:

1. Os usuários devem fazer login com seus emails:
   - tiago.bocchino@4pcapital.com.br
   - tiago.bocchino@gmail.com

2. As senhas foram definidas no momento do cadastro/signup
   - As senhas ficam criptografadas no Supabase Auth
   - Não é possível recuperar senhas originais
   - Se esqueceram a senha, usar "Esqueci minha senha"

3. Com as permissões de Administrador (nivel_acesso = 5), eles podem:
   - Acessar todos os dashboards Power BI
   - Gerenciar outros usuários
   - Criar/editar/deletar análises
   - Ver todas as informações do sistema

4. Dashboards que podem acessar:
   - Dashboard Compras (Financeiro)
   - Dashboard SDRs (Comercial)
   - Dashboard Pastas (Comercial)

5. URLs de acesso:
   - Sistema: http://localhost:5173
   - Dashboards: http://localhost:5173/analyses
   - Gestão de usuários: http://localhost:5173/users
*/

-- =====================================================
-- FIM DA CONFIGURAÇÃO
-- =====================================================
