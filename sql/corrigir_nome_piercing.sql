-- ===========================================================================
-- Corrigir o nome do PIERCING
--
-- O nome certo e "Piercing do Outro Mundo do Caos" (antes estava
-- "Piercing da Dimensão do Caos").
--
-- ⚠ **A COR**: no app a cor do acessorio vem das REGRAS do codigo
-- (card_personagem.py), que casam por TRECHO do nome. Com o nome novo a
-- regra "outro mundo do caos" passa a casar e o Piercing fica
-- VERMELHO \u2014 igual ao "Brinco do Outro Mundo do Caos" (que e o mesmo
-- item do jogo). Antes ("Dimensao do Caos") nenhuma regra casava e ele
-- ficava sem cor.
--
-- Como usar: SQL Editor do Supabase > cole > Run.
-- ===========================================================================

-- 1) conferindo como esta hoje:
select coalesce(piercing, '(vazio)') as piercing, count(*)
  from public.user_acessorios_titulo
 where piercing is not null and piercing <> ''
 group by piercing
 order by count(*) desc;

-- 2) a correcao (todas as contas):
update public.user_acessorios_titulo
   set piercing = 'Piercing do Outro Mundo do Caos'
 where piercing = 'Piercing da Dimensão do Caos';

-- 3) conferindo depois:
select coalesce(piercing, '(vazio)') as piercing, count(*)
  from public.user_acessorios_titulo
 where piercing is not null and piercing <> ''
 group by piercing
 order by count(*) desc;

-- 4) (opcional) ver o quanto de cada acessorio tem no total:
select
  count(*) filter (where anel <> '')          as anel,
  count(*) filter (where brinco <> '')        as brinco,
  count(*) filter (where piercing <> '')      as piercing,
  count(*) filter (where tornozeleira <> '')  as tornozeleira,
  count(*) filter (where titulo <> '')        as titulo
from public.user_acessorios_titulo;
