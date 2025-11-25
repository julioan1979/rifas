-- Adicionar colunas rifas_entregues e observacoes_canhotos à tabela pagamentos

ALTER TABLE pagamentos
ADD COLUMN IF NOT EXISTS rifas_entregues INTEGER;

ALTER TABLE pagamentos
ADD COLUMN IF NOT EXISTS observacoes_canhotos TEXT;

-- Adicionar comentários
COMMENT ON COLUMN pagamentos.rifas_entregues IS 'Número de canhotos/rifas entregues pelo escuteiro';
COMMENT ON COLUMN pagamentos.observacoes_canhotos IS 'Observações sobre os canhotos entregues (rifas perdidas, etc)';

-- Verificar estrutura
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'pagamentos'
ORDER BY ordinal_position;
