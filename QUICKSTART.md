# Quick Start Guide - Sistema de Gestão de Rifas

## 🚀 Como começar rapidamente

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Supabase

1. **Criar conta no Supabase**: https://supabase.com/
2. **Criar novo projeto** no dashboard do Supabase
3. **Executar o script SQL** abaixo no SQL Editor do Supabase:

```sql
-- Tabela de Escuteiros
CREATE TABLE escuteiros (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    email TEXT,
    telefone TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Blocos de Rifas
CREATE TABLE blocos_rifas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    numero_inicial INTEGER NOT NULL,
    numero_final INTEGER NOT NULL,
    preco_unitario DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Vendas
CREATE TABLE vendas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    escuteiro_id UUID REFERENCES escuteiros(id),
    bloco_id UUID REFERENCES blocos_rifas(id),
    quantidade INTEGER NOT NULL,
    valor_total DECIMAL(10, 2) NOT NULL,
    data_venda TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Pagamentos
CREATE TABLE pagamentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venda_id UUID REFERENCES vendas(id),
    valor_pago DECIMAL(10, 2) NOT NULL,
    data_pagamento TIMESTAMP DEFAULT NOW(),
    metodo_pagamento TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

4. **Obter credenciais**:
   - Vá em Settings > API
   - Copie `Project URL` e `anon public` key

### 3. Configurar Variáveis de Ambiente

Copie o ficheiro de exemplo:
```bash
cp .env.example .env
```

Edite `.env` e adicione suas credenciais:
```
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anon-aqui
```

### 4. Executar a Aplicação

```bash
streamlit run app.py
```

Acesse: http://localhost:8501

## 📋 Fluxo de Uso Recomendado

1. **Adicionar Escuteiros** → Página "👥 Escuteiros"
2. **Criar Blocos de Rifas** → Página "🎟️ Blocos de Rifas"
3. **Registar Vendas** → Página "💰 Vendas"
4. **Controlar Pagamentos** → Página "💳 Pagamentos"

> **Nota (2025-11-24):** O fluxo oficial de pagamentos passou a ser **Escuteiro → Organização**. As páginas relacionadas com pagamentos comprador→escuteiro foram descontinuadas temporariamente; consulte `docs/MIGRATION_PAYMENTS.md` para o procedimento de migração e consolidação.

## 🎯 Funcionalidades Principais

- ✅ Gestão completa de escuteiros
- ✅ Criação e gestão de blocos de rifas
- ✅ Registro de vendas com cálculo automático
- ✅ Controlo de pagamentos e saldos
- ✅ Estatísticas em tempo real
- ✅ Interface intuitiva e responsiva

## ⚠️ Notas Importantes

- O ficheiro `.env` **não deve** ser commitado ao Git (já está no .gitignore)
- Use as chaves `anon` do Supabase, não as chaves `service_role`
- Configure Row Level Security (RLS) no Supabase para ambientes de produção

## 🆘 Precisa de Ajuda?

Consulte o README.md completo para documentação detalhada.
