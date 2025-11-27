-- scripts/clear_all_data.sql
--
-- Limpador de dados para testes
--
-- ATENÇÃO: Faça backup antes de executar.
-- Execução recomendada: copie este conteúdo para o SQL Editor do Supabase
-- (ou execute com psql ligado ao seu projeto). Este script TRUNCATEIA todas
-- as tabelas do schema `public`, reinicia as sequences e usa CASCADE para
-- contornar constraints de FK.

-- Observações:
-- - Este script não altera objetos em schemas diferentes (ex: `auth`).
-- - Se precisar também limpar o schema `auth` (usuários), proceda com
--   cautela — normalmente não é recomendado em ambientes Supabase geridos.
-- - Se tiver tabelas que não quer truncar (ex: migrations, configurações),
--   adicione os nomes no array de exclusão abaixo.

BEGIN;

-- Trabalhamos explicitamente no schema public
SET search_path = public;

-- Lista de tabelas a excluir do truncate (adicione nomes se necessário)
-- Ex.: ('alvo_para_manter','outra_tabela')
DO $$
DECLARE
  exclude_tables TEXT[] := ARRAY[ 'spatial_ref_sys' ];
  r RECORD;
BEGIN
  FOR r IN
    SELECT tablename
    FROM pg_tables
    WHERE schemaname = 'public'
      AND tablename NOT LIKE 'pg_%'
      AND NOT (tablename = ANY (exclude_tables))
  LOOP
    RAISE NOTICE 'Truncating table: %', r.tablename;
    EXECUTE format('TRUNCATE TABLE public.%I RESTART IDENTITY CASCADE;', r.tablename);
  END LOOP;
END
$$;

COMMIT;

-- Recomenda-se VACUUM após limpeza, executável separadamente
-- VACUUM FULL;

-- Fim do script
