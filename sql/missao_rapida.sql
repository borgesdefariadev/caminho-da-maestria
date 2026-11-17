-- ===========================================================================
-- Pendencia #4 (14/11): Missoes Rapida
--
-- O botao "Missao Rapida" abre um painel para marcar as dungeons semanais
-- de qualquer personagem sem abrir a tela de edicao. O painel tambem
-- lembra o ULTIMO PERSONAGEM usado (para ja abrir nele).
--
-- Rode este SQL no Supabase (SQL Editor). Sem as colunas o app funciona
-- normalmente: o ultimo personagem so fica salvo nesta sessao.
-- ===========================================================================

alter table public.user_profiles
  add column if not exists missao_rapida boolean default false;

alter table public.user_profiles
  add column if not exists missao_rapida_personagem text;

-- conferindo:
select id, username, missao_rapida, missao_rapida_personagem
  from public.user_profiles;
