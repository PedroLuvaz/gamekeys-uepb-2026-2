-- GK-136: permite conferir o estado do banco sem usar a credencial do proprietário no CI.
-- Não autoriza inserir, editar ou apagar o histórico de migrações.
do $$
begin
    if exists (select from pg_roles where rolname = 'gamekeys_equipe') then
        grant select on public.migracoes_aplicadas to gamekeys_equipe;
    end if;
end;
$$;
