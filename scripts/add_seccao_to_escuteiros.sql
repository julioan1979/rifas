-- Adicionar coluna 'seccao' à tabela escuteiros
-- Execute este SQL no Supabase SQL Editor

-- Adicionar coluna seccao (se não existir)
ALTER TABLE escuteiros ADD COLUMN IF NOT EXISTS seccao VARCHAR(50);

-- Adicionar comentário na coluna
COMMENT ON COLUMN escuteiros.seccao IS 'Secção do escuteiro: Lobitos, Exploradores, Pioneiros, Caminheiros, CPP';

-- Verificar a estrutura atualizada
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns
WHERE table_name = 'escuteiros'
ORDER BY ordinal_position;
