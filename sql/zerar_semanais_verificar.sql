-- ===========================================================================
-- CONFERIR a limpeza semanal (opcional, rode depois de criar)
--
-- Este arquivo so tem queries de LEITURA. Ele pode ser rodado quantas
-- vezes quiser e nunca mexe em nada.
-- ===========================================================================

-- 1) a tarefa agendada:
select jobid, jobname, schedule, command, active
  from cron.job
 order by jobid;

-- 2) o fuso do servidor (as 03h de Brasilia viram 06h se for UTC):
show timezone;

-- 3) o fuso POR TAREFA (so existe no pg_cron 1.4+; se nao existir, o
--    agendamento usa o fuso do servidor, que e o certo):
do $$
begin
  if exists (select 1 from information_schema.columns
              where table_schema = 'cron'
                and table_name = 'job'
                and column_name = 'timezone') then
    raise notice 'fuso da tarefa: %',
      (select timezone from cron.job where jobname = 'zerar-missoes-semanais');
  else
    raise notice 'Este pg_cron nao tem fuso por tarefa: a schedule acima '
                 'ja esta no fuso do servidor (UTC).';
  end if;
end $$;

-- 4) as execucoes anteriores (pg_cron 1.4+):
do $$
begin
  if exists (select 1 from information_schema.views
               where table_schema = 'cron'
                 and table_name = 'job_run_details') then
    raise notice 'historico: %', (
      select string_agg(format('%s -> %s', run_time, status), ', ')
        from cron.job_run_details
       where jobid = (select jobid from cron.job
                       where jobname = 'zerar-missoes-semanais')
       order by run_time desc limit 5));
  else
    raise notice 'Este pg_cron nao tem a tabela de historico.';
  end if;
end $$;

-- 5) quantas marcacoes ativas existem agora (deve dar 0 depois da limpeza):
select
  count(*) filter (where fornalha_infernal)          as fornalha_infernal,
  count(*) filter (where altar_da_runha)             as altar_da_runha,
  count(*) filter (where torre_das_ilusoes_semanal) as torre_das_ilusoes_semanal,
  count(*) filter (where void_123)                  as void_123,
  count(*) filter (where void_4)                    as void_4,
  count(*) filter (where caminho_abissal)            as caminho_abissal,
  count(*) filter (where terra_do_julgamento)        as terra_do_julgamento
from public.user_semanais;

-- 6) TESTE NA MAO (zera agora e devolve quantas linhas mudou):
--    select public.zerar_semanais();


-- ===========================================================================
-- COMO REMOVER o agendamento
-- ===========================================================================
--   select cron.unschedule('zerar-missoes-semanais');
--   drop function if exists public.zerar_semanais();
