-- Adicionar coluna 'preco_unitario' à tabela blocos_rifas e preencher a partir de preco_bloco
-- Execute este SQL no Supabase SQL Editor (faça backup antes de alterações destrutivas)

-- 1) Adicionar coluna preco_unitario
ALTER TABLE blocos_rifas ADD COLUMN IF NOT EXISTS preco_unitario numeric;

-- 2) Backfill: quando existir preco_bloco e número de rifas > 0
UPDATE blocos_rifas
SET preco_unitario = preco_bloco / (numero_final - numero_inicial + 1)
WHERE preco_bloco IS NOT NULL
  AND (numero_final - numero_inicial + 1) > 0
  AND preco_unitario IS NULL;

-- 3) Garantir valores não-negativos (adicionar apenas se não existir)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'preco_unitario_non_negative'
  ) THEN
    ALTER TABLE blocos_rifas ADD CONSTRAINT preco_unitario_non_negative CHECK (preco_unitario >= 0);
  END IF;
END$$;

-- Observação:
-- - Este script apenas adiciona a coluna e tenta derivar o preco_unitario a partir do preco_bloco existente.
-- - Depois de executar, actualize a aplicação para começar a gravar explicitamente preco_unitario em novos blocos
--   (ou ao dividir blocos) para manter o preço unitário fixo no momento da criação.
