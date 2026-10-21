-- Papel usado pela API e pelos integrantes no dia a dia: lê e grava dados, mas não altera a
-- estrutura. Mudança de estrutura entra só por migração, aplicada pelo dono do banco.
-- O papel e a senha são criados fora do repositório (a senha não é versionada).

do $$
begin
    if exists (select from pg_roles where rolname = 'gamekeys_equipe') then
        execute format('grant connect on database %I to gamekeys_equipe', current_database());
        grant usage on schema core, catalogo to gamekeys_equipe;
        grant select, insert, update, delete on all tables in schema core, catalogo
            to gamekeys_equipe;
        grant usage, select on all sequences in schema core, catalogo to gamekeys_equipe;
        alter default privileges in schema core, catalogo
            grant select, insert, update, delete on tables to gamekeys_equipe;
        alter default privileges in schema core, catalogo
            grant usage, select on sequences to gamekeys_equipe;
    end if;
end;
$$;
