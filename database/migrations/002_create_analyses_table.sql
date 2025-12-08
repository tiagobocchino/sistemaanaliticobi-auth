-- =====================================================
-- Analytics Platform - Analyses Table
-- =====================================================
-- Tabela para armazenar dashboards e análises
-- =====================================================

-- =====================================================
-- 1. TABELA DE ANÁLISES
-- =====================================================
CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('powerbi', 'python', 'tableau')),
    embed_url TEXT NOT NULL,
    divisao_restrita_id UUID REFERENCES public.divisoes(id) ON DELETE SET NULL,
    publico BOOLEAN NOT NULL DEFAULT true,
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Comentários na tabela
COMMENT ON TABLE public.analyses IS 'Tabela de análises/dashboards disponíveis no sistema';
COMMENT ON COLUMN public.analyses.tipo IS 'Tipo da análise: powerbi, python, tableau';
COMMENT ON COLUMN public.analyses.embed_url IS 'URL para embed da análise';
COMMENT ON COLUMN public.analyses.divisao_restrita_id IS 'Divisão específica (NULL = todas divisões)';
COMMENT ON COLUMN public.analyses.publico IS 'Se é visível para usuários comuns';

-- Índices
CREATE INDEX IF NOT EXISTS idx_analyses_tipo ON public.analyses(tipo);
CREATE INDEX IF NOT EXISTS idx_analyses_divisao_restrita_id ON public.analyses(divisao_restrita_id);
CREATE INDEX IF NOT EXISTS idx_analyses_publico ON public.analyses(publico);
CREATE INDEX IF NOT EXISTS idx_analyses_ativo ON public.analyses(ativo);

-- =====================================================
-- 2. TRIGGER PARA updated_at
-- =====================================================
DROP TRIGGER IF EXISTS update_analyses_updated_at ON public.analyses;
CREATE TRIGGER update_analyses_updated_at
    BEFORE UPDATE ON public.analyses
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- 3. ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Habilitar RLS
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

-- Política: Análises públicas são visíveis para todos autenticados
DROP POLICY IF EXISTS "Análises públicas são visíveis para todos" ON public.analyses;
CREATE POLICY "Análises públicas são visíveis para todos"
    ON public.analyses FOR SELECT
    TO authenticated
    USING (publico = true AND ativo = true);

-- Política: Análises restritas por divisão são visíveis para usuários da divisão
DROP POLICY IF EXISTS "Análises da divisão são visíveis para usuários da divisão" ON public.analyses;
CREATE POLICY "Análises da divisão são visíveis para usuários da divisão"
    ON public.analyses FOR SELECT
    TO authenticated
    USING (
        divisao_restrita_id IS NOT NULL AND ativo = true AND
        divisao_restrita_id IN (
            SELECT divisao_id FROM public.usuarios WHERE id = auth.uid()
        )
    );

-- Política: Master/Diretor/Gerente podem ver tudo
DROP POLICY IF EXISTS "Administradores podem ver todas análises" ON public.analyses;
CREATE POLICY "Administradores podem ver todas análises"
    ON public.analyses FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.usuarios u
            INNER JOIN public.cargos c ON u.cargo_id = c.id
            WHERE u.id = auth.uid() AND c.nivel_acesso >= 4
        )
    );

-- Política: Apenas administradores podem criar/editar/deletar
DROP POLICY IF EXISTS "Apenas administradores podem gerenciar análises" ON public.analyses;
CREATE POLICY "Apenas administradores podem gerenciar análises"
    ON public.analyses FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.usuarios u
            INNER JOIN public.cargos c ON u.cargo_id = c.id
            WHERE u.id = auth.uid() AND c.nivel_acesso = 5
        )
    );

-- =====================================================
-- 4. GRANTS - PERMISSÕES
-- =====================================================

-- Usuários autenticados podem ler análises
GRANT SELECT ON public.analyses TO authenticated;

-- Administradores podem fazer tudo
GRANT ALL ON public.analyses TO authenticated;

-- Sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- =====================================================
-- 5. DADOS INICIAIS - DASHBOARDS DO CLIENTE
-- =====================================================

-- Dashboard SDRs (TV)
INSERT INTO public.analyses (nome, descricao, tipo, embed_url, publico) VALUES
('Dashboard - SDRs (TV) v2.0', 'Dashboard de acompanhamento dos SDRs de TV', 'powerbi',
 'https://app.powerbi.com/view?r=eyJrIjoiMTIzNDU2NzgiLCJ0IjoiYWJjZGVmZ2giLCJjIjozfQ%3D%3D',
 true)
ON CONFLICT DO NOTHING;

-- Dashboard Compras - DW
INSERT INTO public.analyses (nome, descricao, tipo, embed_url, publico) VALUES
('Dashboard - Compras - DW', 'Dashboard de compras do Data Warehouse', 'powerbi',
 'https://app.powerbi.com/view?r=eyJrIjoiODc2NTQzMjEiLCJ0IjoiZGVmZ2hpamsiLCJjIjo0fQ%3D%3D',
 true)
ON CONFLICT DO NOTHING;

-- =====================================================
-- FIM DO SCRIPT
-- =====================================================