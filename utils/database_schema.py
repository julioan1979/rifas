"""
Database schema documentation for the raffle management system

The database should have the following tables in Supabase:

1. escuteiros (scouts)
   - id: UUID (primary key)
   - nome: TEXT (scout name)
   - email: TEXT (optional)
   - telefone: TEXT (optional)
   - created_at: TIMESTAMP

2. blocos_rifas (raffle blocks)
   - id: UUID (primary key)
   - nome: TEXT (block name)
   - numero_inicial: INTEGER (starting number)
   - numero_final: INTEGER (ending number)
   - preco_unitario: DECIMAL (price per ticket)
   - created_at: TIMESTAMP

3. vendas (sales)
   - id: UUID (primary key)
   - escuteiro_id: UUID (foreign key to escuteiros)
   - bloco_id: UUID (foreign key to blocos_rifas)
   - quantidade: INTEGER (number of tickets sold)
   - valor_total: DECIMAL (total value)
   - data_venda: TIMESTAMP
   - created_at: TIMESTAMP

4. pagamentos (payments)
   - id: UUID (primary key)
   - venda_id: UUID (foreign key to vendas)
   - valor_pago: DECIMAL (amount paid)
   - data_pagamento: TIMESTAMP
   - metodo_pagamento: TEXT (payment method)
   - created_at: TIMESTAMP

SQL to create these tables:

-- Escuteiros table
CREATE TABLE escuteiros (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    email TEXT,
    telefone TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Blocos de rifas table
CREATE TABLE blocos_rifas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    numero_inicial INTEGER NOT NULL,
    numero_final INTEGER NOT NULL,
    preco_unitario DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vendas table
CREATE TABLE vendas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    escuteiro_id UUID REFERENCES escuteiros(id),
    bloco_id UUID REFERENCES blocos_rifas(id),
    quantidade INTEGER NOT NULL,
    valor_total DECIMAL(10, 2) NOT NULL,
    data_venda TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Pagamentos table
CREATE TABLE pagamentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venda_id UUID REFERENCES vendas(id),
    valor_pago DECIMAL(10, 2) NOT NULL,
    data_pagamento TIMESTAMP DEFAULT NOW(),
    metodo_pagamento TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
"""
