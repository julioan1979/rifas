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

### 💰 Vendas e Pagamentos
- 📝 **Vendas:** Registro de vendas por bloco
- 💳 **Pagamentos:** Controle de pagamentos das vendas
- 🔄 **Devoluções:** Gestão de devoluções
- 📊 Relatórios consolidados por escuteiro e campanha

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
│   ├── 2_🎟️_Blocos_de_Rifas.py   # Gestão de blocos
│   ├── 3_💰_Vendas.py             # Registro de vendas
│   ├── 4_💳_Pagamentos.py         # Pagamentos
│   ├── 5_🔄_Devoluções.py         # Devoluções
│   └── 7_📅_Campanhas.py          # Gestão de campanhas
├── utils/
│   ├── supabase_client.py         # Cliente Supabase
│   └── database_schema.py         # Schema SQL
├── scripts/                        # Scripts utilitários
│   ├── setup_completo_supabase.sql           # Setup completo DB
│   ├── verificar_e_ajustar_supabase.py       # Verificação
│   └── limpar_campos_extras_blocos.sql       # Limpeza
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

### 4. Registar Vendas e Pagamentos
- **Tab 3 - Vendas:** Registar vendas por bloco e escuteiro
- **Tab 4 - Pagamentos:** Registar pagamentos das vendas
- Status consolidado por escuteiro e campanha

## 🗄️ Base de Dados

### Tabelas Principais
- `campanhas` - Campanhas de rifas
- `escuteiros` - Cadastro de escuteiros
- `blocos_rifas` - Blocos de rifas (com campanha_id e seccao)
- `vendas` - Registro de vendas por bloco
- `pagamentos` - Pagamentos das vendas
- `devolucoes` - Devoluções de blocos

### Campos Importantes
- `blocos_rifas.campanha_id` - Relacionamento com campanha
- `blocos_rifas.seccao` - Secção do bloco (Lobitos, Exploradores, etc)
- `blocos_rifas.escuteiro_id` - Escuteiro atribuído ao bloco
- `blocos_rifas.estado` - Estado: disponivel, atribuido, vendido, devolvido

## 🛠️ Scripts Utilitários

### Verificar Estrutura do Supabase
```bash
python scripts/verificar_e_ajustar_supabase.py
```
✅ Verifica todas as tabelas e campos
✅ Identifica campos extras ou faltantes
✅ Gera SQL de ajuste se necessário

### Executar Setup Completo
No Supabase SQL Editor, execute:
```bash
# Conteúdo do arquivo: scripts/setup_completo_supabase.sql
```
✅ Cria todas as tabelas
✅ Configura índices e políticas RLS
✅ Cria views para relatórios

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
- Escuteiros únicos (sem duplicados)

### Gestão por Campanha
- Múltiplas campanhas simultâneas
- Filtros por campanha em todas as páginas
- Relatórios consolidados por campanha
- Dashboard com métricas por campanha

---

**Desenvolvido com ❤️ para Escuteiros**
