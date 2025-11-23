# 🚀 Guia de Deploy - Streamlit Cloud

Este guia explica como fazer deploy da aplicação no Streamlit Cloud (grátis).

## 📋 Pré-requisitos

- ✅ Conta no GitHub
- ✅ Conta no Streamlit Cloud ([share.streamlit.io](https://share.streamlit.io))
- ✅ Projeto Supabase configurado
- ✅ Código no GitHub

## 🎯 Passo a Passo

### 1️⃣ Preparar o Repositório GitHub

#### A. Verificar Ficheiros Necessários

Certifique-se que o repositório tem:
- ✅ `app.py`
- ✅ `requirements.txt`
- ✅ `utils/supabase_client.py`
- ✅ `utils/database_schema.py`
- ✅ `pages/` com todos os ficheiros
- ✅ `.streamlit/config.toml`

#### B. Fazer Push do Código

```bash
git add .
git commit -m "Sistema de Rifas - Versão completa"
git push origin main
```

### 2️⃣ Configurar Supabase

Se ainda não fez:

1. Execute o SQL completo de `SETUP_DATABASE.md`
2. Obtenha as credenciais:
   - Project URL: `https://seu-projeto.supabase.co`
   - anon public key: `eyJ...`

### 3️⃣ Deploy no Streamlit Cloud

#### A. Aceder ao Streamlit Cloud

1. Vá a [share.streamlit.io](https://share.streamlit.io)
2. Faça login com a sua conta GitHub
3. Autorize o Streamlit Cloud a aceder aos seus repositórios

#### B. Criar Nova App

1. Clique no botão **"New app"**
2. Preencha os campos:
   - **Repository:** `julioan1979/rifas` (ou o seu username)
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** Escolha um nome único (ex: `rifas-escuteiros`)

#### C. Configurar Secrets (IMPORTANTE!)

1. Clique em **"Advanced settings"**
2. Na secção **"Secrets"**, cole:

```toml
[supabase]
url = "https://seu-projeto.supabase.co"
key = "sua_chave_anon_publica_aqui"
```

⚠️ **IMPORTANTE:** 
- Use a chave **anon/public**, NÃO a service_role
- Certifique-se que não há espaços extra
- O formato TOML é sensível a espaços

#### D. Deploy

1. Clique em **"Deploy!"**
2. Aguarde 2-3 minutos
3. A app vai abrir automaticamente quando estiver pronta

### 4️⃣ Verificar o Deploy

#### ✅ Checklist Pós-Deploy

- [ ] App abre sem erros
- [ ] Mensagem "Conectado ao Supabase com sucesso" aparece
- [ ] Dashboard mostra métricas
- [ ] Todas as páginas do menu lateral aparecem
- [ ] Consegue adicionar um escuteiro de teste
- [ ] Consegue criar um bloco de rifas de teste

#### ❌ Se Houver Erros

**Erro: "Credenciais não encontradas"**
- Verifique as Secrets no Streamlit Cloud
- Certifique-se que usou o formato TOML correto
- Reinicie a app: Menu (⋮) → Reboot app

**Erro: "Tabela não encontrada"**
- Execute o SQL completo de `SETUP_DATABASE.md`
- Verifique no Supabase se as tabelas existem

**App não carrega / Erro de dependências**
- Verifique `requirements.txt`
- Reinicie a app
- Verifique os logs: Menu (⋮) → Logs

## ⚙️ Configurações Adicionais

### Alterar URL da App

1. No dashboard do Streamlit Cloud
2. Clique no menu (⋮) da app
3. Settings → General
4. Altere o App URL
5. Save

### Atualizar Secrets

1. Dashboard → Selecione a app
2. Menu (⋮) → Settings
3. Secrets
4. Edite e Save
5. App reinicia automaticamente

### Ver Logs

1. Dashboard → Selecione a app
2. Menu (⋮) → Logs
3. Ou clique no botão "Manage app" no canto inferior direito da app

### Reiniciar App

1. Dashboard → Selecione a app
2. Menu (⋮) → Reboot app
3. Ou na app, clique em "Manage app" → Reboot

## 🔄 Atualizações Automáticas

### Como Funciona

Sempre que fizer push para o branch `main`, o Streamlit Cloud:
1. Deteta as alterações
2. Faz rebuild automático
3. Deploy da nova versão
4. Reinicia a app

### Fazer uma Atualização

```bash
# 1. Fazer alterações no código
# 2. Commit
git add .
git commit -m "Descrição da atualização"

# 3. Push
git push origin main

# 4. Aguardar 2-3 minutos
# App atualiza automaticamente ✅
```

## 🌐 Partilhar a App

### URL Público

Após deploy, a app fica disponível em:
```
https://rifas-escuteiros.streamlit.app
```
(ou o nome que escolheu)

### Partilhar com a Equipa

1. Copie o URL da app
2. Partilhe com os utilizadores
3. Não precisa de login para aceder!

### Domínio Personalizado (Premium)

Para usar um domínio próprio:
1. Upgrade para Streamlit Cloud Pro
2. Configure o domínio nas Settings

## 🔐 Segurança

### ✅ Boas Práticas

- **Nunca** partilhe as Secrets
- Use a chave **anon**, não service_role
- Configure RLS no Supabase para produção
- Considere adicionar autenticação

### 🔒 Restringir Acesso (Premium)

No plano Pro do Streamlit Cloud:
- Pode adicionar autenticação
- Restringir por email/domínio
- Password protect

## 📊 Monitorização

### Ver Estatísticas de Uso

1. Dashboard do Streamlit Cloud
2. Selecione a app
3. Analytics (se disponível)

### Limites do Plano Grátis

- ✅ Apps ilimitadas (públicas)
- ✅ 1 GB de recursos por app
- ✅ Atualizações automáticas
- ⚠️ A app hiberna após inatividade (acorda em 30s)

## 🆘 Troubleshooting

### App hiberna muito
**Solução:** No plano grátis é normal. Considere upgrade para Pro.

### Erro de memória
**Solução:** Otimize queries, use cache do Streamlit.

### Erro "Module not found"
**Solução:** Adicione o módulo a `requirements.txt` e faça push.

### App muito lenta
**Solução:** 
- Use `st.cache_data` para queries
- Otimize queries SQL
- Considere índices no Supabase

## 📚 Recursos Úteis

- [Documentação Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- [Gestão de Secrets](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Deploy Tutorial](https://docs.streamlit.io/streamlit-community-cloud/get-started)

## ✅ Checklist Final

Antes de considerar o deploy concluído:

- [ ] App acessível publicamente
- [ ] Todas as funcionalidades a funcionar
- [ ] Secrets configuradas corretamente
- [ ] Database setup completo
- [ ] Sem erros nos logs
- [ ] Testado em diferentes dispositivos
- [ ] URL partilhado com a equipa
- [ ] Documentação acessível (README no repo)

---

## 🎉 Parabéns!

A sua aplicação está agora online e acessível para todos!

**URL da App:** `https://sua-app.streamlit.app`

**Próximos Passos:**
1. Adicione os primeiros escuteiros
2. Crie blocos de rifas
3. Comece a registar vendas
4. Partilhe com a equipa!

---

**💡 Dica:** Adicione o URL aos favoritos do navegador para acesso rápido!
