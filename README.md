# 🎫 Sistema de Gestão de Rifas dos Escuteiros

Sistema completo desenvolvido em **Streamlit** com backend **Supabase** para gerir campanhas de rifas, incluindo controle financeiro completo e gestão de irmãos.

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.31+-red.svg)
![Supabase](https://img.shields.io/badge/supabase-enabled-green.svg)

## ✨ Funcionalidades

### 📅 Gestão de Campanhas
- ✅ Múltiplas campanhas simultâneas
- 📦 Criação automática de blocos ao criar campanha
- 🔄 Ativar/desativar campanhas
- 📊 Filtros por campanha em todas as páginas

### 👥 Gestão de Escuteiros  
- ➕ Adicionar escuteiros únicos (sem duplicados)
- 📋 Organização por secções (Lobitos, Exploradores, Pioneiros, Caminheiros, CPP)
- 👨‍👩‍👧‍👦 Sistema de identificação de irmãos
- ✅ Controlo de escuteiros ativos/inativos

### ��️ Blocos de Rifas (Sistema Avançado)
- 📦 **Criação automática** ao criar campanha
- 🏷️ **Reserva por secção** (sem atribuição específica)
- 👤 **Atribuição individual** com prevenção de duplicação
- 👨‍👩‍👧‍👦 **Atribuição para irmãos** com divisão automática
- 🔒 Prevenção de reatribuição de blocos já atribuídos
- 📊 3 tabs: Lista, Reservar por Secção, Atribuir a Escuteiro

### 💵 Controle Financeiro Completo
- 💰 **Pagamentos:** Escuteiro → Organização
- 📋 **Canhotos:** Controle de devolução
- 📊 Dashboard com status visual
- ✅ Rastreamento individual por bloco
- 📅 Datas de pagamento e devolução

## 🚀 Deploy no Streamlit Cloud

### Passo 1: Configurar Supabase
1. Crie projeto em [supabase.com](https://supabase.com)
2. Execute SQL em `SETUP_DATABASE.md` no SQL Editor
3. Copie URL e chave do projeto

### Passo 2: Deploy
1. Aceda a [share.streamlit.io](https://share.streamlit.io)
2. Faça login com GitHub
3. Clique em **"New app"**
4. Configure:
   - Repository: `julioan1979/rifas`
   - Branch: `main`
   - Main file: `app.py`
5. Em **Advanced settings → Secrets**, adicione:
   ```toml
   SUPABASE_URL = "sua_url_supabase"
   SUPABASE_KEY = "sua_chave_supabase"
   ```
6. Clique em **Deploy**

## 🖥️ Desenvolvimento Local

```bash
# Clone o repositório
git clone https://github.com/julioan1979/rifas.git
cd rifas

# Instale as dependências
pip install -r requirements.txt

# Configure as credenciais
cp .env.example .env
# Edite .env com suas credenciais Supabase

# Execute a aplicação
streamlit run app.py
```

## 📁 Estrutura do Projeto

```
rifas/
├── app.py                          # Dashboard principal
├── requirements.txt                # Dependências
├── pages/                          # Páginas da aplicação
│   ├── 1_👥_Escuteiros.py         # Gestão de escuteiros
│   ├── 2_🎟️_Blocos_de_Rifas.py   # Gestão de blocos (3 tabs)
│   ├── 3_💰_Vendas.py             # Registro de vendas
│   ├── 4_💳_Pagamentos.py         # Pagamentos
│   ├── 5_🔄_Devoluções.py         # Devoluções
│   ├── 6_💵_Controle_Escuteiros.py # Controle financeiro
│   └── 7_📅_Campanhas.py          # Gestão de campanhas
├── utils/
│   ├── supabase_client.py         # Cliente Supabase
│   └── database_schema.py         # Schema SQL
├── scripts/                        # Scripts utilitários
│   ├── limpar_base_dados.py       # Limpeza da BD
│   └── importar_natal_2025_corrigido.py # Importação
└── .streamlit/
    └── config.toml                 # Configuração
```

## 📊 Fluxo de Trabalho

### 1. Criar Campanha
- Aceda a **📅 Campanhas**
- Defina nome, datas, preço por rifa, total de rifas
- Sistema cria blocos automaticamente

### 2. Reservar/Atribuir Blocos
- Aceda a **🎟️ Blocos de Rifas**
- **Tab 2:** Reservar por secção (sem escuteiro específico)
- **Tab 3:** Atribuir individual ou para irmãos

### 3. Escuteiros Vendem Rifas
- Escuteiros vendem rifas aos compradores
- Preenchem canhotos com dados do comprador

### 4. Registar Pagamento e Canhotos

### Nota Importante (2025-11-24)
- Fluxo oficial de pagamentos do sistema agora é: **Escuteiro → Organização**.
- Os registos do fluxo "comprador → escuteiro" foram considerados inadequados para o nosso processo e foram arquivados para auditoria; não são usados como fonte ativa.
- Operadores devem registar apenas a entrega de dinheiro pelo escuteiro e a devolução dos canhotos (campos em `blocos_rifas`).
- As páginas e scripts que registam pagamentos de comprador→escuteiro foram descontinuados: consulte `docs/MIGRATION_PAYMENTS.md` e `scripts/consolidar_pagamentos_para_blocos.sql` para o procedimento de consolidação e migração.

- Status visual: ✅ Pago, ⏳ Pendente, ❌ Em falta

## 🗄️ Base de Dados

### Tabelas Principais
- `campanhas` - Campanhas de rifas
- `escuteiros` - Cadastro de escuteiros
- `blocos_rifas` - Blocos com controle completo
- `vendas` - Registro de vendas
- `pagamentos` - Pagamentos
- `devolucoes` - Devoluções

### Colunas de Controle (blocos_rifas)
- `valor_a_pagar`, `valor_pago` - Controle financeiro
- `rifas_vendidas`, `canhotos_devolvidos` - Status
- `data_pagamento`, `data_devolucao_canhotos` - Datas
- `observacoes_pagamento`, `observacoes_canhotos` - Notas

## 🛠️ Scripts Utilitários

### Limpar Base de Dados
```bash
python scripts/limpar_base_dados.py
```
⚠️ **ATENÇÃO:** Apaga todos os dados!

### Importar Dados
```bash
python scripts/importar_natal_2025_corrigido.py
```
✅ Importa escuteiros únicos, sem duplicados
✅ Identifica relações de irmãos
✅ Cria blocos e atribuições

## 🔧 Tecnologias

- **Frontend:** Streamlit 1.31.0+
- **Backend:** Supabase (PostgreSQL)
- **Python:** 3.12+
- **Bibliotecas:** Pandas 2.2.0, Plotly 5.18.0

## 📄 Licença

MIT License - Ver arquivo `LICENSE`

## 🎯 Funcionalidades Avançadas

### Sistema de Irmãos
- Radio button: Individual vs Irmãos
- Divisão automática de blocos
- Primeiro irmão recebe rifas extras (se ímpar)
- Nomes de todos os irmãos nos blocos criados

### Prevenção de Duplicação
- Filtro `.is_('escuteiro_id', 'null')` mostra apenas blocos não atribuídos
- Impossível reatribuir bloco já atribuído
- Escuteiros únicos na importação

### Controle Completo
- Pagamento: Escuteiro → Organização
- Canhotos: Rifas vendidas devolvidas
- Status visual em tempo real
- Dashboard com métricas consolidadas

---

**Desenvolvido com ❤️ para Escuteiros**
