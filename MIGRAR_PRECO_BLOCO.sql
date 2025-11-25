-- ================================================================
-- MIGRAR DE PREÇO UNITÁRIO PARA PREÇO DO BLOCO
-- ================================================================
-- 
-- Esta migração muda de preco_unitario para preco_bloco
-- O preço do bloco é mais prático e intuitivo
-- ================================================================

-- PASSO 1: REMOVER VIEWS QUE DEPENDEM DE preco_unitario
-- ================================================================
DROP VIEW IF EXISTS vw_blocos_status CASCADE;
DROP VIEW IF EXISTS vw_pagamentos_por_bloco CASCADE;

-- PASSO 2: MIGRAR A COLUNA
-- ================================================================

-- 2.1. Adicionar nova coluna preco_bloco
ALTER TABLE blocos_rifas 
ADD COLUMN IF NOT EXISTS preco_bloco DECIMAL(10, 2);

-- 2.2. Calcular e preencher preco_bloco baseado nos dados existentes
UPDATE blocos_rifas 
SET preco_bloco = (numero_final - numero_inicial + 1) * preco_unitario
WHERE preco_bloco IS NULL AND preco_unitario IS NOT NULL;

-- 2.3. Tornar preco_bloco obrigatório
ALTER TABLE blocos_rifas 
ALTER COLUMN preco_bloco SET NOT NULL;

-- 2.4. Adicionar constraint para garantir que o preço é positivo
ALTER TABLE blocos_rifas 
ADD CONSTRAINT check_preco_bloco_positivo CHECK (preco_bloco > 0);

-- 2.5. Remover a coluna antiga preco_unitario
ALTER TABLE blocos_rifas 
DROP COLUMN IF EXISTS preco_unitario;

-- 2.6. Adicionar comentário explicativo
COMMENT ON COLUMN blocos_rifas.preco_bloco IS 'Preço total do bloco de rifas (não é por unidade)';

-- PASSO 3: RECRIAR AS VIEWS COM preco_bloco
-- ================================================================

-- View: Status dos blocos por secção
CREATE OR REPLACE VIEW vw_blocos_status AS
SELECT 
    c.nome AS campanha,
    b.seccao,
    COUNT(*) AS total_blocos,
    SUM(CASE WHEN b.estado = 'disponivel' THEN 1 ELSE 0 END) AS blocos_disponiveis,
    SUM(CASE WHEN b.estado = 'reservado' THEN 1 ELSE 0 END) AS blocos_reservados,
    SUM(CASE WHEN b.estado = 'vendido' THEN 1 ELSE 0 END) AS blocos_vendidos,
    SUM(b.preco_bloco) AS valor_total_blocos,
    SUM(CASE WHEN b.estado = 'vendido' THEN b.preco_bloco ELSE 0 END) AS valor_vendido
FROM blocos_rifas b
INNER JOIN campanhas c ON b.campanha_id = c.id
GROUP BY c.nome, b.seccao;

-- View: Pagamentos por bloco
CREATE OR REPLACE VIEW vw_pagamentos_por_bloco AS
SELECT 
    b.id AS bloco_id,
    b.nome AS bloco_nome,
    b.numero_inicial,
    b.numero_final,
    b.preco_bloco,
    e.nome AS escuteiro,
    COALESCE(SUM(p.valor_pago), 0) AS total_pago,
    b.preco_bloco - COALESCE(SUM(p.valor_pago), 0) AS saldo_pendente,
    CASE 
        WHEN COALESCE(SUM(p.valor_pago), 0) >= b.preco_bloco THEN 'Pago'
        WHEN COALESCE(SUM(p.valor_pago), 0) > 0 THEN 'Parcial'
        ELSE 'Pendente'
    END AS status_pagamento
FROM blocos_rifas b
INNER JOIN escuteiros e ON b.escuteiro_id = e.id
LEFT JOIN pagamentos p ON b.id = p.bloco_id
WHERE b.estado IN ('reservado', 'vendido')
GROUP BY b.id, b.nome, b.numero_inicial, b.numero_final, b.preco_bloco, e.nome;

-- PASSO 4: VERIFICAR RESULTADO
-- ================================================================

-- 7. Verificar resultado
SELECT 
    nome,
    numero_inicial,
    numero_final,
    (numero_final - numero_inicial + 1) as quantidade_rifas,
    preco_bloco,
    ROUND(preco_bloco / (numero_final - numero_inicial + 1), 2) as preco_por_rifa
FROM blocos_rifas
ORDER BY numero_inicial
LIMIT 10;

-- ================================================================
-- ✅ MIGRAÇÃO COMPLETA!
-- ================================================================
-- Este SQL faz:
-- 1. Remove views dependentes
-- 2. Adiciona preco_bloco e converte dados
-- 3. Remove preco_unitario
-- 4. Recria views com preco_bloco
--
-- Depois: reinicie a aplicação Streamlit
-- ================================================================
