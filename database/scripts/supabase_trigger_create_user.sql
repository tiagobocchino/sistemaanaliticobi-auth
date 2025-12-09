-- ===============================================
-- TRIGGER: Criar perfil automaticamente quando usuário é criado
-- ===============================================
-- Este trigger cria automaticamente um registro na tabela public.usuarios
-- sempre que um novo usuário é criado em auth.users

-- 1. Função que será executada pelo trigger
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
    NULLIF((NEW.raw_user_meta_data->>'cargo_id'), '')::uuid,  -- NULL se vazio
    NULLIF((NEW.raw_user_meta_data->>'divisao_id'), '')::uuid, -- NULL se vazio
    true,
    NOW(),
    NOW()
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Remover trigger existente se houver
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- 3. Criar trigger
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- ===============================================
-- EXPLICAÇÃO:
-- ===============================================
-- Quando um usuário é criado via signup:
-- 1. Supabase insere em auth.users
-- 2. Trigger on_auth_user_created dispara
-- 3. Função handle_new_user() é executada
-- 4. Perfil é criado em public.usuarios com:
--    - id: mesmo id de auth.users
--    - email: email do usuário
--    - nome: full_name do metadata OU email (fallback)
--    - cargo_id: extraído do metadata (pode ser null)
--    - divisao_id: extraído do metadata (pode ser null)
--    - ativo: true por padrão
--    - timestamps: NOW()
--
-- IMPORTANTE: Execute este script no SQL Editor do Supabase!
-- ===============================================
