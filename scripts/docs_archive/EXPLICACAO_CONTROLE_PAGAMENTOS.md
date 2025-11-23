# 💵 Sistema de Controle de Pagamentos e Canhotos

## 📋 O Problema Identificado

Você identificou corretamente que o sistema atual não estava adequado ao fluxo real:

### Fluxo Real dos Escuteiros:
1. **Escuteiro recebe bloco de rifas** (ex: rifas 1-10)
2. **Escuteiro vende as rifas** aos compradores
3. **Escuteiro PAGA o dinheiro** à organização (pelo valor total ou pelas vendidas)
4. **Escuteiro DEVOLVE os CANHOTOS** das rifas vendidas
   - **IMPORTANTE:** Os canhotos contêm os dados de quem comprou (nome, contacto, nº da rifa)
   - Sem os canhotos, não é possível fazer o sorteio!

### O que estava errado:
- Sistema focava em "vendas" genéricas
- Não rastreava o pagamento do escuteiro à organização
- Não controlava a devolução dos canhotos
- Confusão entre "venda" (escuteiro vende rifa) e "pagamento" (escuteiro paga à organização)

## ✅ Solução Implementada

### 1. Nova Página: "💵 Controle de Escuteiros"
Criada em `/workspaces/rifas/pages/6_💵_Controle_Escuteiros.py`

**Funcionalidades:**
- **Tab 1 - Visão Geral:** Lista todos os blocos atribuídos e sua situação
- **Tab 2 - Registar:** Interface para registar:
  - 💰 Pagamento do escuteiro
  - 📋 Devolução dos canhotos
  - Quantas rifas foram vendidas

### 2. Atualização da Base de Dados
Arquivo SQL criado: `/workspaces/rifas/sql_update_blocos_controle.sql`

**Novas colunas adicionadas à tabela `blocos_rifas`:**

**Controle de Pagamentos:**
- `valor_a_pagar` - Valor total do bloco (nº rifas × preço)
- `valor_pago` - Quanto o escuteiro já pagou
- `data_pagamento` - Quando pagou
- `metodo_pagamento` - Como pagou (Dinheiro, Transferência, etc)
- `observacoes_pagamento` - Notas sobre o pagamento

**Controle de Canhotos:**
- `rifas_vendidas` - Quantas rifas o escuteiro vendeu
- `canhotos_devolvidos` - TRUE/FALSE se devolveu os canhotos
- `data_devolucao_canhotos` - Quando devolveu
- `observacoes_canhotos` - Notas (ex: faltam 2 canhotos)

**View Criada:** `vw_situacao_blocos`
- Consolida todas as informações de cada bloco
- Calcula saldo pendente
- Mostra situação: ✅ Completo | 💰 Pago | 📋 Canhotos OK | ⏳ Pendente

## 🚀 Como Ativar

### Passo 1: Executar o SQL
1. Abra o Supabase (https://supabase.com)
2. Vá ao seu projeto
3. Clique em "SQL Editor"
4. Copie todo o conteúdo de `/workspaces/rifas/sql_update_blocos_controle.sql`
5. Cole e execute (RUN)

### Passo 2: Atualizar a página de Controle
Depois de executar o SQL, vou atualizar a página para usar as novas colunas.

## 📊 Fluxo de Trabalho Completo

### Fase 1: Preparação (Página Campanhas)
1. Criar campanha (ex: Natal2025)
2. Criar blocos de rifas automaticamente

### Fase 2: Atribuição (Página Blocos de Rifas)
1. Atribuir blocos aos escuteiros
2. Escuteiro sai com o bloco para vender

### Fase 3: Controle (NOVA Página Controle de Escuteiros)
1. **Quando escuteiro paga:**
   - Selecionar o bloco do escuteiro
   - Registar valor pago
   - Registar método (dinheiro, transferência, etc)
   - Data do pagamento

2. **Quando escuteiro devolve canhotos:**
   - Marcar quantas rifas vendeu
   - Marcar que devolveu os canhotos
   - Data da devolução
   - Observações (se falta algum canhoto)

### Fase 4: Visão Geral
- Dashboard mostra situação de cada escuteiro
- Status claro: Completo | Pago | Canhotos OK | Pendente
- Relatórios de quem ainda não pagou
- Relatórios de quem não devolveu canhotos

## 💡 Vantagens do Novo Sistema

1. ✅ **Controle Financeiro:** Sabe exatamente quem pagou e quanto
2. ✅ **Controle dos Canhotos:** Essencial para o sorteio
3. ✅ **Visibilidade:** Dashboard mostra situação de cada escuteiro
4. ✅ **Histórico:** Todas as datas registadas
5. ✅ **Flexibilidade:** Pagamentos parciais possíveis
6. ✅ **Auditoria:** Observações para casos especiais

## 🎯 Próximos Passos

Quer que eu:
1. ✅ Execute o SQL (se tiver acesso)
2. ✅ Ative a funcionalidade na página de Controle
3. ✅ Crie relatórios adicionais
4. ✅ Adicione notificações para escuteiros pendentes

**Diga-me se quer que execute o SQL ou se prefere fazer manualmente!**
