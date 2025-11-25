# 🎯 GUIA COMPLETO DE CONFIGURAÇÃO DO ZERO

Este guia irá configurar todo o sistema de gestão de rifas do zero, desde a criação do banco de dados até a primeira execução.

---

## 📋 PRÉ-REQUISITOS

Antes de começar, certifique-se de ter:

- ✅ Uma conta no [Supabase](https://supabase.com) (gratuita)
- ✅ Python 3.8+ instalado
- ✅ Terminal com acesso ao Python/pip

---

## 🚀 PASSO 1: CRIAR PROJETO NO SUPABASE

### 1.1 Criar novo projeto

1. Acesse [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Clique em **"New Project"**
3. Preencha os dados:
   - **Name**: `rifas-escuteiros` (ou nome de sua preferência)
   - **Database Password**: Escolha uma senha forte e **GUARDE-A**
   - **Region**: Escolha a região mais próxima (ex: Europe - West (London))
   - **Pricing Plan**: Free (suficiente para começar)
4. Clique em **"Create new project"**
5. ⏱️ Aguarde 1-2 minutos enquanto o projeto é criado

### 1.2 Obter credenciais

Após o projeto ser criado:

1. No dashboard do projeto, vá em **Settings** (engrenagem) no menu lateral
2. Clique em **API**
3. Copie e guarde:
   - **Project URL** (algo como: `https://xxxxx.supabase.co`)
   - **anon/public key** (uma string longa começando com `eyJ...`)

⚠️ **IMPORTANTE**: Nunca compartilhe essas credenciais publicamente!

---

## 🗄️ PASSO 2: CRIAR SCHEMA DO BANCO DE DADOS

### 2.1 Acessar SQL Editor

1. No menu lateral do Supabase, clique em **"SQL Editor"**
2. Clique em **"New query"**

### 2.2 Executar script SQL completo

1. Abra o arquivo `COMPLETE_SCHEMA.sql` neste repositório
2. Copie **TODO** o conteúdo do arquivo (Ctrl+A, Ctrl+C)
3. Cole no SQL Editor do Supabase
4. Clique em **"Run"** (ou pressione Ctrl+Enter)

### 2.3 Verificar criação

Se tudo correr bem, você verá:
- ✅ Mensagem de sucesso
- ✅ Lista das 6 tabelas criadas
- ✅ Resumo das funcionalidades ativadas

**Tabelas criadas:**
- `campanhas` - Campanhas de rifas
- `escuteiros` - Escuteiros vendedores
- `blocos_rifas` - Blocos de rifas
- `vendas` - Vendas (legado)
- `pagamentos` - Pagamentos e canhotos
- `devolucoes` - Devoluções de rifas

---

## ⚙️ PASSO 3: CONFIGURAR VARIÁVEIS DE AMBIENTE

### 3.1 Criar arquivo .env

Na raiz do projeto, crie um arquivo chamado `.env`:

```bash
# No terminal, na pasta do projeto:
touch .env
```

### 3.2 Adicionar credenciais

Abra o arquivo `.env` e adicione:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

⚠️ Substitua pelos valores que você copiou no Passo 1.2!

### 3.3 Verificar .gitignore

Certifique-se de que o arquivo `.gitignore` contém:

```
.env
*.pyc
__pycache__/
```

Isso evita que suas credenciais sejam enviadas ao Git.

---

## 📦 PASSO 4: INSTALAR DEPENDÊNCIAS

### 4.1 Criar ambiente virtual (recomendado)

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

### 4.2 Instalar pacotes

```bash
pip install -r requirements.txt
```

**Pacotes instalados:**
- `streamlit` - Framework web
- `supabase` - Cliente Python do Supabase
- `python-dotenv` - Carregar variáveis .env
- `pandas` - Manipulação de dados
- `plotly` - Gráficos interativos

---

## 🎮 PASSO 5: EXECUTAR APLICAÇÃO

### 5.1 Iniciar aplicação

```bash
streamlit run app.py
```

### 5.2 Acessar aplicação

A aplicação abrirá automaticamente no navegador em:
```
http://localhost:8501
```

Se não abrir automaticamente, copie e cole o endereço no navegador.

---

## 📊 PASSO 6: CONFIGURAÇÃO INICIAL DO SISTEMA

### 6.1 Criar primeira campanha

1. No menu lateral, clique em **"📅 Campanhas"**
2. Vá na tab **"➕ Adicionar Campanha"**
3. Preencha:
   - Nome: `Natal2025`
   - Descrição: `Campanha de rifas de Natal 2025`
   - Data Início: `01/11/2025`
   - Data Fim: `31/12/2025`
   - ✅ Marque **"Campanha Ativa"**
4. Clique em **"✅ Criar Campanha"**

### 6.2 Criar blocos de rifas

1. Ainda na página de Campanhas, vá na tab **"🎟️ Criar Blocos de Rifas"**
2. Selecione a campanha **"Natal2025"**
3. Preencha:
   - Total de Rifas: `1000`
   - Rifas por Bloco: `10`
   - Preço por Rifa: `1.00 €`
4. Clique em **"🎟️ Criar Blocos de Rifas"**

✅ Serão criados 100 blocos de 10 rifas cada!

### 6.3 Adicionar escuteiros

1. No menu lateral, clique em **"👥 Escuteiros"**
2. Vá na tab **"➕ Adicionar"**
3. Adicione alguns escuteiros:
   - Nome: `João Silva`
   - Email: `joao@exemplo.com` (opcional)
   - Telefone: `912345678` (opcional)
4. Clique em **"Adicionar Escuteiro"**

Repita para adicionar mais escuteiros.

### 6.4 Atribuir blocos aos escuteiros

1. No menu lateral, clique em **"🎟️ Blocos de Rifas"**
2. Vá na tab **"🏷️ Reservar por Secção"** (opcional)
   - Pode reservar blocos para secções específicas
3. Vá na tab **"➕ Atribuir a Escuteiro"**
4. Selecione um bloco disponível
5. Selecione o escuteiro
6. Clique em **"💾 Guardar"**

### 6.5 Registar pagamentos

1. No menu lateral, clique em **"💳 Pagamentos"**
2. Vá na tab **"➕ Registar Pagamento"**
3. Selecione o bloco do escuteiro
4. Indique quantas rifas vendeu
5. Registe o valor pago
6. Indique quantos canhotos entregou
7. Clique em **"Registar Pagamento"**

---

## 🔍 VERIFICAR TUDO FUNCIONA

### ✅ Checklist de verificação

- [ ] Aplicação abre sem erros
- [ ] Dashboard mostra "✅ Conectado"
- [ ] Consegue criar uma campanha
- [ ] Consegue adicionar escuteiros
- [ ] Consegue criar blocos de rifas
- [ ] Consegue atribuir blocos a escuteiros
- [ ] Consegue registar pagamentos
- [ ] Gráficos aparecem corretamente

---

## 🐛 RESOLUÇÃO DE PROBLEMAS

### Erro: "Credenciais do Supabase não encontradas"

**Causa**: Arquivo `.env` não foi criado ou está mal configurado

**Solução**:
1. Verifique se o arquivo `.env` existe na raiz do projeto
2. Verifique se as variáveis estão corretas:
   ```env
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=eyJxxxxxxxxxxxxx
   ```
3. Reinicie a aplicação

### Erro ao executar SQL: "relation already exists"

**Causa**: Tabelas já foram criadas anteriormente

**Solução**: 
Isso é normal se estiver recriando. O SQL usa `CREATE TABLE IF NOT EXISTS`, então não há problema.

### Erro: "permission denied for table"

**Causa**: Políticas RLS muito restritivas

**Solução**:
1. No Supabase, vá em **SQL Editor**
2. Execute:
   ```sql
   -- Verificar se RLS está causando problemas
   ALTER TABLE campanhas DISABLE ROW LEVEL SECURITY;
   ALTER TABLE escuteiros DISABLE ROW LEVEL SECURITY;
   ALTER TABLE blocos_rifas DISABLE ROW LEVEL SECURITY;
   ALTER TABLE vendas DISABLE ROW LEVEL SECURITY;
   ALTER TABLE pagamentos DISABLE ROW LEVEL SECURITY;
   ALTER TABLE devolucoes DISABLE ROW LEVEL SECURITY;
   ```

### Aplicação lenta

**Causa**: Muitos dados ou queries não otimizadas

**Solução**:
- Use os filtros de campanha
- Limite o período de datas
- Os índices já estão criados pelo SQL

---

## 📚 PRÓXIMOS PASSOS

Agora que o sistema está configurado:

1. 📖 Leia o `README.md` para entender as funcionalidades
2. 🎯 Configure campanhas reais
3. 👥 Adicione todos os escuteiros
4. 🎟️ Crie e distribua blocos de rifas
5. 💰 Acompanhe vendas e pagamentos
6. 📊 Use o dashboard para análises

---

## 🆘 PRECISA DE AJUDA?

- 📧 Verifique a documentação do Supabase: https://supabase.com/docs
- 🐛 Reporte issues no GitHub
- 💬 Entre em contato com o administrador do sistema

---

## 🔐 SEGURANÇA

⚠️ **IMPORTANTE**:

- ❌ NUNCA compartilhe o arquivo `.env`
- ❌ NUNCA commite credenciais no Git
- ✅ Use variáveis de ambiente
- ✅ Configure RLS adequadamente para produção
- ✅ Use HTTPS em produção
- ✅ Faça backups regulares no Supabase

---

## 🎉 ESTÁ PRONTO!

O sistema está 100% configurado e pronto para uso!

Boa gestão de rifas! 🎟️✨
