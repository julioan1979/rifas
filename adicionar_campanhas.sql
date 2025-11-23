-- Script para adicionar suporte a Campanhas
-- Execute este SQL no Supabase SQL Editor

-- 1. Criar tabela de campanhas
CREATE TABLE IF NOT EXISTS campanhas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    ativa BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT check_datas CHECK (data_fim >= data_inicio)
);

-- Criar índice
CREATE INDEX IF NOT EXISTS idx_campanhas_ativa ON campanhas(ativa);

-- Habilitar RLS
ALTER TABLE campanhas ENABLE ROW LEVEL SECURITY;

-- Criar policy
CREATE POLICY "Enable all for authenticated users" ON campanhas
    FOR ALL USING (true);

-- 2. Adicionar coluna campanha_id à tabela blocos_rifas
ALTER TABLE blocos_rifas 
ADD COLUMN IF NOT EXISTS campanha_id UUID REFERENCES campanhas(id) ON DELETE CASCADE;

-- Criar índice
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_campanha ON blocos_rifas(campanha_id);

-- 3. Criar campanha Natal2025 e associar blocos existentes
INSERT INTO campanhas (nome, descricao, data_inicio, data_fim, ativa)
VALUES ('Natal2025', 'Campanha de rifas do Natal 2025', '2025-11-01', '2025-12-31', true)
ON CONFLICT (nome) DO NOTHING;

-- 4. Associar todos os blocos existentes à campanha Natal2025
UPDATE blocos_rifas
SET campanha_id = (SELECT id FROM campanhas WHERE nome = 'Natal2025')
WHERE campanha_id IS NULL;

-- 5. Verificar resultado
SELECT 
    c.nome as campanha,
    c.ativa,
    COUNT(b.id) as total_blocos,
    SUM(b.numero_final - b.numero_inicial + 1) as total_rifas
FROM campanhas c
LEFT JOIN blocos_rifas b ON c.id = b.campanha_id
GROUP BY c.id, c.nome, c.ativa
ORDER BY c.created_at DESC;
