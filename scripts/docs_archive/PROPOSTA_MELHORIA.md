# Proposta de Melhoria - Fluxo de Pagamentos e Devoluções

## Problema Atual
O sistema atual tem duas tabelas separadas (vendas e pagamentos) que criam confusão:
- **Vendas**: Registra que rifas foram vendidas
- **Pagamentos**: Registra pagamentos de vendas

Mas o fluxo real é:
1. Escuteiro recebe bloco de rifas
2. Escuteiro vende as rifas (ou não)
3. Escuteiro **paga** o valor do bloco à organização
4. Escuteiro **devolve os canhotos** das rifas vendidas

## Solução Proposta

### Opção A: Adicionar campos ao bloco (Mais Simples)
Adicionar à tabela `blocos_rifas`:
- `valor_a_pagar`: DECIMAL (valor que o escuteiro deve pagar)
- `valor_pago`: DECIMAL (valor já pago)
- `data_pagamento`: TIMESTAMP (quando pagou)
- `canhotos_devolvidos`: BOOLEAN (se devolveu os canhotos)
- `data_devolucao_canhotos`: TIMESTAMP
- `observacoes_pagamento`: TEXT

### Opção B: Nova tabela de controle (Mais Completo)
Criar tabela `controle_blocos`:
- `id`: UUID
- `bloco_id`: UUID (FK)
- `escuteiro_id`: UUID (FK)
- `rifas_vendidas`: INTEGER
- `rifas_nao_vendidas`: INTEGER
- `valor_a_pagar`: DECIMAL
- `valor_pago`: DECIMAL
- `saldo_pendente`: DECIMAL
- `data_pagamento`: TIMESTAMP
- `metodo_pagamento`: TEXT
- `canhotos_devolvidos`: BOOLEAN
- `data_devolucao_canhotos`: TIMESTAMP
- `observacoes`: TEXT

## Fluxo Recomendado

1. **Atribuição**: Bloco atribuído ao escuteiro
2. **Venda**: Escuteiro vende rifas (opcional registrar quantas)
3. **Pagamento**: Escuteiro paga valor à organização
4. **Devolução de Canhotos**: Escuteiro devolve canhotos das rifas vendidas
5. **Encerramento**: Bloco marcado como completo

## Qual opção prefere?
