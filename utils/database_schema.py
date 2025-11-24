"""
Database schema documentation for the raffle management system

The database should have the following tables in Supabase:

1. campanhas (campaigns)
   - id: UUID (primary key)
   - nome: TEXT (campaign name, e.g., "Natal2025")
   - descricao: TEXT (optional description)
   - data_inicio: DATE (campaign start date)
   - data_fim: DATE (campaign end date)
   - ativa: BOOLEAN (is currently active)
   - created_at: TIMESTAMP

2. escuteiros (scouts)
   - id: UUID (primary key)
   - nome: TEXT (scout name)
   - email: TEXT (optional)
   - telefone: TEXT (optional)
   - ativo: BOOLEAN (active status, default true)
   - created_at: TIMESTAMP

3. blocos_rifas (raffle blocks)
   - id: UUID (primary key)
   - campanha_id: UUID (foreign key to campanhas)
   - nome: TEXT (block name)
   - numero_inicial: INTEGER (starting number)
   - numero_final: INTEGER (ending number)
   - preco_unitario: DECIMAL (price per ticket)
   - escuteiro_id: UUID (foreign key to escuteiros - assigned scout)
   - seccao: TEXT (scout section: Reserva, Lobitos, Exploradores, Pioneiros, Caminheiros)
   - data_atribuicao: TIMESTAMP (assignment date)
   - estado: TEXT (estado: 'disponivel', 'atribuido', 'vendido', 'devolvido')
   - created_at: TIMESTAMP

4. vendas (sales)
   - id: UUID (primary key)
   - escuteiro_id: UUID (foreign key to escuteiros)
   - bloco_id: UUID (foreign key to blocos_rifas)
   - quantidade: INTEGER (number of tickets sold)
   - valor_total: DECIMAL (total value)
   - data_venda: TIMESTAMP
   - observacoes: TEXT (notes)
   - created_at: TIMESTAMP

5. pagamentos (payments)
   - id: UUID (primary key)
   - venda_id: UUID (foreign key to vendas)
   - valor_pago: DECIMAL (amount paid)
   - data_pagamento: TIMESTAMP
   - metodo_pagamento: TEXT (payment method)
   - referencia: TEXT (payment reference)
   - observacoes: TEXT (notes)
   - canhotos_entregues: INTEGER (number of stubs delivered)
   - canhotos_esperados: INTEGER (number of stubs expected)
   - data_entrega_canhotos: TIMESTAMP (stub delivery date)
   - observacoes_canhotos: TEXT (stub delivery notes)
   - created_at: TIMESTAMP

6. devolucoes (returns)
   - id: UUID (primary key)
   - escuteiro_id: UUID (foreign key to escuteiros)
   - bloco_id: UUID (foreign key to blocos_rifas)
   - quantidade: INTEGER (number of tickets returned)
   - motivo: TEXT (reason for return)
   - data_devolucao: TIMESTAMP
   - created_at: TIMESTAMP

SQL to create these tables in Supabase:

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Campanhas table
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

-- Create index
CREATE INDEX IF NOT EXISTS idx_campanhas_ativa ON campanhas(ativa);

-- Escuteiros table
CREATE TABLE IF NOT EXISTS escuteiros (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    email TEXT,
    telefone TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_escuteiros_nome ON escuteiros(nome);
CREATE INDEX IF NOT EXISTS idx_escuteiros_ativo ON escuteiros(ativo);

-- Blocos de rifas table
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

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_campanha ON blocos_rifas(campanha_id);
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_escuteiro ON blocos_rifas(escuteiro_id);
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_estado ON blocos_rifas(estado);

-- Vendas table
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

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_vendas_escuteiro ON vendas(escuteiro_id);
CREATE INDEX IF NOT EXISTS idx_vendas_bloco ON vendas(bloco_id);
CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data_venda);

-- Pagamentos table
CREATE TABLE IF NOT EXISTS pagamentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venda_id UUID REFERENCES vendas(id) ON DELETE CASCADE,
    valor_pago DECIMAL(10, 2) NOT NULL CHECK (valor_pago > 0),
    data_pagamento TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metodo_pagamento TEXT DEFAULT 'Dinheiro',
    referencia TEXT,
    observacoes TEXT,
    canhotos_entregues INTEGER DEFAULT 0 CHECK (canhotos_entregues >= 0),
    canhotos_esperados INTEGER CHECK (canhotos_esperados >= 0),
    data_entrega_canhotos TIMESTAMP WITH TIME ZONE,
    observacoes_canhotos TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_pagamentos_venda ON pagamentos(venda_id);
CREATE INDEX IF NOT EXISTS idx_pagamentos_data ON pagamentos(data_pagamento);
CREATE INDEX IF NOT EXISTS idx_pagamentos_canhotos_status ON pagamentos(canhotos_entregues, canhotos_esperados);

-- Devolucoes table
CREATE TABLE IF NOT EXISTS devolucoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    escuteiro_id UUID REFERENCES escuteiros(id) ON DELETE CASCADE,
    bloco_id UUID REFERENCES blocos_rifas(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    motivo TEXT,
    data_devolucao TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_devolucoes_escuteiro ON devolucoes(escuteiro_id);
CREATE INDEX IF NOT EXISTS idx_devolucoes_bloco ON devolucoes(bloco_id);
CREATE INDEX IF NOT EXISTS idx_devolucoes_data ON devolucoes(data_devolucao);

-- Enable Row Level Security (RLS) - IMPORTANT FOR SECURITY
ALTER TABLE campanhas ENABLE ROW LEVEL SECURITY;
ALTER TABLE escuteiros ENABLE ROW LEVEL SECURITY;
ALTER TABLE blocos_rifas ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendas ENABLE ROW LEVEL SECURITY;
ALTER TABLE pagamentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE devolucoes ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users (adjust based on your security needs)
-- For development, you can use permissive policies. For production, restrict appropriately.

CREATE POLICY "Enable all for authenticated users" ON campanhas
    FOR ALL USING (true);

CREATE POLICY "Enable all for authenticated users" ON escuteiros
    FOR ALL USING (true);

CREATE POLICY "Enable all for authenticated users" ON blocos_rifas
    FOR ALL USING (true);

CREATE POLICY "Enable all for authenticated users" ON vendas
    FOR ALL USING (true);

CREATE POLICY "Enable all for authenticated users" ON pagamentos
    FOR ALL USING (true);

CREATE POLICY "Enable all for authenticated users" ON devolucoes
    FOR ALL USING (true);

-- Helpful views for reporting

-- View: Summary of sales by scout
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

-- View: Block status summary
CREATE OR REPLACE VIEW vw_blocos_status AS
SELECT 
    estado,
    COUNT(*) as quantidade,
    SUM(numero_final - numero_inicial + 1) as total_rifas
FROM blocos_rifas
GROUP BY estado;

"""

def create_tables_sql():
    """
    Returns the SQL commands to create all tables
    Use this in Supabase SQL Editor
    """
    return """
    -- Copy the SQL commands above and run them in Supabase SQL Editor
    -- This will create all necessary tables, indexes, and views
    """
