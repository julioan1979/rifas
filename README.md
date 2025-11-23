# 🎫 Sistema de Gestão de Rifas dos Escuteiros

Aplicação web desenvolvida com Streamlit para gerir rifas dos escuteiros, com base de dados Supabase.

## 📋 Funcionalidades

- **👥 Gestão de Escuteiros**: Registar e gerir os escuteiros que vendem rifas
- **🎟️ Gestão de Blocos de Rifas**: Criar e gerir blocos de rifas com numeração e preços
- **💰 Gestão de Vendas**: Registar vendas de rifas por escuteiro
- **💳 Gestão de Pagamentos**: Controlar pagamentos recebidos pelas vendas

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- Conta no [Supabase](https://supabase.com/)

### 1. Clonar o Repositório

```bash
git clone https://github.com/julioan1979/rifas.git
cd rifas
```

### 2. Criar Ambiente Virtual (Recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Supabase

#### 4.1. Criar Projeto no Supabase

1. Aceda a [https://app.supabase.com/](https://app.supabase.com/)
2. Crie um novo projeto
3. Aguarde a criação do projeto

#### 4.2. Criar Tabelas na Base de Dados

No editor SQL do Supabase (`SQL Editor`), execute o seguinte script:

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

#### 4.3. Obter Credenciais do Supabase

1. No painel do Supabase, vá a `Settings` > `API`
2. Copie o `Project URL` e o `anon public` key

#### 4.4. Configurar Variáveis de Ambiente

Crie um ficheiro `.env` na raiz do projeto:

```bash
cp .env.example .env
```

Edite o ficheiro `.env` e adicione as suas credenciais:

```
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anon-aqui
```

**Alternativa:** Pode configurar usando Streamlit Secrets:

Crie o ficheiro `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://seu-projeto.supabase.co"
SUPABASE_KEY = "sua-chave-anon-aqui"
```

### 5. Executar a Aplicação

```bash
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`

## 📖 Como Usar

### Fluxo de Trabalho Recomendado

1. **Registar Escuteiros**: Comece por adicionar os escuteiros na página "👥 Escuteiros"
2. **Criar Blocos de Rifas**: Crie blocos de rifas na página "🎟️ Blocos de Rifas"
3. **Registar Vendas**: Quando um escuteiro vender rifas, registe na página "💰 Vendas"
4. **Controlar Pagamentos**: Registe os pagamentos recebidos na página "💳 Pagamentos"

### Páginas Disponíveis

#### Página Principal
- Dashboard com estatísticas gerais
- Visão geral do sistema

#### 👥 Escuteiros
- Listar todos os escuteiros
- Adicionar novos escuteiros
- Editar ou eliminar escuteiros existentes

#### 🎟️ Blocos de Rifas
- Listar todos os blocos de rifas
- Criar novos blocos com numeração e preço
- Editar ou eliminar blocos

#### 💰 Vendas
- Listar todas as vendas
- Registar nova venda (escuteiro + bloco + quantidade)
- Editar ou eliminar vendas
- Ver estatísticas de vendas

#### 💳 Pagamentos
- Listar todos os pagamentos
- Registar pagamentos recebidos
- Acompanhar saldo pendente de cada venda
- Editar ou eliminar pagamentos

## 🛠️ Estrutura do Projeto

```
rifas/
├── app.py                          # Página principal da aplicação
├── pages/                          # Páginas do Streamlit
│   ├── 1_👥_Escuteiros.py         # Gestão de escuteiros
│   ├── 2_🎟️_Blocos_de_Rifas.py   # Gestão de blocos de rifas
│   ├── 3_💰_Vendas.py             # Gestão de vendas
│   └── 4_💳_Pagamentos.py         # Gestão de pagamentos
├── utils/                          # Utilitários
│   ├── supabase_client.py         # Cliente Supabase
│   └── database_schema.py         # Documentação do schema
├── requirements.txt                # Dependências Python
├── .env.example                    # Exemplo de configuração
├── .gitignore                      # Ficheiros a ignorar
└── README.md                       # Este ficheiro
```

## 📦 Dependências

- **streamlit**: Framework web para a aplicação
- **supabase**: Cliente Python para Supabase
- **python-dotenv**: Gestão de variáveis de ambiente
- **pandas**: Manipulação de dados

## 🔒 Segurança

- Nunca partilhe o ficheiro `.env` ou as suas chaves de API
- O ficheiro `.env` está incluído no `.gitignore`
- Use as chaves `anon` do Supabase, não as chaves `service_role`
- Configure Row Level Security (RLS) no Supabase para produção

## 🤝 Contribuir

Contribuições são bem-vindas! Por favor:

1. Faça fork do projeto
2. Crie uma branch para a sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit as suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença especificada no ficheiro LICENSE.

## 📧 Suporte

Para questões ou suporte, por favor abra uma issue no GitHub.

---

**Desenvolvido para a gestão de rifas dos escuteiros** 🎯
