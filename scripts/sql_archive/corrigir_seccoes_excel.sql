-- Corrigir secções baseado nos dados REAIS do Excel
-- Observação visual do ficheiro: cores indicam secções

-- 1. Reserva: 1-180 (azul escuro)
UPDATE blocos_rifas 
SET seccao = 'Reserva' 
WHERE numero_inicial BETWEEN 1 AND 180;

-- 2. Lobitos: 181-310 (amarelo) 
UPDATE blocos_rifas 
SET seccao = 'Lobitos' 
WHERE numero_inicial BETWEEN 181 AND 310;

-- 3. Pioneiros: 311-420 (vermelho)
UPDATE blocos_rifas 
SET seccao = 'Pioneiros' 
WHERE numero_inicial BETWEEN 311 AND 420;

-- 4. Exploradores: 421-990 (verde - maior secção)
UPDATE blocos_rifas 
SET seccao = 'Exploradores' 
WHERE numero_inicial BETWEEN 421 AND 990;

-- Verificar resultado
SELECT 
    seccao,
    COUNT(*) as total_blocos,
    MIN(numero_inicial) as primeira_rifa,
    MAX(numero_final) as ultima_rifa,
    SUM(numero_final - numero_inicial + 1) as total_rifas
FROM blocos_rifas
GROUP BY seccao
ORDER BY MIN(numero_inicial);
