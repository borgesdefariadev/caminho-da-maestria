-- ===========================================================================
-- Pendencia #10 (14/11): limpar a coluna antiga
--
-- A coluna `fragmentos_facis` era a versao ANTIGA do contador de
-- "Fragmento do Vazio Disperso" (hoje e `fragmento_vazio_disperso`).
-- O app ja a ignorava; aqui ela e removida de vez.
--
-- ⚠ O statement e idempotente: pode rodar varias vezes sem erro.
-- (Se a coluna ja nao existir, nao acontece nada.)
-- ===========================================================================

alter table public.user_characters
  drop column if exists fragmentos_facis;

-- conferindo as colunas que sobraram:
select column_name, data_type
  from information_schema.columns
 where table_schema = 'public'
   and table_name = 'user_characters'
 order by column_name;
