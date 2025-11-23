-- Adicionar coluna 'seccao' à tabela blocos_rifas
ALTER TABLE blocos_rifas 
ADD COLUMN IF NOT EXISTS seccao TEXT;

-- Atualizar blocos existentes com a secção baseado nos números
UPDATE blocos_rifas 
SET seccao = 'Reserva' 
WHERE numero_inicial >= 1 AND numero_final <= 180;

UPDATE blocos_rifas 
SET seccao = 'Lobitos' 
WHERE numero_inicial >= 181 AND numero_final <= 420;

UPDATE blocos_rifas 
SET seccao = 'Exploradores' 
WHERE numero_inicial >= 421 AND numero_final <= 830;

UPDATE blocos_rifas 
SET seccao = 'Pioneiros' 
WHERE numero_inicial >= 831 AND numero_final <= 930;

UPDATE blocos_rifas 
SET seccao = 'Caminheiros' 
WHERE numero_inicial >= 931 AND numero_final <= 990;

SELECT 'Coluna seccao adicionada e blocos atualizados! ✅' as status;
