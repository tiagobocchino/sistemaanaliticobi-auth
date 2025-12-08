-- =====================================================
-- Analytics Platform - Base Tables Setup
-- =====================================================
-- Este script cria as tabelas principais do sistema:
-- 1. cargos (Posições/Funções)
-- 2. divisoes (Departamentos/Divisões)
-- 3. usuarios (Perfis de usuário com RLS)
-- =====================================================

-- =====================================================
-- 1. TABELA DE CARGOS
-- =====================================================
CREATE TABLE IF NOT EXISTS public.cargos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    nivel_acesso INTEGER NOT NULL DEFAULT 1, -- Nível de acesso (1-5, sendo 5 o mais alto)
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Comentários na tabela
COMMENT ON TABLE public.cargos IS 'Tabela de cargos/funções dos usuários';
COMMENT ON COLUMN public.cargos.nivel_acesso IS 'Nível de acesso do cargo (1-5)';

-- Índices
CREATE INDEX IF NOT EXISTS idx_cargos_ativo ON public.cargos(ativo);
CREATE INDEX IF NOT EXISTS idx_cargos_nivel_acesso ON public.cargos(nivel_acesso);

-- =====================================================
-- 2. TABELA DE DIVISÕES
-- =====================================================
CREATE TABLE IF NOT EXISTS public.divisoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    codigo VARCHAR(20) UNIQUE, -- Código/sigla da divisão (ex: TI, RH, FIN)
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Comentários na tabela
COMMENT ON TABLE public.divisoes IS 'Tabela de divisões/departamentos da empresa';
COMMENT ON COLUMN public.divisoes.codigo IS 'Código/sigla da divisão';

-- Índices
CREATE INDEX IF NOT EXISTS idx_divisoes_ativo ON public.divisoes(ativo);
CREATE INDEX IF NOT EXISTS idx_divisoes_codigo ON public.divisoes(codigo);

-- =====================================================
-- 3. TABELA DE USUÁRIOS (PERFIS)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.usuarios (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    cargo_id UUID NOT NULL REFERENCES public.cargos(id) ON DELETE RESTRICT,
    divisao_id UUID NOT NULL REFERENCES public.divisoes(id) ON DELETE RESTRICT,
    ativo BOOLEAN NOT NULL DEFAULT true,
    avatar_url TEXT,
    telefone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Comentários na tabela
COMMENT ON TABLE public.usuarios IS 'Perfis estendidos dos usuários vinculados ao auth.users';
COMMENT ON COLUMN public.usuarios.id IS 'FK para auth.users.id';
COMMENT ON COLUMN public.usuarios.cargo_id IS 'Cargo do usuário (usado para RLS)';
COMMENT ON COLUMN public.usuarios.divisao_id IS 'Divisão do usuário (usado para RLS)';

-- Índices
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON public.usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_cargo_id ON public.usuarios(cargo_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_divisao_id ON public.usuarios(divisao_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_ativo ON public.usuarios(ativo);
CREATE INDEX IF NOT EXISTS idx_usuarios_cargo_divisao ON public.usuarios(cargo_id, divisao_id);

-- =====================================================
-- 4. FUNÇÃO PARA ATUALIZAR updated_at AUTOMATICAMENTE
-- =====================================================
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 5. TRIGGERS PARA updated_at
-- =====================================================
DROP TRIGGER IF EXISTS update_cargos_updated_at ON public.cargos;
CREATE TRIGGER update_cargos_updated_at
    BEFORE UPDATE ON public.cargos
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_divisoes_updated_at ON public.divisoes;
CREATE TRIGGER update_divisoes_updated_at
    BEFORE UPDATE ON public.divisoes
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_usuarios_updated_at ON public.usuarios;
CREATE TRIGGER update_usuarios_updated_at
    BEFORE UPDATE ON public.usuarios
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- 6. INSERIR DADOS INICIAIS (SEEDS)
-- =====================================================

-- Cargos iniciais
INSERT INTO public.cargos (nome, descricao, nivel_acesso) VALUES
    ('Administrador', 'Acesso total ao sistema', 5),
    ('Gerente', 'Acesso gerencial', 4),
    ('Coordenador', 'Coordenação de equipes', 3),
    ('Analista', 'Análise de dados', 2),
    ('Assistente', 'Suporte operacional', 1)
ON CONFLICT (nome) DO NOTHING;

-- Divisões iniciais
INSERT INTO public.divisoes (nome, descricao, codigo) VALUES
    ('Tecnologia da Informação', 'Departamento de TI', 'TI'),
    ('Recursos Humanos', 'Departamento de RH', 'RH'),
    ('Financeiro', 'Departamento Financeiro', 'FIN'),
    ('Comercial', 'Departamento Comercial', 'COM'),
    ('Operações', 'Departamento de Operações', 'OPS')
ON CONFLICT (nome) DO NOTHING;

-- =====================================================
-- 7. ROW LEVEL SECURITY (RLS) - CONFIGURAÇÃO INICIAL
-- =====================================================

-- Habilitar RLS nas tabelas
ALTER TABLE public.cargos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.divisoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usuarios ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- POLÍTICAS RLS - CARGOS
-- =====================================================

-- Todos podem visualizar cargos ativos
DROP POLICY IF EXISTS "Cargos são visíveis para todos usuários autenticados" ON public.cargos;
CREATE POLICY "Cargos são visíveis para todos usuários autenticados"
    ON public.cargos FOR SELECT
    TO authenticated
    USING (ativo = true);

-- Apenas administradores podem inserir/atualizar/deletar cargos
DROP POLICY IF EXISTS "Apenas administradores podem gerenciar cargos" ON public.cargos;
CREATE POLICY "Apenas administradores podem gerenciar cargos"
    ON public.cargos FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.usuarios u
            INNER JOIN public.cargos c ON u.cargo_id = c.id
            WHERE u.id = auth.uid() AND c.nivel_acesso = 5
        )
    );

-- =====================================================
-- POLÍTICAS RLS - DIVISÕES
-- =====================================================

-- Todos podem visualizar divisões ativas
DROP POLICY IF EXISTS "Divisões são visíveis para todos usuários autenticados" ON public.divisoes;
CREATE POLICY "Divisões são visíveis para todos usuários autenticados"
    ON public.divisoes FOR SELECT
    TO authenticated
    USING (ativo = true);

-- Apenas administradores podem inserir/atualizar/deletar divisões
DROP POLICY IF EXISTS "Apenas administradores podem gerenciar divisões" ON public.divisoes;
CREATE POLICY "Apenas administradores podem gerenciar divisões"
    ON public.divisoes FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.usuarios u
            INNER JOIN public.cargos c ON u.cargo_id = c.id
            WHERE u.id = auth.uid() AND c.nivel_acesso = 5
        )
    );

