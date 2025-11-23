-- SQL para adicionar colunas de controle de pagamentos e canhotos à tabela blocos_rifas
-- Execute este SQL no Supabase SQL Editor

-- Adicionar colunas para controle de pagamentos
ALTER TABLE blocos_rifas ADD COLUMN IF NOT EXISTS valor_a_pagar DECIMAL(10, 2);
ALTER TABLE blocos_rifas ADD COLUMN IF NOT EXISTS valor_pago DECIMAL(10, 2) DEFAULT 0;
ALTER TABLE blocos_rifas ADD COLUMN IF NOT EXISTS data_pagamento TIMESTAMP WITH TIME ZONE;
ALTER TABLE blocos_rifas ADD COLUMN IF NOT EXISTS metodo_pagamento TEXT;
ALTER TABLE blocos_rifas ADD COLUMN IF NOT EXISTS observacoes_pagamento TEXT;

-- Adicionar colunas para controle de canhotos/rifas
ALTER TABLE blocos_rifas ADD COLUMN IF NOT EXISTS rifas_vendidas INTEGER DEFAULT 0;
ALTER TABLE blocos_rifas ADD COLUMN IF NOT EXISTS canhotos_devolvidos BOOLEAN DEFAULT FALSE;
ALTER TABLE blocos_rifas ADD COLUMN IF NOT EXISTS data_devolucao_canhotos TIMESTAMP WITH TIME ZONE;
ALTER TABLE blocos_rifas ADD COLUMN IF NOT EXISTS observacoes_canhotos TEXT;

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_pagamento ON blocos_rifas(data_pagamento);
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_canhotos ON blocos_rifas(canhotos_devolvidos);

-- Atualizar valor_a_pagar para blocos existentes (baseado no total de rifas * preço)
UPDATE blocos_rifas
SET valor_a_pagar = (numero_final - numero_inicial + 1) * preco_unitario
WHERE valor_a_pagar IS NULL;

-- Comentários nas colunas para documentação
COMMENT ON COLUMN blocos_rifas.valor_a_pagar IS 'Valor total que o escuteiro deve pagar pelo bloco';
COMMENT ON COLUMN blocos_rifas.valor_pago IS 'Valor que o escuteiro já pagou';
COMMENT ON COLUMN blocos_rifas.data_pagamento IS 'Data em que o escuteiro pagou';
COMMENT ON COLUMN blocos_rifas.metodo_pagamento IS 'Método utilizado para pagamento (Dinheiro, Transferência, etc)';
COMMENT ON COLUMN blocos_rifas.rifas_vendidas IS 'Número de rifas que o escuteiro conseguiu vender';
COMMENT ON COLUMN blocos_rifas.canhotos_devolvidos IS 'Se o escuteiro já devolveu os canhotos das rifas vendidas';
COMMENT ON COLUMN blocos_rifas.data_devolucao_canhotos IS 'Data em que os canhotos foram devolvidos';
COMMENT ON COLUMN blocos_rifas.observacoes_pagamento IS 'Observações sobre o pagamento';
COMMENT ON COLUMN blocos_rifas.observacoes_canhotos IS 'Observações sobre a devolução dos canhotos';

-- Criar view para relatório de situação dos blocos
CREATE OR REPLACE VIEW vw_situacao_blocos AS
SELECT 
    b.id,
    b.numero_inicial,
    b.numero_final,
    (b.numero_final - b.numero_inicial + 1) as total_rifas,
    b.preco_unitario,
    b.valor_a_pagar,
    b.valor_pago,
    (b.valor_a_pagar - COALESCE(b.valor_pago, 0)) as saldo_pendente,
    b.data_pagamento,
    b.metodo_pagamento,
    b.rifas_vendidas,
    b.canhotos_devolvidos,
    b.data_devolucao_canhotos,
    e.nome as escuteiro_nome,
    e.email as escuteiro_email,
    e.telefone as escuteiro_telefone,
    c.nome as campanha_nome,
    b.seccao,
    CASE 
        WHEN b.valor_pago >= b.valor_a_pagar AND b.canhotos_devolvidos = TRUE THEN '✅ Completo'
        WHEN b.valor_pago >= b.valor_a_pagar THEN '💰 Pago (faltam canhotos)'
        WHEN b.canhotos_devolvidos = TRUE THEN '📋 Canhotos OK (falta pagamento)'
        ELSE '⏳ Pendente'
    END as situacao
FROM blocos_rifas b
LEFT JOIN escuteiros e ON b.escuteiro_id = e.id
LEFT JOIN campanhas c ON b.campanha_id = c.id
WHERE b.escuteiro_id IS NOT NULL
ORDER BY b.numero_inicial;

-- Comentário na view
COMMENT ON VIEW vw_situacao_blocos IS 'Visão consolidada da situação de pagamentos e canhotos de cada bloco atribuído';
