# 🎫 Sistema de Gestão de Rifas dos Escuteiros

Sistema completo desenvolvido em **Streamlit** com backend **Supabase** para gerir rifas distribuídas aos escuteiros, incluindo gestão de escuteiros, blocos de rifas, vendas, pagamentos e devoluções.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.31+-red.svg)
![Supabase](https://img.shields.io/badge/supabase-enabled-green.svg)

## ✨ Funcionalidades

### 👥 Gestão de Escuteiros
- ➕ Adicionar, editar e remover escuteiros
- 📋 Listagem com filtros e pesquisa
- ✅ Controlo de escuteiros ativos/inativos
- 📧 Validação de emails e telefones

### 🎟️ Blocos de Rifas
- 📦 Criar e gerir blocos de rifas
- 🔢 Definir intervalos de números (inicial-final)
- 💰 Configurar preços unitários
- 👤 Atribuir blocos a escuteiros
- 📊 Controlo de estados (disponível, atribuído, vendido, devolvido)

### 💰 Vendas
- 📝 Registar vendas por escuteiro
- 📊 Cálculo automático de valores
- 📅 Histórico de vendas com filtros
- 📈 Estatísticas e relatórios

### 💳 Pagamentos
- 💵 Registar pagamentos recebidos
- 🔄 Múltiplos métodos de pagamento
- 💰 Controlo de saldos pendentes
- 📑 Referências e observações

### 🔄 Devoluções
- ↩️ Registar devoluções de rifas
- 📝 Motivos de devolução
- 📊 Estatísticas de devoluções

### 📊 Dashboard
- 📈 Visão geral com métricas principais
- 📊 Gráficos interativos (Plotly)
- 💶 Resumo financeiro
- 🎯 Análise de vendas por escuteiro
- 📉 Evolução temporal das vendas

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- Conta no [Supabase](https://supabase.com)
- Git (opcional)

### 1. Clonar o Repositório

```bash
git clone https://github.com/julioan1979/rifas.git
cd rifas
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar Supabase

#### 3.1 Criar Projeto no Supabase
1. Aceda a [supabase.com](https://supabase.com)
2. Crie um novo projeto
3. Aguarde a criação do projeto
4. Copie a **URL do projeto** e a **chave anon/public**

#### 3.2 Criar Tabelas na Base de Dados
1. No Supabase, aceda ao **SQL Editor**
2. Copie todo o conteúdo SQL do ficheiro `utils/database_schema.py`
3. Execute o SQL para criar todas as tabelas, índices e views

### 4. Configurar Credenciais

#### Opção A: Desenvolvimento Local (Ficheiro .env)

Crie um ficheiro `.env` na raiz do projeto:

```bash
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon_publica_aqui
```

#### Opção B: GitHub Codespaces / CI

Configure as variáveis de ambiente:

```bash
export SUPABASE_URL='https://seu-projeto.supabase.co'
export SUPABASE_KEY='sua_chave_anon_publica_aqui'
```

Ou adicione no GitHub:
1. Settings → Secrets and variables → Actions
2. New repository secret:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

#### Opção C: Streamlit Cloud (Deploy)

1. Aceda ao dashboard do Streamlit Cloud
2. Selecione a sua aplicação
3. Settings → Secrets
4. Adicione:

```toml
[supabase]
url = "https://seu-projeto.supabase.co"
key = "sua_chave_anon_publica_aqui"
```

### 5. Executar a Aplicação

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente em `http://localhost:8501`

## 🌐 Deploy no Streamlit Cloud

### Passo 1: Preparar o Repositório GitHub
1. Faça push do código para o GitHub
2. Certifique-se que os ficheiros estão na raiz:
   - `app.py`
   - `requirements.txt`
   - `utils/`
   - `pages/`

### Passo 2: Deploy
1. Aceda a [share.streamlit.io](https://share.streamlit.io)
2. Faça login com GitHub
3. Clique em **"New app"**
4. Selecione:
   - Repository: `julioan1979/rifas`
   - Branch: `main`
   - Main file path: `app.py`
5. Clique em **Advanced settings**
6. Adicione as secrets (ver secção "Opção C" acima)
7. Clique em **Deploy!**

## 📁 Estrutura do Projeto

```
rifas/
├── app.py                          # Página principal com dashboard
├── requirements.txt                # Dependências Python
├── README.md                       # Este ficheiro
├── LICENSE                         # Licença do projeto
├── .streamlit/
│   └── config.toml                # Configuração do Streamlit
├── utils/
│   ├── supabase_client.py         # Cliente Supabase com auto-detecção
│   └── database_schema.py         # Schema SQL completo
└── pages/
    ├── 1_👥_Escuteiros.py         # Gestão de escuteiros
    ├── 2_🎟️_Blocos_de_Rifas.py  # Gestão de blocos
    ├── 3_💰_Vendas.py             # Gestão de vendas
    ├── 4_💳_Pagamentos.py         # Gestão de pagamentos
    └── 5_🔄_Devoluções.py         # Gestão de devoluções
```

## 🔒 Segurança

### Gestão de Credenciais
✅ **Nunca** adicione credenciais diretamente no código  
✅ Use `st.secrets` no Streamlit Cloud  
✅ Use variáveis de ambiente ou ficheiro `.env` localmente  
✅ Adicione `.env` ao `.gitignore`  

### Row Level Security (RLS)
O schema SQL inclui políticas RLS básicas. Para produção:
1. Configure políticas mais restritivas no Supabase
2. Implemente autenticação de utilizadores
3. Restrinja acessos por perfil

## 📊 Base de Dados

### Tabelas Principais

| Tabela | Descrição |
|--------|-----------|
| `escuteiros` | Dados dos escuteiros |
| `blocos_rifas` | Blocos de rifas |
| `vendas` | Registo de vendas |
| `pagamentos` | Pagamentos recebidos |
| `devolucoes` | Devoluções de rifas |

### Views Disponíveis
- `vw_vendas_por_escuteiro` - Resumo de vendas por escuteiro
- `vw_blocos_status` - Estado dos blocos de rifas

## 🛠️ Desenvolvimento

### Adicionar Nova Página
1. Crie um ficheiro em `pages/` com o formato: `N_🔸_Nome.py`
2. O Streamlit detecta automaticamente
3. Use o template das páginas existentes

### Personalizar Tema
Edite `.streamlit/config.toml`:
- `primaryColor` - Cor principal
- `backgroundColor` - Cor de fundo
- `secondaryBackgroundColor` - Cor secundária
- `textColor` - Cor do texto

## 📝 Como Usar

### 1. Adicionar Escuteiros
1. Aceda à página **👥 Escuteiros**
2. No separador **➕ Adicionar**
3. Preencha nome (obrigatório), email e telefone (opcionais)
4. Clique em **Adicionar Escuteiro**

### 2. Criar Blocos de Rifas
1. Aceda à página **🎟️ Blocos de Rifas**
2. No separador **➕ Adicionar**
3. Defina nome, números (inicial-final) e preço
4. Opcionalmente, atribua a um escuteiro
5. Clique em **Criar Bloco de Rifas**

### 3. Registar Vendas
1. Aceda à página **💰 Vendas**
2. No separador **➕ Registar Venda**
3. Selecione escuteiro e bloco
4. Digite a quantidade vendida
5. O valor é calculado automaticamente
6. Clique em **Registar Venda**

### 4. Registar Pagamentos
1. Aceda à página **💳 Pagamentos**
2. No separador **➕ Registar Pagamento**
3. Selecione a venda
4. Digite o valor pago
5. Selecione o método de pagamento
6. Clique em **Registar Pagamento**

## 🐛 Resolução de Problemas

### Erro: "Credenciais não encontradas"
- Verifique se configurou `SUPABASE_URL` e `SUPABASE_KEY`
- No Streamlit Cloud, verifique as Secrets
- Localmente, verifique o ficheiro `.env`

### Erro: "Tabela não encontrada"
- Execute o SQL completo do ficheiro `database_schema.py`
- Verifique a consola do Supabase para erros

### Aplicação não carrega
- Verifique `requirements.txt`
- Reinstale as dependências: `pip install -r requirements.txt --upgrade`
- Limpe cache do Streamlit: `streamlit cache clear`

## 📧 Suporte

Para questões ou sugestões:
1. Abra uma issue no GitHub
2. Contacte o administrador do sistema

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## 🙏 Créditos

Desenvolvido para a gestão de rifas dos Escuteiros.

Tecnologias utilizadas:
- [Streamlit](https://streamlit.io) - Framework de aplicações web
- [Supabase](https://supabase.com) - Backend e base de dados
- [Plotly](https://plotly.com) - Gráficos interativos
- [Pandas](https://pandas.pydata.org) - Análise de dados

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**
