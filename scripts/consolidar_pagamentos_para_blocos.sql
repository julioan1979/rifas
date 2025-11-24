-- Script: auditoria + consolidação para migrar informação de
-- "pagamentos" (comprador->escuteiro) para o estado "escuteiro->organização"
-- ATENÇÃO: testar em staging. Fazer backup antes (pg_dump ou export CSV).

-- 1) Auditoria: resumo de pagamentos por bloco
CREATE TABLE IF NOT EXISTS audit_pagamentos_por_bloco AS
SELECT v.bloco_id,
       COALESCE(b.nome,'(sem nome)') AS bloco_nome,
       SUM(p.valor_pago) AS total_pago,
       MAX(p.data_pagamento) AS last_data_pagamento,
       COUNT(p.id) AS num_pagamentos
FROM pagamentos p
JOIN vendas v ON v.id = p.venda_id
LEFT JOIN blocos_rifas b ON b.id = v.bloco_id
GROUP BY v.bloco_id, b.nome
ORDER BY v.bloco_id;

-- 2) Auditoria: diferenças entre blocos.valor_pago e soma de pagamentos
CREATE TABLE IF NOT EXISTS audit_diferencas_bloco AS
SELECT b.id AS bloco_id,
       b.nome AS bloco_nome,
       COALESCE(b.valor_pago,0) AS bloco_valor,
       COALESCE(a.total_pago,0) AS pagamentos_total,
       COALESCE(a.num_pagamentos,0) AS num_pagamentos,
       (COALESCE(b.valor_pago,0) - COALESCE(a.total_pago,0)) AS diferenca
FROM blocos_rifas b
LEFT JOIN (
  SELECT v.bloco_id, SUM(p.valor_pago) AS total_pago, COUNT(p.id) AS num_pagamentos
  FROM pagamentos p
  JOIN vendas v ON v.id = p.venda_id
  GROUP BY v.bloco_id
) a ON a.bloco_id = b.id
WHERE COALESCE(b.valor_pago,0) <> COALESCE(a.total_pago,0)
ORDER BY b.id;

-- 3) Arquivar pagamentos (snapshot)
CREATE TABLE IF NOT EXISTS pagamentos_archive AS
SELECT * FROM pagamentos;

-- 4) Adicionar coluna 'reconciled' (opcional)
ALTER TABLE pagamentos
  ADD COLUMN IF NOT EXISTS reconciled boolean DEFAULT false;

-- 5) Consolidação: atualizar blocos com soma de pagamentos (teste em staging)
WITH pagos_por_bloco AS (
  SELECT v.bloco_id,
         SUM(p.valor_pago) AS total_pago,
         MAX(p.data_pagamento) AS last_data
  FROM pagamentos p
  JOIN vendas v ON v.id = p.venda_id
  GROUP BY v.bloco_id
)
UPDATE blocos_rifas b
SET valor_pago = COALESCE(pagos_por_bloco.total_pago, 0),
    data_pagamento = COALESCE(pagos_por_bloco.last_data, b.data_pagamento),
    ultima_conciliacao = NOW()
FROM pagos_por_bloco
WHERE b.id = pagos_por_bloco.bloco_id
  AND COALESCE(b.valor_pago,0) <> COALESCE(pagos_por_bloco.total_pago,0);

-- 6) Marcar pagamentos como reconciled quando ligados a um bloco
UPDATE pagamentos p
SET reconciled = true
FROM vendas v
WHERE p.venda_id = v.id
  AND v.bloco_id IS NOT NULL;

-- 7) Detectar duplicados (SELECT antes de apagar)
SELECT venda_id,
       valor_pago,
       date_trunc('second', data_pagamento) AS dt,
       COUNT(*) AS cnt,
       array_agg(id) AS ids
FROM pagamentos
GROUP BY venda_id, valor_pago, date_trunc('second', data_pagamento)
HAVING COUNT(*) > 1;

-- 8) (Opcional) Remover duplicados após revisão manual
WITH duplicates AS (
  SELECT id,
         ROW_NUMBER() OVER (
           PARTITION BY venda_id, valor_pago, date_trunc('second', data_pagamento)
           ORDER BY created_at NULLS LAST, id
         ) AS rn
  FROM pagamentos
)
DELETE FROM pagamentos
WHERE id IN (SELECT id FROM duplicates WHERE rn > 1);

-- 9) Relatório final de consolidação
CREATE TABLE IF NOT EXISTS report_consolidacao AS
SELECT b.id AS bloco_id,
       b.nome AS bloco_nome,
       COALESCE(b.valor_a_pagar,0) AS valor_a_pagar,
       COALESCE(b.valor_pago,0) AS valor_pago,
       COALESCE(b.valor_a_pagar,0) - COALESCE(b.valor_pago,0) AS saldo_pendente,
       COALESCE(a.num_pagamentos,0) AS num_pagamentos_registados,
       COALESCE(a.total_pago,0) AS total_pago_registado,
       b.ultima_conciliacao
FROM blocos_rifas b
LEFT JOIN (
  SELECT v.bloco_id, SUM(p.valor_pago) AS total_pago, COUNT(p.id) AS num_pagamentos
  FROM pagamentos p
  JOIN vendas v ON v.id = p.venda_id
  GROUP BY v.bloco_id
) a ON a.bloco_id = b.id
ORDER BY b.id;
