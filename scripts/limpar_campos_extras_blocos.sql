-- ============================================
-- LIMPAR CAMPOS EXTRAS DA TABELA blocos_rifas
-- ============================================
-- Remove campos que eram da página 6 (Controle_Escuteiros) 
-- que foi removida do projeto

-- 1. Remover views que dependem dos campos
DROP VIEW IF EXISTS vw_situacao_blocos CASCADE;
DROP VIEW IF EXISTS vw_controle_escuteiros CASCADE;
DROP VIEW IF EXISTS vw_blocos_controle CASCADE;

-- 2. Remover campos não utilizados
ALTER TABLE blocos_rifas DROP COLUMN IF EXISTS data_pagamento CASCADE;
ALTER TABLE blocos_rifas DROP COLUMN IF EXISTS valor_a_pagar CASCADE;
ALTER TABLE blocos_rifas DROP COLUMN IF EXISTS observacoes_canhotos CASCADE;
ALTER TABLE blocos_rifas DROP COLUMN IF EXISTS canhotos_devolvidos CASCADE;
ALTER TABLE blocos_rifas DROP COLUMN IF EXISTS metodo_pagamento CASCADE;
ALTER TABLE blocos_rifas DROP COLUMN IF EXISTS rifas_vendidas CASCADE;
ALTER TABLE blocos_rifas DROP COLUMN IF EXISTS data_devolucao_canhotos CASCADE;
ALTER TABLE blocos_rifas DROP COLUMN IF EXISTS observacoes_pagamento CASCADE;
ALTER TABLE blocos_rifas DROP COLUMN IF EXISTS valor_pago CASCADE;

-- Verificação: Listar campos restantes
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'blocos_rifas' 
  AND table_schema = 'public'
ORDER BY ordinal_position;

-- Confirmação
SELECT 'Campos extras removidos com sucesso! ✅' as status;
