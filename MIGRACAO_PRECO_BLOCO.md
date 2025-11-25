# 🔄 MIGRAÇÃO: Preço Unitário → Preço do Bloco

## ✅ O QUE MUDOU

**ANTES:** Preço unitário (por rifa)
**AGORA:** Preço do bloco (total)

## 🎯 VANTAGENS

1. **Mais prático**: Define preço total do bloco diretamente
2. **Flexível**: Blocos diferentes podem ter preços diferentes
3. **Simples**: Sem cálculos (10 rifas × 1€ = 10€)
4. **Real**: É assim que os blocos são vendidos

## 📊 EXEMPLO

```
Bloco 1-10 (10 rifas) = 10€
Bloco 11-20 (10 rifas) = 10€
Bloco 21-50 (30 rifas) = 25€ (desconto!)
```

## 🚀 COMO MIGRAR

### 1️⃣ Execute o SQL de Migração

```bash
Arquivo: MIGRAR_PRECO_BLOCO.sql
```

1. Abra o arquivo `MIGRAR_PRECO_BLOCO.sql`
2. Copie todo o conteúdo
3. Cole no Supabase SQL Editor
4. Execute (Run)

**O que o SQL faz:**
- ✅ Cria coluna `preco_bloco`
- ✅ Calcula valores (quantidade × preço_unitario)
- ✅ Remove coluna `preco_unitario`
- ✅ Mantém todos os dados existentes

### 2️⃣ Reinicie a Aplicação

```bash
# Parar (Ctrl+C)
streamlit run app.py
```

## 🎨 NOVA INTERFACE

### Criar Blocos (Campanhas):
```
Preço por Bloco: [10.00 €]  ← NOVO!
```

### Lista de Blocos:
```
Nº Inicial | Nº Final | Total | Secção | Preço Bloco
1          | 10       | 10    | Lobitos| 10.00 €
```

### Pagamentos:
```
Bloco selecionado: 10€
Rifas vendidas: 5
Valor esperado: 5.00€ (5 × 1.00€)
```

## ⚠️ IMPORTANTE

- **Backup**: O SQL remove `preco_unitario`
- **Dados preservados**: Valores são convertidos automaticamente
- **Compatível**: Todas as páginas atualizadas

## ✅ TUDO PRONTO!

Depois de executar o SQL, o sistema:
- ✅ Exibe "Preço do Bloco" em vez de "Preço Unitário"
- ✅ Calcula automaticamente preço por rifa quando necessário
- ✅ Funciona perfeitamente com dados existentes

---

**Execute o SQL agora!** 🚀
