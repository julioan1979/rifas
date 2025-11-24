-- Script de Migração: Pagamentos Diretos por Bloco
-- Data: 2025-11-24
-- Descrição: Refatoração para permitir pagamentos diretos sem necessidade de registar vendas
-- IMPORTANTE: Este script migra dados existentes

-- =============================================================================
-- PARTE 1: ADICIONAR NOVOS CAMPOS
-- =============================================================================

-- Adicionar bloco_id (referência direta ao bloco)
ALTER TABLE pagamentos ADD COLUMN IF NOT EXISTS bloco_id UUID REFERENCES blocos_rifas(id) ON DELETE CASCADE;

-- Adicionar quantidade de rifas vendidas do bloco
ALTER TABLE pagamentos ADD COLUMN IF NOT EXISTS quantidade_rifas INTEGER CHECK (quantidade_rifas >= 0);

-- Criar índice para performance
CREATE INDEX IF NOT EXISTS idx_pagamentos_bloco ON pagamentos(bloco_id);

-- Adicionar comentários
COMMENT ON COLUMN pagamentos.bloco_id IS 'Referência direta ao bloco de rifas (novo fluxo sem vendas)';
COMMENT ON COLUMN pagamentos.quantidade_rifas IS 'Quantidade de rifas vendidas do bloco';

-- =============================================================================
-- PARTE 2: MIGRAR DADOS EXISTENTES (vendas → blocos)
-- =============================================================================

-- Preencher bloco_id e quantidade_rifas baseado nas vendas existentes
UPDATE pagamentos p
SET 
    bloco_id = v.bloco_id,
    quantidade_rifas = v.quantidade
FROM vendas v
WHERE p.venda_id = v.id
  AND p.bloco_id IS NULL;

-- =============================================================================
-- PARTE 3: ATUALIZAR CONSTRAINTS
-- =============================================================================

-- Tornar venda_id opcional (NULL permitido) para novos pagamentos
ALTER TABLE pagamentos ALTER COLUMN venda_id DROP NOT NULL;

-- Adicionar constraint: pelo menos um deve existir (venda_id OU bloco_id)
ALTER TABLE pagamentos ADD CONSTRAINT check_venda_ou_bloco 
    CHECK (venda_id IS NOT NULL OR bloco_id IS NOT NULL);

-- =============================================================================
-- PARTE 4: ATUALIZAR VIEW DE STATUS DE CANHOTOS
-- =============================================================================

-- Recriar view para suportar ambos os fluxos (vendas legado + blocos novo)
CREATE OR REPLACE VIEW vw_status_canhotos_escuteiro AS
SELECT 
    e.id as escuteiro_id,
    e.nome as escuteiro_nome,
    COALESCE(SUM(p.canhotos_esperados), 0) as total_canhotos_esperados,
    COALESCE(SUM(p.canhotos_entregues), 0) as total_canhotos_entregues,
    COALESCE(SUM(p.canhotos_esperados), 0) - COALESCE(SUM(p.canhotos_entregues), 0) as canhotos_em_falta,
    CASE 
        WHEN COALESCE(SUM(p.canhotos_esperados), 0) = 0 THEN 0
        ELSE ROUND((COALESCE(SUM(p.canhotos_entregues), 0)::NUMERIC / COALESCE(SUM(p.canhotos_esperados), 1)::NUMERIC * 100), 2)
    END as percentagem_entregue
FROM escuteiros e
LEFT JOIN blocos_rifas b ON e.id = b.escuteiro_id
LEFT JOIN pagamentos p ON b.id = p.bloco_id
WHERE e.ativo = TRUE
GROUP BY e.id, e.nome
HAVING COALESCE(SUM(p.canhotos_esperados), 0) > 0
ORDER BY canhotos_em_falta DESC;

-- =============================================================================
-- PARTE 5: VIEW AUXILIAR - BLOCOS COM SALDO PENDENTE
-- =============================================================================

