-- ================================================================
-- SCHEMA COMPLETO DO SISTEMA DE GESTÃO DE RIFAS DOS ESCUTEIROS
-- ================================================================
-- 
-- INSTRUÇÕES:
-- 1. Acesse o Supabase Dashboard: https://supabase.com/dashboard
-- 2. Selecione seu projeto
-- 3. Vá em "SQL Editor" no menu lateral
-- 4. Clique em "New query"
-- 5. Copie TODO este arquivo e cole no editor
-- 6. Clique em "Run" para executar
-- 
-- Este script irá:
-- - Ativar a extensão UUID
-- - Criar todas as tabelas necessárias
-- - Criar índices para melhor performance
-- - Ativar Row Level Security (RLS)
-- - Criar policies de acesso
-- - Criar views úteis para relatórios
-- ================================================================

-- ================================================================
-- 1. ATIVAR EXTENSÕES NECESSÁRIAS
-- ================================================================

-- Extensão para gerar UUIDs automaticamente
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ================================================================
-- 2. CRIAR TABELAS
-- ================================================================

-- ----------------------------------------------------------------
-- 2.1 Tabela: campanhas
-- Armazena as campanhas de rifas (ex: Natal2025, Páscoa2026)
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS campanhas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    ativa BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT check_datas CHECK (data_fim >= data_inicio)
);

COMMENT ON TABLE campanhas IS 'Campanhas de rifas (ex: Natal2025, Páscoa2026)';
COMMENT ON COLUMN campanhas.nome IS 'Nome único da campanha';
COMMENT ON COLUMN campanhas.ativa IS 'Indica se a campanha está ativa (pode ter múltiplas ativas)';

