"""
Database schema documentation for the raffle management system

🔥 IMPORTANTE: Use o arquivo COMPLETE_SCHEMA.sql para criar o schema completo!

Este arquivo contém apenas documentação. Para criar as tabelas no Supabase:
1. Abra o arquivo COMPLETE_SCHEMA.sql
2. Copie TODO o conteúdo
3. Cole no SQL Editor do Supabase
4. Execute (clique em "Run")

==============================================
ESTRUTURA DO BANCO DE DADOS
==============================================

📋 6 TABELAS PRINCIPAIS:

1. campanhas
   - Armazena campanhas de rifas (ex: Natal2025, Páscoa2026)
   - Campos: id, nome, descricao, data_inicio, data_fim, ativa, created_at
   - Uma campanha pode estar ativa ou inativa
   - Pode ter múltiplas campanhas ativas simultaneamente

2. escuteiros
   - Armazena dados dos escuteiros que vendem rifas
   - Campos: id, nome, email, telefone, ativo, created_at
   - Escuteiros podem ser marcados como ativos/inativos

3. blocos_rifas
   - Armazena blocos de rifas atribuídos a escuteiros
   - Campos: id, campanha_id, nome, numero_inicial, numero_final, 
            preco_unitario, escuteiro_id, seccao, data_atribuicao, 
            estado, created_at
   - Estados possíveis: disponivel, atribuido, vendido, devolvido
   - Secções: Lobitos, Exploradores, Pioneiros, Caminheiros

4. vendas (LEGADO - mantido para compatibilidade)
   - Mantida apenas para dados históricos
   - Novos registros devem ir direto para tabela pagamentos
   - Campos: id, escuteiro_id, bloco_id, quantidade, valor_total,
            data_venda, observacoes, created_at

5. pagamentos ⭐ (PRINCIPAL)
   - Armazena pagamentos/prestações de contas dos escuteiros
   - Suporta DOIS fluxos:
     * NOVO (recomendado): bloco_id diretamente
     * LEGADO: venda_id (dados antigos)
   - Campos: id, venda_id, bloco_id, quantidade_rifas, valor_pago,
            data_pagamento, metodo_pagamento, referencia, observacoes,
            canhotos_entregues, canhotos_esperados, 
            data_entrega_canhotos, observacoes_canhotos, created_at
   - Controla também entrega de canhotos (comprovantes físicos)

6. devolucoes
   - Armazena devoluções de rifas não vendidas
   - Campos: id, escuteiro_id, bloco_id, quantidade, motivo,
            data_devolucao, created_at

==============================================
VIEWS DISPONÍVEIS (relatórios automáticos)
==============================================

1. vw_vendas_por_escuteiro
   - Resumo de vendas e pagamentos por escuteiro

2. vw_blocos_status
   - Resumo do estado dos blocos por campanha

3. vw_pagamentos_por_bloco
   - Resumo de pagamentos e status por bloco (novo fluxo)

4. vw_canhotos_pendentes
   - Lista de escuteiros com canhotos pendentes de entrega

==============================================
FUNCIONALIDADES AUTOMÁTICAS
==============================================

✅ Trigger automático para atualizar estado do bloco:
   - Quando pagamentos são registrados
   - Estado muda automaticamente: disponivel → atribuido → vendido

✅ Índices otimizados para queries rápidas

✅ Row Level Security (RLS) ativado

✅ Constraints para garantir integridade dos dados

==============================================
COMO USAR
==============================================

1. Execute o arquivo COMPLETE_SCHEMA.sql no Supabase
2. Configure variáveis de ambiente:
   - SUPABASE_URL
   - SUPABASE_KEY
3. Execute: streamlit run app.py
4. Crie uma campanha
5. Adicione escuteiros
6. Crie blocos de rifas
7. Atribua blocos aos escuteiros
8. Registe pagamentos conforme vendem

==============================================
FLUXO RECOMENDADO
==============================================

Campanhas → Escuteiros → Blocos → Atribuição → Pagamentos → Canhotos

❌ NÃO use mais a tabela 'vendas'
✅ Use pagamentos diretos com bloco_id

"""

def create_tables_sql():
    """
    Returns the SQL commands to create all tables
    Use this in Supabase SQL Editor
    """
    return """
    -- Copy the SQL commands above and run them in Supabase SQL Editor
    -- This will create all necessary tables, indexes, and views
    """
