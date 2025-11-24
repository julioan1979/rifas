# 📄 Sistema de Controlo de Canhotos

## 🎯 Objetivo
Rastrear a entrega de canhotos (físicos) das rifas vendidas pelos escuteiros durante a prestação de contas.

## 📋 Como Funciona

### 1. **Fluxo Normal**
```
Escuteiro recebe rifas → Vende rifas → Presta contas (dinheiro + canhotos)
```

### 2. **Na Página de Pagamentos**
Quando um pagamento é registado, o gestor pode:
- ✅ Registar quantos canhotos foram entregues (pode ser parcial)
- 📝 Adicionar observações (ex: "Faltam 3 canhotos")
- 📅 Data de entrega é registada automaticamente

### 3. **Status Visuais**
- **✅ Verde** `10/10`: Todos os canhotos entregues
- **⚠️ Amarelo** `7/10`: Entrega parcial (faltam canhotos)
- **❌ Vermelho** `0/10`: Nenhum canhoto entregue

## 🛠️ Implementação Técnica

### **Campos na tabela `pagamentos`**
```sql
canhotos_entregues INTEGER       -- Quantos foram entregues
canhotos_esperados INTEGER       -- Quantos eram esperados (baseado na venda)
data_entrega_canhotos TIMESTAMP  -- Quando foram entregues
observacoes_canhotos TEXT        -- Notas sobre a entrega
```

### **Para Ativar no Supabase**
Execute o script SQL:
```bash
# No Supabase SQL Editor, execute:
/workspaces/rifas/scripts/adicionar_controlo_canhotos.sql
```

## 📊 Métricas Disponíveis

Na página de Pagamentos, são exibidas:
1. **Total de Pagamentos**
2. **Valor Total Recebido**
3. **Canhotos Entregues** (X/Y)
4. **Taxa de Entrega** (%)

## 🔍 View Auxiliar

Foi criada uma view `vw_status_canhotos_escuteiro` que mostra:
- Total de canhotos esperados por escuteiro
- Total de canhotos entregues
- Canhotos em falta
- Percentagem de entrega

## 💡 Casos de Uso

### **Caso 1: Entrega Completa**
```
Escuteiro vendeu 10 rifas
→ Entrega 10 canhotos
→ Status: 10/10 ✅
```

### **Caso 2: Entrega Parcial**
```
Escuteiro vendeu 10 rifas
→ Entrega 7 canhotos agora
→ Status: 7/10 ⚠️
→ Observações: "Prometeu entregar os restantes 3 na próxima semana"
→ Pode fazer outro pagamento depois com os 3 restantes
```

### **Caso 3: Sem Canhotos**
```
Escuteiro vendeu 10 rifas
→ Paga mas não traz canhotos
→ Status: 0/10 ❌
→ Observações: "Deixou em casa, vai trazer amanhã"
```

## ⚠️ Notas Importantes

1. **Múltiplas Entregas**: O sistema suporta entregas parciais em diferentes datas
2. **Histórico**: Cada pagamento mantém registo dos canhotos entregues naquela data
3. **Flexibilidade**: O campo observações permite registar qualquer situação especial
4. **Rastreabilidade**: Data de entrega é automática quando canhotos > 0

## 🚀 Próximos Passos

1. Execute o script SQL no Supabase
2. Teste registar um pagamento com canhotos
3. Verifique a coluna "Canhotos" na listagem
4. Consulte as métricas no topo da página
