-- Script para corrigir secções dos blocos que foram reatribuídos
-- Alguns blocos que antes eram Reserva foram depois dados a outras secções

-- Bloco 391-400 e 411-420: São Lobitos (originalmente Reserva)
UPDATE blocos_rifas 
SET seccao = 'Lobitos' 
WHERE (numero_inicial = 391 AND numero_final = 400)
   OR (numero_inicial = 411 AND numero_final = 420);

-- Verificar se há mais blocos fora do range esperado das secções
-- que precisam de correção manual

-- Ranges esperados:
-- Reserva: 1-180 (sem escuteiro atribuído)
-- Lobitos: 181-420
-- Exploradores: 421-830
-- Pioneiros: 831-930
-- Caminheiros: 931-990

SELECT 
    nome,
    seccao,
    numero_inicial,
    numero_final,
    CASE 
        WHEN numero_inicial BETWEEN 1 AND 180 THEN 'Reserva'
        WHEN numero_inicial BETWEEN 181 AND 420 THEN 'Lobitos'
        WHEN numero_inicial BETWEEN 421 AND 830 THEN 'Exploradores'
        WHEN numero_inicial BETWEEN 831 AND 930 THEN 'Pioneiros'
        WHEN numero_inicial BETWEEN 931 AND 990 THEN 'Caminheiros'
        ELSE 'Desconhecido'
    END as seccao_esperada
FROM blocos_rifas
WHERE seccao != CASE 
        WHEN numero_inicial BETWEEN 1 AND 180 THEN 'Reserva'
        WHEN numero_inicial BETWEEN 181 AND 420 THEN 'Lobitos'
        WHEN numero_inicial BETWEEN 421 AND 830 THEN 'Exploradores'
        WHEN numero_inicial BETWEEN 831 AND 930 THEN 'Pioneiros'
        WHEN numero_inicial BETWEEN 931 AND 990 THEN 'Caminheiros'
        ELSE 'Desconhecido'
    END
ORDER BY numero_inicial;
