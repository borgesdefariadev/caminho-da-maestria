-- ===========================================================================
-- Pendencia #7 (15/11): o PERFIL do usuario
--
-- O perfil fica no espaco vago do hero ("Caminho da Maestria"):
--   [foto]  Lv. <Nick> <Nivel do Chaser>   + o icone do nivel
--
-- Estas colunas sao OPCIONAIS: se nao existirem, o app funciona normal
-- (so o nick e a foto nao ficam guardados entre sessoes).
-- ===========================================================================

alter table public.user_profiles
  add column if not exists nick text;

-- a foto do usuario (PNG em base64, 128x128 -> ~20-40 KB)
alter table public.user_profiles
  add column if not exists avatar text;

-- conferindo:
select id, username, nick,
       (avatar is not null) as tem_avatar
  from public.user_profiles;
