-- Corrigir blocos da Reserva que estão sem secção

-- 1. Atualizar blocos entre 1-180 que não têm secção
UPDATE blocos_rifas 
SET seccao = 'Reserva' 
WHERE numero_inicial BETWEEN 1 AND 180 
  AND (seccao IS NULL OR seccao = '');

-- 2. Verificar resultado
SELECT 
    seccao,
    COUNT(*) as total_blocos,
    MIN(numero_inicial) as primeira_rifa,
    MAX(numero_final) as ultima_rifa
FROM blocos_rifas
GROUP BY seccao
ORDER BY MIN(numero_inicial);

-- 3. Listar blocos sem secção (se houver)
SELECT 
    nome,
    numero_inicial,
    numero_final,
    seccao,
    estado
FROM blocos_rifas
WHERE seccao IS NULL OR seccao = ''
ORDER BY numero_inicial;
