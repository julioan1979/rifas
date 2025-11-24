-- ============================================
-- SISTEMA DE GESTÃO DE RIFAS - SETUP COMPLETO
-- Script atualizado com tabela campanhas
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TABELA: campanhas
-- ============================================
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

CREATE INDEX IF NOT EXISTS idx_campanhas_ativa ON campanhas(ativa);
CREATE INDEX IF NOT EXISTS idx_campanhas_nome ON campanhas(nome);

-- ============================================
-- TABELA: escuteiros
-- ============================================
CREATE TABLE IF NOT EXISTS escuteiros (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    email TEXT,
    telefone TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_escuteiros_nome ON escuteiros(nome);
CREATE INDEX IF NOT EXISTS idx_escuteiros_ativo ON escuteiros(ativo);

-- ============================================
-- TABELA: blocos_rifas
-- ============================================
CREATE TABLE IF NOT EXISTS blocos_rifas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campanha_id UUID REFERENCES campanhas(id) ON DELETE CASCADE,
    nome TEXT NOT NULL,
    numero_inicial INTEGER NOT NULL,
    numero_final INTEGER NOT NULL,
    preco_unitario DECIMAL(10, 2) NOT NULL,
    escuteiro_id UUID REFERENCES escuteiros(id) ON DELETE SET NULL,
    seccao TEXT,
    data_atribuicao TIMESTAMP WITH TIME ZONE,
    estado TEXT DEFAULT 'disponivel' CHECK (estado IN ('disponivel', 'atribuido', 'vendido', 'devolvido')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT check_numeros CHECK (numero_final >= numero_inicial)
);

CREATE INDEX IF NOT EXISTS idx_blocos_rifas_campanha ON blocos_rifas(campanha_id);
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_escuteiro ON blocos_rifas(escuteiro_id);
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_estado ON blocos_rifas(estado);
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_seccao ON blocos_rifas(seccao);

-- ============================================
-- TABELA: vendas
-- ============================================
CREATE TABLE IF NOT EXISTS vendas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    escuteiro_id UUID REFERENCES escuteiros(id) ON DELETE CASCADE,
    bloco_id UUID REFERENCES blocos_rifas(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    valor_total DECIMAL(10, 2) NOT NULL CHECK (valor_total >= 0),
    data_venda TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vendas_escuteiro ON vendas(escuteiro_id);
CREATE INDEX IF NOT EXISTS idx_vendas_bloco ON vendas(bloco_id);
CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data_venda);

-- ============================================
-- TABELA: pagamentos
-- ============================================
CREATE TABLE IF NOT EXISTS pagamentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venda_id UUID REFERENCES vendas(id) ON DELETE CASCADE,
    valor_pago DECIMAL(10, 2) NOT NULL CHECK (valor_pago > 0),
    data_pagamento TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metodo_pagamento TEXT DEFAULT 'Dinheiro',
    referencia TEXT,
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pagamentos_venda ON pagamentos(venda_id);
CREATE INDEX IF NOT EXISTS idx_pagamentos_data ON pagamentos(data_pagamento);

-- ============================================
-- TABELA: devolucoes
-- ============================================
CREATE TABLE IF NOT EXISTS devolucoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    escuteiro_id UUID REFERENCES escuteiros(id) ON DELETE CASCADE,
    bloco_id UUID REFERENCES blocos_rifas(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    motivo TEXT,
    data_devolucao TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_devolucoes_escuteiro ON devolucoes(escuteiro_id);
CREATE INDEX IF NOT EXISTS idx_devolucoes_bloco ON devolucoes(bloco_id);
CREATE INDEX IF NOT EXISTS idx_devolucoes_data ON devolucoes(data_devolucao);

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================
ALTER TABLE campanhas ENABLE ROW LEVEL SECURITY;
ALTER TABLE escuteiros ENABLE ROW LEVEL SECURITY;
ALTER TABLE blocos_rifas ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendas ENABLE ROW LEVEL SECURITY;
ALTER TABLE pagamentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE devolucoes ENABLE ROW LEVEL SECURITY;

-- Políticas permissivas para desenvolvimento
-- ATENÇÃO: Para produção, ajuste estas políticas conforme necessário
DROP POLICY IF EXISTS "Enable all for authenticated users" ON campanhas;
CREATE POLICY "Enable all for authenticated users" ON campanhas FOR ALL USING (true);

DROP POLICY IF EXISTS "Enable all for authenticated users" ON escuteiros;
CREATE POLICY "Enable all for authenticated users" ON escuteiros FOR ALL USING (true);

DROP POLICY IF EXISTS "Enable all for authenticated users" ON blocos_rifas;
CREATE POLICY "Enable all for authenticated users" ON blocos_rifas FOR ALL USING (true);

DROP POLICY IF EXISTS "Enable all for authenticated users" ON vendas;
CREATE POLICY "Enable all for authenticated users" ON vendas FOR ALL USING (true);

DROP POLICY IF EXISTS "Enable all for authenticated users" ON pagamentos;
CREATE POLICY "Enable all for authenticated users" ON pagamentos FOR ALL USING (true);

DROP POLICY IF EXISTS "Enable all for authenticated users" ON devolucoes;
CREATE POLICY "Enable all for authenticated users" ON devolucoes FOR ALL USING (true);

-- ============================================
-- VIEWS PARA RELATÓRIOS
-- ============================================

-- View: Resumo de vendas por escuteiro
CREATE OR REPLACE VIEW vw_vendas_por_escuteiro AS
SELECT 
    e.id as escuteiro_id,
    e.nome as escuteiro_nome,
    COUNT(v.id) as total_vendas,
    COALESCE(SUM(v.quantidade), 0) as total_rifas_vendidas,
    COALESCE(SUM(v.valor_total), 0) as valor_total_vendas,
    COALESCE(SUM(p.valor_pago), 0) as total_pago,
    COALESCE(SUM(v.valor_total) - SUM(p.valor_pago), 0) as saldo_pendente
FROM escuteiros e
LEFT JOIN vendas v ON e.id = v.escuteiro_id
LEFT JOIN pagamentos p ON v.id = p.venda_id
GROUP BY e.id, e.nome;

-- View: Estado dos blocos
CREATE OR REPLACE VIEW vw_blocos_status AS
SELECT 
    estado,
    COUNT(*) as quantidade,
    SUM(numero_final - numero_inicial + 1) as total_rifas
FROM blocos_rifas
GROUP BY estado;

-- View: Resumo de blocos por campanha
CREATE OR REPLACE VIEW vw_blocos_por_campanha AS
SELECT 
    c.id as campanha_id,
    c.nome as campanha_nome,
    c.ativa as campanha_ativa,
    COUNT(b.id) as total_blocos,
    SUM(b.numero_final - b.numero_inicial + 1) as total_rifas,
    COUNT(CASE WHEN b.estado = 'atribuido' THEN 1 END) as blocos_atribuidos,
    COUNT(CASE WHEN b.estado = 'vendido' THEN 1 END) as blocos_vendidos,
    COUNT(CASE WHEN b.estado = 'disponivel' THEN 1 END) as blocos_disponiveis,
    COUNT(CASE WHEN b.estado = 'devolvido' THEN 1 END) as blocos_devolvidos
FROM campanhas c
LEFT JOIN blocos_rifas b ON c.id = b.campanha_id
GROUP BY c.id, c.nome, c.ativa;

-- View: Resumo de vendas por campanha
CREATE OR REPLACE VIEW vw_vendas_por_campanha AS
SELECT 
    c.id as campanha_id,
    c.nome as campanha_nome,
    COUNT(DISTINCT v.id) as total_vendas,
    COALESCE(SUM(v.quantidade), 0) as total_rifas_vendidas,
    COALESCE(SUM(v.valor_total), 0) as valor_total_vendas,
    COALESCE(SUM(p.valor_pago), 0) as total_pago,
    COALESCE(SUM(v.valor_total) - SUM(p.valor_pago), 0) as saldo_pendente
FROM campanhas c
LEFT JOIN blocos_rifas b ON c.id = b.campanha_id
LEFT JOIN vendas v ON b.id = v.bloco_id
LEFT JOIN pagamentos p ON v.id = p.venda_id
GROUP BY c.id, c.nome;

-- ============================================
-- CONFIRMAÇÃO
-- ============================================
SELECT 'Setup completo concluído com sucesso! ✅' as status;
SELECT 'Tabelas criadas: campanhas, escuteiros, blocos_rifas, vendas, pagamentos, devolucoes' as tabelas;
SELECT 'Views criadas: vw_vendas_por_escuteiro, vw_blocos_status, vw_blocos_por_campanha, vw_vendas_por_campanha' as views;
