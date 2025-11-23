# 📅 Sistema de Campanhas - Guia Completo

## 🎯 O que mudou?

O sistema agora suporta **múltiplas campanhas de rifas** ao longo do tempo!

### ✨ Novas Funcionalidades:

1. **Tabela de Campanhas**: Crie e gira diferentes campanhas (Natal2025, Páscoa2026, etc.)
2. **Campanha Ativa**: Apenas uma campanha pode estar ativa por vez
3. **Dados Isolados**: Cada campanha tem seus próprios blocos, vendas e pagamentos
4. **Histórico Completo**: Mantenha o histórico de todas as campanhas anteriores
5. **Nova Página**: Interface dedicada para gestão de campanhas

---

## 📋 Passo a Passo para Configurar

### 1️⃣ Executar SQL no Supabase

Copie e execute o seguinte SQL no **Supabase SQL Editor**:

```sql
-- 1. Criar tabela de campanhas
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

ALTER TABLE campanhas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all for authenticated users" ON campanhas
    FOR ALL USING (true);

-- 2. Adicionar coluna campanha_id à tabela blocos_rifas
ALTER TABLE blocos_rifas 
ADD COLUMN IF NOT EXISTS campanha_id UUID REFERENCES campanhas(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_blocos_rifas_campanha ON blocos_rifas(campanha_id);

-- 3. Criar campanha Natal2025 e associar blocos existentes
INSERT INTO campanhas (nome, descricao, data_inicio, data_fim, ativa)
VALUES ('Natal2025', 'Campanha de rifas do Natal 2025', '2025-11-01', '2025-12-31', true)
ON CONFLICT (nome) DO NOTHING;

-- 4. Associar todos os blocos existentes à campanha Natal2025
UPDATE blocos_rifas
SET campanha_id = (SELECT id FROM campanhas WHERE nome = 'Natal2025')
WHERE campanha_id IS NULL;

-- 5. Verificar resultado
SELECT 
    c.nome as campanha,
    c.ativa,
    COUNT(b.id) as total_blocos,
    SUM(b.numero_final - b.numero_inicial + 1) as total_rifas
FROM campanhas c
LEFT JOIN blocos_rifas b ON c.id = b.campanha_id
GROUP BY c.id, c.nome, c.ativa
ORDER BY c.created_at DESC;
```

### 2️⃣ Reimportar Dados (Opcional)

Se quiser começar do zero com a nova estrutura:

```bash
python importacao_completa.py
```

Isto irá:
- ✅ Limpar todas as tabelas
- ✅ Criar a campanha "Natal2025"
- ✅ Importar 65 escuteiros
- ✅ Importar 99 blocos (990 rifas)
- ✅ Importar vendas e pagamentos

### 3️⃣ Recarregar Aplicação

Simplesmente **recarregue a página** no browser!

---

## 🎯 Como Usar o Sistema de Campanhas

### Página "📅 Campanhas"

Nova página no menu lateral com 3 abas:

#### 📋 **Aba Lista**
- Visualizar todas as campanhas
- Ver estatísticas de cada campanha:
  - Total de blocos
  - Total de rifas
  - Blocos vendidos
  - Datas de início e fim
  - Status (ativa ou não)

#### ➕ **Aba Adicionar**
- Criar nova campanha
- Campos:
  - Nome (ex: "Pascoa2026", "Natal2026")
  - Descrição
  - Data de início
  - Data de fim
  - Marcar como ativa

#### ✏️ **Aba Editar/Eliminar**
- Editar dados de campanha existente
- Ativar/desativar campanha
- Eliminar campanha (⚠️ elimina TODOS os dados associados)

---

## 🔄 Fluxo de Trabalho com Campanhas

### Cenário 1: Nova Campanha (Páscoa 2026)

1. Aceder página **"📅 Campanhas"**
2. Aba **"➕ Adicionar"**
3. Preencher:
   - Nome: `Pascoa2026`
   - Descrição: `Campanha de rifas da Páscoa 2026`
   - Data início: `01/03/2026`
   - Data fim: `30/04/2026`
   - ✅ Marcar como **Ativa**
4. Clicar **"✅ Criar Campanha"**

**Resultado**: 
- Natal2025 fica automaticamente desativada
- Pascoa2026 fica ativa
- Dashboard e todas as páginas mostram dados da Pascoa2026
- Dados do Natal2025 ficam preservados no histórico

### Cenário 2: Ver Dados de Campanha Anterior

1. Página **"📅 Campanhas"**
2. Aba **"📋 Lista"**
3. Ver estatísticas de todas as campanhas (incluindo inativas)

---

## 📊 Impacto nas Páginas Existentes

### 🏠 **Dashboard (app.py)**
- ✅ Mostra nome da campanha ativa no topo
- ✅ Filtra todos os dados pela campanha ativa
- ✅ Métricas e gráficos apenas da campanha ativa

### 🎟️ **Blocos de Rifas**
- ✅ Novos blocos são criados para campanha ativa
- ✅ Lista mostra apenas blocos da campanha ativa

### 💰 **Vendas**
- ✅ Vendas registadas apenas em blocos da campanha ativa
- ✅ Histórico filtrado por campanha

### 💳 **Pagamentos**
- ✅ Pagamentos associados a vendas da campanha ativa

---

## ⚠️ Avisos Importantes

### 🔒 Campanha Ativa Única
- Apenas **uma campanha pode estar ativa** por vez
- Ao ativar uma nova, a anterior é desativada automaticamente

### 🗑️ Eliminação em Cascata
- Ao eliminar uma campanha, **TODOS os dados associados são eliminados**:
  - Blocos de rifas
  - Vendas
  - Pagamentos
  - Devoluções
- ⚠️ **Esta ação é irreversível!**

### 📦 Dados Antigos Preservados
- Campanhas desativadas mantêm todos os seus dados
- Pode consultar histórico na página de Campanhas
- Para ver dados antigos, basta reativar a campanha anterior

---

## 🚀 Próximos Passos Sugeridos

1. ✅ **Executar SQL** no Supabase
2. ✅ **Reimportar dados** (opcional)
3. ✅ **Testar** criação de nova campanha
4. 📊 **Explorar** página de Campanhas
5. 🎯 **Criar** próxima campanha quando necessário

---

## 📞 Dúvidas?

O sistema está pronto para gerir múltiplas campanhas ao longo dos anos! 🎉

**Estrutura atual:**
- ✅ Campanhas independentes
- ✅ Histórico completo
- ✅ Filtragem automática
- ✅ Interface intuitiva
