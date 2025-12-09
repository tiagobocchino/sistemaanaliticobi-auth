-- ===============================================
-- SCRIPT: Corrigir Constraints da Tabela usuarios
-- ===============================================
-- Este script corrige APENAS as constraints que estão erradas
-- Baseado na estrutura REAL do banco de dados
-- Execute no SQL Editor do Supabase
-- ===============================================

-- PASSO 1: Ver estrutura atual
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'usuarios'
ORDER BY ordinal_position;

-- ===============================================
-- PASSO 2: Corrigir constraints erradas
-- ===============================================

-- 2.1: Garantir que ID é NOT NULL (é a PK!)
ALTER TABLE public.usuarios
ALTER COLUMN id SET NOT NULL;

-- 2.2: Permitir NULL em cargo_id (opcional - admin atribui depois)
ALTER TABLE public.usuarios
ALTER COLUMN cargo_id DROP NOT NULL;

-- 2.3: Permitir NULL em divisao_id (opcional - admin atribui depois)
ALTER TABLE public.usuarios
ALTER COLUMN divisao_id DROP NOT NULL;

-- ===============================================
-- PASSO 3: Verificar se funcionou
-- ===============================================

SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'usuarios'
  AND column_name IN ('id', 'cargo_id', 'divisao_id');

-- Resultado esperado:
-- id: is_nullable = NO ✅
-- cargo_id: is_nullable = YES ✅
-- divisao_id: is_nullable = YES ✅

-- ===============================================
-- PASSO 4: Criar perfis para usuários sem perfil
-- ===============================================

-- Agora pode executar sem erro de NOT NULL:
INSERT INTO public.usuarios (id, email, nome, ativo, created_at, updated_at)
SELECT
  a.id,
  a.email,
  COALESCE(a.raw_user_meta_data->>'full_name', a.email) as nome,
  true as ativo,
  a.created_at,
  NOW() as updated_at
FROM auth.users a
LEFT JOIN public.usuarios u ON a.id = u.id
WHERE u.id IS NULL
ON CONFLICT (id) DO NOTHING;

-- ===============================================
-- PASSO 5: Verificar usuários
-- ===============================================

SELECT
    u.id,
    u.email,
    u.nome,
    u.cargo_id,
    u.divisao_id,
    u.ativo,
    c.nome as cargo_nome,
    c.nivel_acesso,
    d.nome as divisao_nome
FROM public.usuarios u
LEFT JOIN public.cargos c ON u.cargo_id = c.id
LEFT JOIN public.divisoes d ON u.divisao_id = d.id
ORDER BY u.created_at DESC;

-- ===============================================
-- FIM DO SCRIPT
-- ===============================================

/*
ESTRUTURA CORRETA:

Tabela: public.usuarios
├── id (uuid, PK, NOT NULL) → FK auth.users(id)
├── email (text, NOT NULL)
├── nome (text, NOT NULL)
├── cargo_id (uuid, NULL OK) → FK cargos(id) - Admin atribui depois
├── divisao_id (uuid, NULL OK) → FK divisoes(id) - Admin atribui depois
├── ativo (boolean, NOT NULL, DEFAULT true)
├── created_at (timestamp, NOT NULL)
└── updated_at (timestamp, NOT NULL)

NÍVEIS DE ACESSO (via cargos.nivel_acesso):
- nivel_acesso >= 5: Admin (pode gerenciar usuários, criar análises)
- nivel_acesso >= 4: Master/Diretor/Gerente (vê todas análises)
- nivel_acesso < 4: Usuário comum (vê apenas análises públicas + divisão)

NÃO EXISTE coluna "role"! O papel é determinado pelo cargo.
*/
