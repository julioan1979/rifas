# 📊 Setup da Base de Dados - Supabase

Este guia mostra como configurar todas as tabelas necessárias no Supabase.

## ⚡ Configuração Rápida

### 1. Aceder ao SQL Editor

1. Abra o seu projeto no [Supabase](https://app.supabase.com)
2. No menu lateral, clique em **SQL Editor**
3. Clique em **+ New Query**

### 2. Executar o SQL Completo

Copie e cole **TODO** o código SQL abaixo no editor e clique em **RUN** (ou F5):

```sql
-- ============================================
-- SISTEMA DE GESTÃO DE RIFAS - SETUP COMPLETO
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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
    nome TEXT NOT NULL,
    numero_inicial INTEGER NOT NULL,
    numero_final INTEGER NOT NULL,
    preco_unitario DECIMAL(10, 2) NOT NULL,
    escuteiro_id UUID REFERENCES escuteiros(id) ON DELETE SET NULL,
    data_atribuicao TIMESTAMP WITH TIME ZONE,
    estado TEXT DEFAULT 'disponivel' CHECK (estado IN ('disponivel', 'atribuido', 'vendido', 'devolvido')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT check_numeros CHECK (numero_final >= numero_inicial)
);

CREATE INDEX IF NOT EXISTS idx_blocos_rifas_escuteiro ON blocos_rifas(escuteiro_id);
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_estado ON blocos_rifas(estado);

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
ALTER TABLE escuteiros ENABLE ROW LEVEL SECURITY;
ALTER TABLE blocos_rifas ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendas ENABLE ROW LEVEL SECURITY;
ALTER TABLE pagamentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE devolucoes ENABLE ROW LEVEL SECURITY;

-- Políticas permissivas para desenvolvimento
-- ATENÇÃO: Para produção, ajuste estas políticas conforme necessário
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

-- ============================================
-- CONFIRMAÇÃO
-- ============================================
SELECT 'Setup concluído com sucesso! ✅' as status;
```

### 3. Verificar Resultados

Deve ver a mensagem: **"Setup concluído com sucesso! ✅"**

## ✅ Verificação das Tabelas

Para confirmar que tudo foi criado corretamente, execute:

```sql
-- Verificar tabelas criadas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

Deve ver:
- ✅ `blocos_rifas`
- ✅ `devolucoes`
- ✅ `escuteiros`
- ✅ `pagamentos`
- ✅ `vendas`

## 📊 Estrutura das Tabelas

### escuteiros
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | ID único (chave primária) |
| nome | TEXT | Nome do escuteiro |
| email | TEXT | Email (opcional) |
| telefone | TEXT | Telefone (opcional) |
| ativo | BOOLEAN | Escuteiro ativo? |
| created_at | TIMESTAMP | Data de criação |

### blocos_rifas
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | ID único |
| nome | TEXT | Nome do bloco |
| numero_inicial | INTEGER | Número inicial |
| numero_final | INTEGER | Número final |
| preco_unitario | DECIMAL | Preço por rifa |
| escuteiro_id | UUID | ID do escuteiro atribuído |
| data_atribuicao | TIMESTAMP | Data de atribuição |
| estado | TEXT | disponivel/atribuido/vendido/devolvido |
| created_at | TIMESTAMP | Data de criação |

### vendas
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | ID único |
| escuteiro_id | UUID | ID do escuteiro |
| bloco_id | UUID | ID do bloco |
| quantidade | INTEGER | Quantidade vendida |
| valor_total | DECIMAL | Valor total |
| data_venda | TIMESTAMP | Data da venda |
| observacoes | TEXT | Observações |
| created_at | TIMESTAMP | Data de criação |

### pagamentos
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | ID único |
| venda_id | UUID | ID da venda |
| valor_pago | DECIMAL | Valor pago |
| data_pagamento | TIMESTAMP | Data do pagamento |
| metodo_pagamento | TEXT | Método de pagamento |
| referencia | TEXT | Referência |
| observacoes | TEXT | Observações |
| created_at | TIMESTAMP | Data de criação |

### devolucoes
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | ID único |
| escuteiro_id | UUID | ID do escuteiro |
| bloco_id | UUID | ID do bloco |
| quantidade | INTEGER | Quantidade devolvida |
| motivo | TEXT | Motivo da devolução |
| data_devolucao | TIMESTAMP | Data da devolução |
| created_at | TIMESTAMP | Data de criação |

## 🔄 Adicionar Dados de Teste (Opcional)

Se quiser adicionar alguns dados de exemplo para testar:

```sql
-- Adicionar escuteiros de teste
INSERT INTO escuteiros (nome, email, telefone, ativo) VALUES
('João Silva', 'joao@example.com', '912345678', true),
('Maria Santos', 'maria@example.com', '913456789', true),
('Pedro Costa', 'pedro@example.com', '914567890', true);

-- Adicionar blocos de rifas de teste
INSERT INTO blocos_rifas (nome, numero_inicial, numero_final, preco_unitario, estado) VALUES
('Bloco A', 1, 100, 1.00, 'disponivel'),
('Bloco B', 101, 200, 1.00, 'disponivel'),
('Bloco C', 201, 300, 1.50, 'disponivel');

-- Verificar dados inseridos
SELECT * FROM escuteiros;
SELECT * FROM blocos_rifas;
```

## 🔒 Segurança em Produção

⚠️ **IMPORTANTE:** As políticas RLS atuais são permissivas para desenvolvimento.

Para produção, considere:

1. **Implementar autenticação de utilizadores**
2. **Restringir acessos por perfil** (admin, escuteiro, etc.)
3. **Criar políticas RLS específicas:**

```sql
-- Exemplo: Apenas utilizadores autenticados
DROP POLICY IF EXISTS "Enable read for authenticated" ON escuteiros;
CREATE POLICY "Enable read for authenticated" 
ON escuteiros FOR SELECT 
USING (auth.role() = 'authenticated');

-- Exemplo: Apenas admins podem inserir
DROP POLICY IF EXISTS "Enable insert for admins" ON escuteiros;
CREATE POLICY "Enable insert for admins" 
ON escuteiros FOR INSERT 
WITH CHECK (auth.jwt() ->> 'role' = 'admin');
```

## ❓ Problemas Comuns

### Erro: "permission denied for schema public"
**Solução:** Verifique se está a usar o SQL Editor com permissões de admin do projeto.

### Erro: "relation already exists"
**Solução:** As tabelas já existem. Para recriar, primeiro apague:
```sql
DROP TABLE IF EXISTS devolucoes CASCADE;
DROP TABLE IF EXISTS pagamentos CASCADE;
DROP TABLE IF EXISTS vendas CASCADE;
DROP TABLE IF EXISTS blocos_rifas CASCADE;
DROP TABLE IF EXISTS escuteiros CASCADE;
```

### Erro ao criar views
**Solução:** Certifique-se que todas as tabelas foram criadas primeiro.

## 📚 Próximos Passos

Após setup da base de dados:

1. ✅ Configure as credenciais na aplicação (`.env` ou Streamlit Secrets)
2. ✅ Execute `streamlit run app.py`
3. ✅ Comece a usar o sistema!

---

**📌 Nota:** Guarde este ficheiro para referência futura ou caso precise recriar a base de dados.