-- =====================================================
-- POLÍTICAS RLS - USUÁRIOS
-- =====================================================

-- Usuários podem ver seu próprio perfil
DROP POLICY IF EXISTS "Usuários podem ver seu próprio perfil" ON public.usuarios;
CREATE POLICY "Usuários podem ver seu próprio perfil"
    ON public.usuarios FOR SELECT
    TO authenticated
    USING (id = auth.uid());

-- Administradores e gerentes podem ver todos os usuários
DROP POLICY IF EXISTS "Administradores e gerentes podem ver todos usuários" ON public.usuarios;
CREATE POLICY "Administradores e gerentes podem ver todos usuários"
    ON public.usuarios FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.usuarios u
            INNER JOIN public.cargos c ON u.cargo_id = c.id
            WHERE u.id = auth.uid() AND c.nivel_acesso >= 4
        )
    );

-- Usuários podem ver outros da mesma divisão
DROP POLICY IF EXISTS "Usuários podem ver colegas da mesma divisão" ON public.usuarios;
CREATE POLICY "Usuários podem ver colegas da mesma divisão"
    ON public.usuarios FOR SELECT
    TO authenticated
    USING (
        divisao_id IN (
            SELECT divisao_id FROM public.usuarios WHERE id = auth.uid()
        )
    );

-- Usuários podem atualizar seu próprio perfil (exceto cargo e divisão)
DROP POLICY IF EXISTS "Usuários podem atualizar seu próprio perfil" ON public.usuarios;
CREATE POLICY "Usuários podem atualizar seu próprio perfil"
    ON public.usuarios FOR UPDATE
    TO authenticated
    USING (id = auth.uid())
    WITH CHECK (
        id = auth.uid() AND
        -- Não permite alterar cargo_id e divisao_id
        cargo_id = (SELECT cargo_id FROM public.usuarios WHERE id = auth.uid()) AND
        divisao_id = (SELECT divisao_id FROM public.usuarios WHERE id = auth.uid())
    );

-- Apenas administradores podem inserir novos usuários
DROP POLICY IF EXISTS "Apenas administradores podem criar usuários" ON public.usuarios;
CREATE POLICY "Apenas administradores podem criar usuários"
    ON public.usuarios FOR INSERT
    TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.usuarios u
            INNER JOIN public.cargos c ON u.cargo_id = c.id
            WHERE u.id = auth.uid() AND c.nivel_acesso = 5
        )
    );

-- Apenas administradores podem deletar usuários
DROP POLICY IF EXISTS "Apenas administradores podem deletar usuários" ON public.usuarios;
CREATE POLICY "Apenas administradores podem deletar usuários"
    ON public.usuarios FOR DELETE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.usuarios u
            INNER JOIN public.cargos c ON u.cargo_id = c.id
            WHERE u.id = auth.uid() AND c.nivel_acesso = 5
        )
    );

-- =====================================================
-- 8. GRANTS - PERMISSÕES
-- =====================================================

-- Garantir que usuários autenticados possam acessar as tabelas
GRANT SELECT ON public.cargos TO authenticated;
GRANT SELECT ON public.divisoes TO authenticated;
GRANT ALL ON public.usuarios TO authenticated;

-- Garantir que usuários autenticados possam usar as sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- =====================================================
-- FIM DO SCRIPT
-- =====================================================
