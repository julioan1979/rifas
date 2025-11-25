-- ================================================================
-- ATUALIZAR SECÇÕES DOS BLOCOS EXISTENTES
-- ================================================================
-- 
-- Este SQL atribui secções aos blocos que têm seccao = NULL
-- Você pode escolher uma das opções abaixo
-- ================================================================

-- OPÇÃO 1: Atribuir todos os blocos NULL para uma secção específica
-- (descomente e escolha a secção)
-- UPDATE blocos_rifas SET seccao = 'Lobitos' WHERE seccao IS NULL;
-- UPDATE blocos_rifas SET seccao = 'Exploradores' WHERE seccao IS NULL;
-- UPDATE blocos_rifas SET seccao = 'Pioneiros' WHERE seccao IS NULL;
-- UPDATE blocos_rifas SET seccao = 'Caminheiros' WHERE seccao IS NULL;
-- UPDATE blocos_rifas SET seccao = 'CPP' WHERE seccao IS NULL;

-- OPÇÃO 2: Distribuir automaticamente entre secções
-- (distribui em ordem: primeiro terço Lobitos, segundo Exploradores, etc)
WITH blocos_ordenados AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (ORDER BY numero_inicial) as rn,
        COUNT(*) OVER () as total
    FROM blocos_rifas
    WHERE seccao IS NULL
)
UPDATE blocos_rifas b
SET seccao = CASE 
    WHEN bo.rn <= bo.total * 0.2 THEN 'Lobitos'
    WHEN bo.rn <= bo.total * 0.4 THEN 'Exploradores'
    WHEN bo.rn <= bo.total * 0.6 THEN 'Pioneiros'
    WHEN bo.rn <= bo.total * 0.8 THEN 'Caminheiros'
    ELSE 'CPP'
END
FROM blocos_ordenados bo
WHERE b.id = bo.id;

-- OPÇÃO 3: Verificar resultado
SELECT 
    seccao,
    COUNT(*) as total_blocos,
    MIN(numero_inicial) as primeira_rifa,
    MAX(numero_final) as ultima_rifa
FROM blocos_rifas
GROUP BY seccao
ORDER BY MIN(numero_inicial);

-- ================================================================
-- NOTA: Execute apenas UMA das opções acima
-- Depois recarregue a página de Blocos de Rifas
-- ================================================================
