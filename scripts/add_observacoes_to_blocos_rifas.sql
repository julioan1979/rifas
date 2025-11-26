-- Adicionar coluna 'observacoes' à tabela blocos_rifas
-- Execute este SQL no Supabase SQL Editor

ALTER TABLE blocos_rifas ADD COLUMN IF NOT EXISTS observacoes TEXT;

-- Opcional: comentário para documentação
COMMENT ON COLUMN blocos_rifas.observacoes IS 'Observações livres sobre o bloco (ex: divisão automática entre irmãos, histórico, etc)';