-- View para facilitar consultas de blocos com prestação de contas pendente
CREATE OR REPLACE VIEW vw_blocos_saldo_pendente AS
SELECT 
    b.id as bloco_id,
    b.campanha_id,
    b.escuteiro_id,
    e.nome as escuteiro_nome,
    b.numero_inicial,
    b.numero_final,
    b.preco_unitario,
    (b.numero_final - b.numero_inicial + 1) as total_rifas_bloco,
    (b.numero_final - b.numero_inicial + 1) * b.preco_unitario as valor_total_bloco,
    COALESCE(SUM(p.quantidade_rifas), 0) as total_rifas_vendidas,
    COALESCE(SUM(p.valor_pago), 0) as total_pago,
    COALESCE(SUM(p.canhotos_entregues), 0) as total_canhotos_entregues,
    (b.numero_final - b.numero_inicial + 1) * b.preco_unitario - COALESCE(SUM(p.valor_pago), 0) as saldo_pendente
FROM blocos_rifas b
LEFT JOIN escuteiros e ON b.escuteiro_id = e.id
LEFT JOIN pagamentos p ON b.id = p.bloco_id
WHERE b.escuteiro_id IS NOT NULL  -- Apenas blocos atribuídos
GROUP BY b.id, b.campanha_id, b.escuteiro_id, e.nome, b.numero_inicial, b.numero_final, b.preco_unitario
HAVING (b.numero_final - b.numero_inicial + 1) * b.preco_unitario - COALESCE(SUM(p.valor_pago), 0) > 0.01
ORDER BY e.nome, b.numero_inicial;

-- =============================================================================
-- PARTE 6: VERIFICAÇÃO DA MIGRAÇÃO
-- =============================================================================

-- Verificar migração de dados
SELECT 
    COUNT(*) as total_pagamentos,
    COUNT(venda_id) as com_venda_id,
    COUNT(bloco_id) as com_bloco_id,
    COUNT(CASE WHEN venda_id IS NULL AND bloco_id IS NULL THEN 1 END) as sem_referencia
FROM pagamentos;

-- Mostrar primeiros pagamentos migrados
SELECT 
    p.id,
    p.data_pagamento,
    p.valor_pago,
    p.quantidade_rifas,
    CASE 
        WHEN p.venda_id IS NOT NULL THEN 'Legado (venda)'
        WHEN p.bloco_id IS NOT NULL THEN 'Novo (bloco)'
        ELSE 'SEM REFERÊNCIA!'
    END as tipo,
    e.nome as escuteiro,
    CONCAT('Rifas ', b.numero_inicial, '-', b.numero_final) as bloco
FROM pagamentos p
LEFT JOIN blocos_rifas b ON p.bloco_id = b.id
LEFT JOIN escuteiros e ON b.escuteiro_id = e.id
ORDER BY p.data_pagamento DESC
LIMIT 10;

-- Ver blocos com saldo pendente (usando a nova view)
SELECT * FROM vw_blocos_saldo_pendente LIMIT 10;

-- =============================================================================
-- MENSAGENS FINAIS
-- =============================================================================

DO $$ 
BEGIN
    RAISE NOTICE '✅ Migração concluída com sucesso!';
    RAISE NOTICE '';
    RAISE NOTICE '📋 Resumo das alterações:';
    RAISE NOTICE '   - Campo bloco_id adicionado à tabela pagamentos';
    RAISE NOTICE '   - Campo quantidade_rifas adicionado';
    RAISE NOTICE '   - Dados existentes migrados de vendas → blocos';
    RAISE NOTICE '   - venda_id agora é opcional (NULL permitido)';
    RAISE NOTICE '   - View vw_blocos_saldo_pendente criada';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Próximos passos:';
    RAISE NOTICE '   1. Atualizar aplicação Streamlit para usar bloco_id';
    RAISE NOTICE '   2. Testar criação de novos pagamentos';
    RAISE NOTICE '   3. Depois de validado, considerar deprecar tabela vendas';
END $$;
