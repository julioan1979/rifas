-- Script para limpar todos os dados das tabelas mantendo o schema
-- Execute este SQL no Supabase SQL Editor
-- ATENÇÃO: Isto vai apagar TODOS os dados das tabelas!

-- Desabilitar triggers temporariamente (se necessário)
SET session_replication_role = replica;

-- Limpar tabelas na ordem correta (respeitando foreign keys)
-- Primeiro as tabelas dependentes, depois as principais

-- 1. Limpar pagamentos (depende de vendas e blocos_rifas)
TRUNCATE TABLE pagamentos RESTART IDENTITY CASCADE;

-- 2. Limpar devoluções (depende de escuteiros e blocos_rifas)
TRUNCATE TABLE devolucoes RESTART IDENTITY CASCADE;

-- 3. Limpar vendas (depende de escuteiros e blocos_rifas)
TRUNCATE TABLE vendas RESTART IDENTITY CASCADE;

-- 4. Limpar blocos_rifas (depende de escuteiros e campanhas)
TRUNCATE TABLE blocos_rifas RESTART IDENTITY CASCADE;

-- 5. Limpar escuteiros (tabela independente)
TRUNCATE TABLE escuteiros RESTART IDENTITY CASCADE;

-- 6. Limpar campanhas (tabela independente)
TRUNCATE TABLE campanhas RESTART IDENTITY CASCADE;

-- Reabilitar triggers
SET session_replication_role = DEFAULT;

-- Verificar que todas as tabelas foram limpas
SELECT 'pagamentos' as tabela, COUNT(*) as registos FROM pagamentos
UNION ALL
SELECT 'devolucoes' as tabela, COUNT(*) as registos FROM devolucoes
UNION ALL
SELECT 'vendas' as tabela, COUNT(*) as registos FROM vendas
UNION ALL
SELECT 'blocos_rifas' as tabela, COUNT(*) as registos FROM blocos_rifas
UNION ALL
SELECT 'escuteiros' as tabela, COUNT(*) as registos FROM escuteiros
UNION ALL
SELECT 'campanhas' as tabela, COUNT(*) as registos FROM campanhas;

-- Mensagem de sucesso
SELECT 'Todos os dados foram limpos com sucesso! As tabelas estão vazias e prontas para novos registos.' as resultado;
