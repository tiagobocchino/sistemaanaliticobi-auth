-- =====================================================
-- VERIFICAR USUÁRIOS CADASTRADOS
-- =====================================================

-- Ver todos os usuários cadastrados
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

-- Ver especificamente os usuários solicitados
SELECT
    'USUÁRIOS SOLICITADOS:' as status,
    u.id,
    u.email,
    u.nome,
    COALESCE(c.nome, 'Sem cargo') as cargo,
    COALESCE(c.nivel_acesso, 0) as nivel_acesso,
    COALESCE(d.nome, 'Sem divisão') as divisao,
    COALESCE(d.codigo, 'N/A') as divisao_codigo
FROM public.usuarios u
LEFT JOIN public.cargos c ON u.cargo_id = c.id
LEFT JOIN public.divisoes d ON u.divisao_id = d.id
WHERE u.email IN ('tiago.bocchino@4pcapital.com.br', 'tiago.bocchino@gmail.com');
