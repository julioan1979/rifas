-- ================================================================
-- ADICIONAR COLUNA SECCAO À TABELA ESCUTEIROS
-- ================================================================
-- 
-- Execute este SQL no Supabase SQL Editor para adicionar
-- o campo de secção aos escuteiros
-- ================================================================

-- Adicionar coluna seccao à tabela escuteiros
ALTER TABLE escuteiros 
ADD COLUMN IF NOT EXISTS seccao TEXT;

-- Criar índice para melhor performance
CREATE INDEX IF NOT EXISTS idx_escuteiros_seccao ON escuteiros(seccao);

-- Adicionar comentário
COMMENT ON COLUMN escuteiros.seccao IS 'Secção do escuteiro: Lobitos, Exploradores, Pioneiros, Caminheiros, CPP';

-- Verificar
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'escuteiros' 
ORDER BY ordinal_position;