-- ----------------------------------------------------------------
-- 2.2 Tabela: escuteiros
-- Armazena os dados dos escuteiros que vendem rifas
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS escuteiros (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    email TEXT,
    telefone TEXT,
    seccao TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE escuteiros IS 'Escuteiros que vendem rifas';
COMMENT ON COLUMN escuteiros.ativo IS 'Se o escuteiro está ativo no sistema';
COMMENT ON COLUMN escuteiros.seccao IS 'Secção do escuteiro: Lobitos, Exploradores, Pioneiros, Caminheiros, CPP';

-- ----------------------------------------------------------------
-- 2.3 Tabela: blocos_rifas
-- Armazena os blocos de rifas (ex: rifas 1-10, 11-20, etc)
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS blocos_rifas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campanha_id UUID NOT NULL REFERENCES campanhas(id) ON DELETE CASCADE,
    nome TEXT NOT NULL,
    numero_inicial INTEGER NOT NULL,
    numero_final INTEGER NOT NULL,
    preco_bloco DECIMAL(10, 2) NOT NULL CHECK (preco_bloco > 0),
    escuteiro_id UUID REFERENCES escuteiros(id) ON DELETE SET NULL,
    seccao TEXT,
    data_atribuicao TIMESTAMP WITH TIME ZONE,
    estado TEXT DEFAULT 'disponivel' CHECK (estado IN ('disponivel', 'atribuido', 'vendido', 'devolvido')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT check_numeros CHECK (numero_final >= numero_inicial)
);

COMMENT ON TABLE blocos_rifas IS 'Blocos de rifas atribuídos a escuteiros';
COMMENT ON COLUMN blocos_rifas.preco_bloco IS 'Preço total do bloco de rifas (não é por unidade)';
COMMENT ON COLUMN blocos_rifas.seccao IS 'Secção do escuteiro: Lobitos, Exploradores, Pioneiros, Caminheiros, CPP';
COMMENT ON COLUMN blocos_rifas.estado IS 'Estado do bloco: disponivel, atribuido, vendido, devolvido';

-- ----------------------------------------------------------------
-- 2.4 Tabela: vendas (MANTIDA PARA COMPATIBILIDADE)
-- NOTA: Mantida apenas para dados históricos. Novos pagamentos 
-- devem usar bloco_id diretamente na tabela pagamentos
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vendas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    escuteiro_id UUID NOT NULL REFERENCES escuteiros(id) ON DELETE CASCADE,
    bloco_id UUID NOT NULL REFERENCES blocos_rifas(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    valor_total DECIMAL(10, 2) NOT NULL CHECK (valor_total >= 0),
    data_venda TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE vendas IS 'TABELA LEGADA - Mantida para compatibilidade. Novos registros devem ir direto para pagamentos';

-- ----------------------------------------------------------------
-- 2.5 Tabela: pagamentos
-- Armazena os pagamentos/prestações de contas dos escuteiros
-- Suporta DOIS fluxos:
-- 1. NOVO (recomendado): bloco_id diretamente
-- 2. LEGADO: venda_id (dados antigos)
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pagamentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venda_id UUID REFERENCES vendas(id) ON DELETE CASCADE,
    bloco_id UUID REFERENCES blocos_rifas(id) ON DELETE CASCADE,
    quantidade_rifas INTEGER CHECK (quantidade_rifas >= 0),
    valor_pago DECIMAL(10, 2) NOT NULL CHECK (valor_pago > 0),
    data_pagamento TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metodo_pagamento TEXT DEFAULT 'Dinheiro',
    referencia TEXT,
    observacoes TEXT,
    canhotos_entregues INTEGER DEFAULT 0 CHECK (canhotos_entregues >= 0),
    canhotos_esperados INTEGER CHECK (canhotos_esperados >= 0),
    data_entrega_canhotos TIMESTAMP WITH TIME ZONE,
    observacoes_canhotos TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT check_venda_ou_bloco CHECK (venda_id IS NOT NULL OR bloco_id IS NOT NULL)
);

COMMENT ON TABLE pagamentos IS 'Pagamentos/prestações de contas dos escuteiros';
COMMENT ON COLUMN pagamentos.venda_id IS 'LEGADO - Referência à tabela vendas (dados antigos)';
COMMENT ON COLUMN pagamentos.bloco_id IS 'NOVO FLUXO - Referência direta ao bloco de rifas';
COMMENT ON COLUMN pagamentos.quantidade_rifas IS 'Quantidade de rifas vendidas reportadas neste pagamento';
COMMENT ON COLUMN pagamentos.canhotos_entregues IS 'Número de canhotos fisicamente entregues';
COMMENT ON COLUMN pagamentos.canhotos_esperados IS 'Número de canhotos que deveriam ser entregues';

-- ----------------------------------------------------------------
-- 2.6 Tabela: devolucoes
-- Armazena devoluções de rifas não vendidas
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS devolucoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    escuteiro_id UUID NOT NULL REFERENCES escuteiros(id) ON DELETE CASCADE,
    bloco_id UUID NOT NULL REFERENCES blocos_rifas(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    motivo TEXT,
    data_devolucao TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE devolucoes IS 'Devoluções de rifas não vendidas pelos escuteiros';

-- ================================================================
-- 3. CRIAR ÍNDICES PARA MELHOR PERFORMANCE
-- ================================================================

-- Índices para campanhas
CREATE INDEX IF NOT EXISTS idx_campanhas_ativa ON campanhas(ativa);
CREATE INDEX IF NOT EXISTS idx_campanhas_datas ON campanhas(data_inicio, data_fim);

-- Índices para escuteiros
CREATE INDEX IF NOT EXISTS idx_escuteiros_nome ON escuteiros(nome);
CREATE INDEX IF NOT EXISTS idx_escuteiros_ativo ON escuteiros(ativo);
CREATE INDEX IF NOT EXISTS idx_escuteiros_seccao ON escuteiros(seccao);

-- Índices para blocos_rifas
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_campanha ON blocos_rifas(campanha_id);
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_escuteiro ON blocos_rifas(escuteiro_id);
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_estado ON blocos_rifas(estado);
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_seccao ON blocos_rifas(seccao);
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_numeros ON blocos_rifas(numero_inicial, numero_final);

-- Índices para vendas
CREATE INDEX IF NOT EXISTS idx_vendas_escuteiro ON vendas(escuteiro_id);
CREATE INDEX IF NOT EXISTS idx_vendas_bloco ON vendas(bloco_id);
CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data_venda);

-- Índices para pagamentos
CREATE INDEX IF NOT EXISTS idx_pagamentos_venda ON pagamentos(venda_id);
CREATE INDEX IF NOT EXISTS idx_pagamentos_bloco ON pagamentos(bloco_id);
CREATE INDEX IF NOT EXISTS idx_pagamentos_data ON pagamentos(data_pagamento);
CREATE INDEX IF NOT EXISTS idx_pagamentos_canhotos_status ON pagamentos(canhotos_entregues, canhotos_esperados);

-- Índices para devolucoes
CREATE INDEX IF NOT EXISTS idx_devolucoes_escuteiro ON devolucoes(escuteiro_id);
CREATE INDEX IF NOT EXISTS idx_devolucoes_bloco ON devolucoes(bloco_id);
CREATE INDEX IF NOT EXISTS idx_devolucoes_data ON devolucoes(data_devolucao);

-- ================================================================
-- 4. ATIVAR ROW LEVEL SECURITY (RLS)
-- ================================================================

-- Ativar RLS em todas as tabelas
ALTER TABLE campanhas ENABLE ROW LEVEL SECURITY;
ALTER TABLE escuteiros ENABLE ROW LEVEL SECURITY;
ALTER TABLE blocos_rifas ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendas ENABLE ROW LEVEL SECURITY;
ALTER TABLE pagamentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE devolucoes ENABLE ROW LEVEL SECURITY;

-- ================================================================
-- 5. CRIAR POLÍTICAS DE ACESSO (RLS POLICIES)
-- ================================================================
-- 
-- NOTA: Para desenvolvimento, usamos políticas permissivas que 
-- permitem todas as operações. Para produção, ajuste conforme 
-- suas necessidades de segurança.
-- ================================================================

-- Remover políticas existentes se houver
DROP POLICY IF EXISTS "Enable all for authenticated users" ON campanhas;
DROP POLICY IF EXISTS "Enable all for authenticated users" ON escuteiros;
DROP POLICY IF EXISTS "Enable all for authenticated users" ON blocos_rifas;
DROP POLICY IF EXISTS "Enable all for authenticated users" ON vendas;
DROP POLICY IF EXISTS "Enable all for authenticated users" ON pagamentos;
DROP POLICY IF EXISTS "Enable all for authenticated users" ON devolucoes;

-- Políticas permissivas para todas as tabelas
CREATE POLICY "Enable all for authenticated users" ON campanhas
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Enable all for authenticated users" ON escuteiros
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Enable all for authenticated users" ON blocos_rifas
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Enable all for authenticated users" ON vendas
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Enable all for authenticated users" ON pagamentos
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Enable all for authenticated users" ON devolucoes
    FOR ALL USING (true) WITH CHECK (true);

-- ================================================================
-- 6. CRIAR VIEWS ÚTEIS PARA RELATÓRIOS
-- ================================================================

-- ----------------------------------------------------------------
-- 6.1 View: Resumo de vendas por escuteiro
-- ----------------------------------------------------------------
CREATE OR REPLACE VIEW vw_vendas_por_escuteiro AS
SELECT 
    e.id as escuteiro_id,
    e.nome as escuteiro_nome,
    COUNT(DISTINCT v.id) as total_vendas,
    COALESCE(SUM(v.quantidade), 0) as total_rifas_vendidas,
    COALESCE(SUM(v.valor_total), 0) as valor_total_vendas,
    COALESCE(SUM(p.valor_pago), 0) as total_pago,
    COALESCE(SUM(v.valor_total) - SUM(p.valor_pago), 0) as saldo_pendente
FROM escuteiros e
LEFT JOIN vendas v ON e.id = v.escuteiro_id
LEFT JOIN pagamentos p ON v.id = p.venda_id
WHERE e.ativo = true
GROUP BY e.id, e.nome
ORDER BY total_rifas_vendidas DESC;

COMMENT ON VIEW vw_vendas_por_escuteiro IS 'Resumo de vendas e pagamentos por escuteiro (apenas dados legados via tabela vendas)';

-- ----------------------------------------------------------------
-- 6.2 View: Status dos blocos
-- ----------------------------------------------------------------
CREATE OR REPLACE VIEW vw_blocos_status AS
SELECT 
    b.campanha_id,
    c.nome as campanha_nome,
    b.estado,
    COUNT(*) as quantidade_blocos,
    SUM(b.numero_final - b.numero_inicial + 1) as total_rifas,
    SUM(b.preco_bloco) as valor_total
FROM blocos_rifas b
JOIN campanhas c ON b.campanha_id = c.id
GROUP BY b.campanha_id, c.nome, b.estado
ORDER BY c.nome, b.estado;

COMMENT ON VIEW vw_blocos_status IS 'Resumo do estado dos blocos por campanha';

-- ----------------------------------------------------------------
-- 6.3 View: Resumo de pagamentos por bloco (NOVO FLUXO)
-- ----------------------------------------------------------------
CREATE OR REPLACE VIEW vw_pagamentos_por_bloco AS
SELECT 
    b.id as bloco_id,
    b.campanha_id,
    c.nome as campanha_nome,
    b.numero_inicial,
    b.numero_final,
    (b.numero_final - b.numero_inicial + 1) as total_rifas_bloco,
    b.preco_bloco,
    b.preco_bloco as valor_total_bloco,
    e.id as escuteiro_id,
    e.nome as escuteiro_nome,
    COALESCE(SUM(p.quantidade_rifas), 0) as rifas_reportadas,
    COALESCE(SUM(p.valor_pago), 0) as total_pago,
    COALESCE(SUM(p.canhotos_entregues), 0) as canhotos_entregues,
    COALESCE(SUM(p.canhotos_esperados), 0) as canhotos_esperados,
    b.preco_bloco - COALESCE(SUM(p.valor_pago), 0) as saldo_pendente,
    (b.numero_final - b.numero_inicial + 1) - COALESCE(SUM(p.quantidade_rifas), 0) as rifas_pendentes
FROM blocos_rifas b
JOIN campanhas c ON b.campanha_id = c.id
LEFT JOIN escuteiros e ON b.escuteiro_id = e.id
LEFT JOIN pagamentos p ON p.bloco_id = b.id
WHERE b.escuteiro_id IS NOT NULL
GROUP BY b.id, b.campanha_id, c.nome, b.numero_inicial, b.numero_final, 
         b.preco_bloco, e.id, e.nome
ORDER BY c.nome, b.numero_inicial;

COMMENT ON VIEW vw_pagamentos_por_bloco IS 'Resumo de pagamentos e status por bloco (novo fluxo direto)';

-- ----------------------------------------------------------------
-- 6.4 View: Resumo de canhotos pendentes
-- ----------------------------------------------------------------
CREATE OR REPLACE VIEW vw_canhotos_pendentes AS
SELECT 
    e.id as escuteiro_id,
    e.nome as escuteiro_nome,
    b.campanha_id,
    c.nome as campanha_nome,
    b.id as bloco_id,
    b.numero_inicial,
    b.numero_final,
    SUM(p.canhotos_esperados) as total_esperados,
    SUM(p.canhotos_entregues) as total_entregues,
    SUM(p.canhotos_esperados) - SUM(p.canhotos_entregues) as canhotos_pendentes
FROM pagamentos p
JOIN blocos_rifas b ON p.bloco_id = b.id
JOIN campanhas c ON b.campanha_id = c.id
JOIN escuteiros e ON b.escuteiro_id = e.id
WHERE p.bloco_id IS NOT NULL
GROUP BY e.id, e.nome, b.campanha_id, c.nome, b.id, b.numero_inicial, b.numero_final
HAVING SUM(p.canhotos_esperados) - SUM(p.canhotos_entregues) > 0
ORDER BY canhotos_pendentes DESC;

COMMENT ON VIEW vw_canhotos_pendentes IS 'Lista de escuteiros com canhotos pendentes de entrega';

-- ================================================================
-- 7. CRIAR FUNÇÃO PARA ATUALIZAR ESTADO DO BLOCO AUTOMATICAMENTE
-- ================================================================

-- Função para atualizar estado do bloco baseado em pagamentos
CREATE OR REPLACE FUNCTION atualizar_estado_bloco()
RETURNS TRIGGER AS $$
BEGIN
    -- Se é um pagamento novo ou atualizado com bloco_id
    IF NEW.bloco_id IS NOT NULL THEN
        -- Verificar se todas as rifas do bloco foram reportadas
        DECLARE
            total_rifas INTEGER;
            rifas_reportadas INTEGER;
        BEGIN
            -- Buscar total de rifas do bloco
            SELECT numero_final - numero_inicial + 1 
            INTO total_rifas
            FROM blocos_rifas 
            WHERE id = NEW.bloco_id;
            
            -- Somar rifas reportadas
            SELECT COALESCE(SUM(quantidade_rifas), 0)
            INTO rifas_reportadas
            FROM pagamentos
            WHERE bloco_id = NEW.bloco_id;
            
            -- Atualizar estado do bloco
            IF rifas_reportadas >= total_rifas THEN
                UPDATE blocos_rifas 
                SET estado = 'vendido'
                WHERE id = NEW.bloco_id;
            ELSIF rifas_reportadas > 0 THEN
                UPDATE blocos_rifas 
                SET estado = 'atribuido'
                WHERE id = NEW.bloco_id;
            END IF;
        END;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar estado automaticamente ao inserir/atualizar pagamento
DROP TRIGGER IF EXISTS trigger_atualizar_estado_bloco ON pagamentos;
CREATE TRIGGER trigger_atualizar_estado_bloco
    AFTER INSERT OR UPDATE ON pagamentos
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_estado_bloco();

COMMENT ON FUNCTION atualizar_estado_bloco IS 'Atualiza automaticamente o estado do bloco quando pagamentos são registrados';

-- ================================================================
-- 8. INSERIR DADOS DE EXEMPLO (OPCIONAL)
-- ================================================================
-- 
-- DESCOMENTE as linhas abaixo se quiser criar dados de exemplo
-- para testar o sistema
-- ================================================================

/*
-- Inserir campanha de exemplo
INSERT INTO campanhas (nome, descricao, data_inicio, data_fim, ativa)
VALUES ('Natal2025', 'Campanha de rifas de Natal 2025', '2025-11-01', '2025-12-31', true);

-- Inserir escuteiros de exemplo
INSERT INTO escuteiros (nome, email, telefone, ativo)
VALUES 
    ('João Silva', 'joao@exemplo.com', '912345678', true),
    ('Maria Santos', 'maria@exemplo.com', '923456789', true),
    ('Pedro Costa', 'pedro@exemplo.com', '934567890', true);
*/

-- ================================================================
-- 9. VERIFICAÇÃO FINAL
-- ================================================================

-- Listar todas as tabelas criadas
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('campanhas', 'escuteiros', 'blocos_rifas', 'vendas', 'pagamentos', 'devolucoes')
ORDER BY tablename;

-- Mostrar resumo
DO $$ 
BEGIN
    RAISE NOTICE '✅ Schema criado com sucesso!';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Resumo:';
    RAISE NOTICE '  - 6 tabelas criadas';
    RAISE NOTICE '  - Índices otimizados';
    RAISE NOTICE '  - RLS ativado';
    RAISE NOTICE '  - Views para relatórios';
    RAISE NOTICE '  - Trigger automático para estado de blocos';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Próximos passos:';
    RAISE NOTICE '  1. Configure as variáveis de ambiente (SUPABASE_URL e SUPABASE_KEY)';
    RAISE NOTICE '  2. Execute: streamlit run app.py';
    RAISE NOTICE '  3. Crie uma campanha';
    RAISE NOTICE '  4. Adicione escuteiros';
    RAISE NOTICE '  5. Crie blocos de rifas';
    RAISE NOTICE '';
END $$;
