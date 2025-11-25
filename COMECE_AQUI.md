# 🎯 INSTRUÇÕES RÁPIDAS - COMEÇAR DO ZERO

## ⚡ STATUS ATUAL

✅ **Credenciais Configuradas**: Supabase conectado  
❌ **Tabelas Criadas**: NÃO (precisa executar SQL)  
✅ **Aplicação Pronta**: Código validado e funcional  

---

## 🚨 AÇÃO NECESSÁRIA: CRIAR TABELAS NO SUPABASE

Você apagou todas as tabelas. Para recomeçar, execute o SQL completo:

### 📝 PASSO A PASSO RÁPIDO

#### 1️⃣ Abrir o SQL no Supabase

1. Vá em: https://supabase.com/dashboard
2. Selecione seu projeto
3. Clique em **"SQL Editor"** no menu lateral
4. Clique em **"New query"**

#### 2️⃣ Executar o Script

1. Abra o arquivo: **`COMPLETE_SCHEMA.sql`**
2. Selecione TUDO (Ctrl+A)
3. Copie (Ctrl+C)
4. Cole no SQL Editor do Supabase
5. Clique em **"Run"** (ou Ctrl+Enter)

#### 3️⃣ Verificar Criação

Você deve ver:
```
✅ Schema criado com sucesso!

📊 Resumo:
  - 6 tabelas criadas
  - Índices otimizados
  - RLS ativado
  - Views para relatórios
  - Trigger automático para estado de blocos
```

#### 4️⃣ Executar Aplicação

```bash
streamlit run app.py
```

---

## 📊 O QUE O SQL CRIA

### 6 Tabelas Principais
- `campanhas` - Campanhas de rifas
- `escuteiros` - Escuteiros vendedores  
- `blocos_rifas` - Blocos de rifas numeradas
- `vendas` - Vendas (legado, compatibilidade)
- `pagamentos` - Pagamentos e canhotos ⭐
- `devolucoes` - Devoluções de rifas

### 4 Views Automáticas
- `vw_vendas_por_escuteiro` - Vendas por escuteiro
- `vw_blocos_status` - Status dos blocos
- `vw_pagamentos_por_bloco` - Pagamentos detalhados
- `vw_canhotos_pendentes` - Canhotos não entregues

### Funcionalidades Automáticas
- ✅ Índices para queries rápidas
- ✅ Trigger para atualizar estado de blocos
- ✅ Row Level Security (RLS)
- ✅ Constraints de integridade

---

## 🎮 APÓS CRIAR AS TABELAS

### 1. Criar Campanha
```
Página: 📅 Campanhas
→ Tab: ➕ Adicionar Campanha
→ Nome: Natal2025
→ Datas: 01/11/2025 - 31/12/2025
→ ✅ Marcar como ativa
```

### 2. Criar Blocos
```
Página: 📅 Campanhas
→ Tab: 🎟️ Criar Blocos de Rifas
→ Campanha: Natal2025
→ Total: 1000 rifas
→ Por bloco: 10 rifas
→ Preço: 1.00 €
→ Criar (100 blocos serão criados)
```

### 3. Adicionar Escuteiros
```
Página: 👥 Escuteiros
→ Tab: ➕ Adicionar
→ Adicione seus escuteiros
```

### 4. Atribuir Blocos
```
Página: 🎟️ Blocos de Rifas
→ Tab: ➕ Atribuir a Escuteiro
→ Selecione bloco e escuteiro
```

### 5. Registar Pagamentos
```
Página: 💳 Pagamentos
→ Tab: ➕ Registar Pagamento
→ Selecione bloco
→ Quantidade vendida
→ Valor pago
→ Canhotos entregues
```

---

## 📚 DOCUMENTAÇÃO COMPLETA

- **`COMPLETE_SCHEMA.sql`** - SQL completo ⭐
- **`SETUP_COMPLETO.md`** - Guia detalhado
- **`VALIDACAO_COMPLETA.md`** - Status do sistema
- **`database_schema.py`** - Documentação técnica

---

## 🆘 PROBLEMAS?

### Erro ao executar SQL
- Certifique-se de copiar TODO o arquivo
- Execute no SQL Editor do Supabase
- Não execute linha por linha

### Aplicação não conecta
- Verifique arquivo `.env`
- Confirme SUPABASE_URL e SUPABASE_KEY
- Reinicie a aplicação

### Tabela não encontrada
- Execute o COMPLETE_SCHEMA.sql primeiro
- Aguarde alguns segundos após execução
- Recarregue a página da aplicação

---

## ✅ ESTÁ PRONTO!

Depois de executar o SQL, o sistema estará 100% funcional! 🎉
