-- ============================================================================
-- Controle Grand Chase - novos campos dos personagens
-- Rode no SQL Editor do Supabase (uma vez).
-- O app detecta as colunas automaticamente e avisa se ainda faltarem.
-- ============================================================================

alter table public.user_characters
  add column if not exists nucleos_dimensionais       integer default 0,
  add column if not exists fragmento_vazio_disperso   integer default 0,
  add column if not exists libertacao_nucleos         integer default 0,
  add column if not exists libertacao_epicos          integer default 0;

-- (opcional) A coluna da Torre das Ilusoes semanal, caso ainda nao exista:
-- alter table public.user_semanais
--   add column if not exists torre_das_ilusoes boolean default false;
