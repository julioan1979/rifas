# Migração: Consolidar pagamentos para o fluxo Escuteiro → Organização

Objetivo
- Tirar os registos do fluxo comprador→escuteiro da operação ativa e consolidar o estado financeiro no fluxo escuteiro→organização (campos em `blocos_rifas`).

Resumo do processo
1. Fazer backup completo do banco de dados (pg_dump) e exportar `pagamentos` (CSV) para auditoria.
2. Executar as queries de auditoria para identificar discrepâncias (tabelas `audit_pagamentos_por_bloco`, `audit_diferencas_bloco`).
3. Arquivar a tabela `pagamentos` (`pagamentos_archive`).
4. Em staging, executar o script `scripts/consolidar_pagamentos_para_blocos.sql` e rever o relatório gerado (`report_consolidacao`).
5. Validar manualmente blocos com discrepância e corrigir casos especiais (pagamentos não entregues em caixa, erros de import).
6. Marcar `pagamentos` como `reconciled` (opcional) e descontinuar inserções novas nessa tabela.
7. Atualizar documentação e treinar a equipa.

Checklist (execução segura)
- [ ] Backup do BD criado (pg_dump)
- [ ] Export CSV dos pagamentos para auditoria
- [ ] Script de consolidação executado em staging e validado
- [ ] Casos de discrepância tratados manualmente
- [ ] `pagamentos` arquivado e marcado como `deprecated`
- [ ] Dashboard e queries atualizados para usar `blocos_rifas` como estado
- [ ] Comunicação enviada à equipa

Notas e riscos
- A consolidação automática assume que os valores em `pagamentos` representam efectivo recebido pelos escuteiros e que devem ser considerados para actualizar `blocos_rifas.valor_pago`.
- Se existir falta de entrega à organização (escuteiro não entregou o dinheiro), é necessária reconciliação manual antes de atualizar o bloco.
- Não executar `DELETE` em produção sem validação manual dos ids detectados como duplicados.

Referências
- Script de consolidação: `scripts/consolidar_pagamentos_para_blocos.sql`
- README: nota de decisão e referências de migração
