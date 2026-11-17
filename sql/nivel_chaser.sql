-- ===========================================================================
-- Pendencia #3 (14/11): Nivel do Chaser no banco
--
-- Um valor POR CONTA (vale para todos os 25 personagens). O app grava o
-- mesmo valor em todas as linhas de user_characters.
--
-- Rode este SQL no Supabase (SQL Editor) ANTES de usar a tela.
-- Sem a coluna o app continua funcionando (usa o valor padrao 385), mas o
-- nivel nao e gravado.
-- ===========================================================================

alter table public.user_characters
  add column if not exists nivel_chaser bigint default 385;

-- (opcional) um indice nao e necessario: a coluna nao e filtrada.

-- conferindo:
select character_name, nivel_chaser
  from public.user_characters
 where user_id = 'adc651b2-7045-46f5-94ff-ca7f623447b4'
 order by character_name
 limit 5;
