-- Script para adicionar controlo de canhotos na tabela pagamentos
-- Data: 2025-11-24
-- Descrição: Adiciona campos para rastrear entrega de canhotos (parcial ou total)

-- Adicionar campos de controlo de canhotos
ALTER TABLE pagamentos ADD COLUMN IF NOT EXISTS canhotos_entregues INTEGER DEFAULT 0 CHECK (canhotos_entregues >= 0);
ALTER TABLE pagamentos ADD COLUMN IF NOT EXISTS canhotos_esperados INTEGER CHECK (canhotos_esperados >= 0);
ALTER TABLE pagamentos ADD COLUMN IF NOT EXISTS data_entrega_canhotos TIMESTAMP WITH TIME ZONE;
ALTER TABLE pagamentos ADD COLUMN IF NOT EXISTS observacoes_canhotos TEXT;

-- Adicionar comentários para documentação
COMMENT ON COLUMN pagamentos.canhotos_entregues IS 'Número de canhotos efetivamente entregues pelo escuteiro';
COMMENT ON COLUMN pagamentos.canhotos_esperados IS 'Número de canhotos esperados (baseado na quantidade vendida)';
COMMENT ON COLUMN pagamentos.data_entrega_canhotos IS 'Data em que os canhotos foram entregues';
COMMENT ON COLUMN pagamentos.observacoes_canhotos IS 'Observações sobre a entrega dos canhotos (ex: faltam 3, prometeu entregar depois)';

-- Criar índice para consultas de canhotos pendentes
CREATE INDEX IF NOT EXISTS idx_pagamentos_canhotos_status ON pagamentos(canhotos_entregues, canhotos_esperados);

-- Atualizar registos existentes (assumir que não foram entregues canhotos)
-- Os valores de canhotos_esperados serão calculados na aplicação baseado na quantidade vendida
UPDATE pagamentos 
SET canhotos_entregues = 0 
WHERE canhotos_entregues IS NULL;

-- View auxiliar para ver status de canhotos por escuteiro
CREATE OR REPLACE VIEW vw_status_canhotos_escuteiro AS
SELECT 
    e.id as escuteiro_id,
    e.nome as escuteiro_nome,
    COALESCE(SUM(p.canhotos_esperados), 0) as total_canhotos_esperados,
    COALESCE(SUM(p.canhotos_entregues), 0) as total_canhotos_entregues,
    COALESCE(SUM(p.canhotos_esperados), 0) - COALESCE(SUM(p.canhotos_entregues), 0) as canhotos_em_falta,
    CASE 
        WHEN COALESCE(SUM(p.canhotos_esperados), 0) = 0 THEN 0
        ELSE ROUND((COALESCE(SUM(p.canhotos_entregues), 0)::NUMERIC / COALESCE(SUM(p.canhotos_esperados), 1)::NUMERIC * 100), 2)
    END as percentagem_entregue
FROM escuteiros e
LEFT JOIN vendas v ON e.id = v.escuteiro_id
LEFT JOIN pagamentos p ON v.id = p.venda_id
WHERE e.ativo = TRUE
GROUP BY e.id, e.nome
HAVING COALESCE(SUM(p.canhotos_esperados), 0) > 0
ORDER BY canhotos_em_falta DESC;

-- Verificar a estrutura atualizada
SELECT 
    column_name, 
    data_type, 
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'pagamentos' 
    AND column_name LIKE '%canhoto%'
ORDER BY ordinal_position;
