-- GK-11 / GK-118: carrinho persistente do cliente, conforme o DER v1.0.
-- Adicionar ao carrinho não reserva nem consome chaves (GK-15).
create schema if not exists vendas;

create table vendas.carrinhos (
    id              bigint generated always as identity primary key,
    usuario_id      bigint not null unique references core.usuarios (id),
    criado_em       timestamptz not null default now(),
    atualizado_em   timestamptz not null default now()
);

create table vendas.itens_carrinho (
    carrinho_id     bigint not null references vendas.carrinhos (id) on delete cascade,
    jogo_id         bigint not null references catalogo.jogos (id),
    quantidade      integer not null default 1 check (quantidade > 0),
    adicionado_em   timestamptz not null default now(),
    primary key (carrinho_id, jogo_id)
);

-- A PK atende consultas e alterações por carrinho; este índice atende a FK do jogo.
create index itens_carrinho_por_jogo on vendas.itens_carrinho (jogo_id);

create trigger carrinhos_atualizado_em before update on vendas.carrinhos
    for each row execute function core.definir_atualizado_em();

-- A API mantém o papel restrito existente; DDL continua fora do usuário da equipe.
do $$
begin
    if exists (select from pg_roles where rolname = 'gamekeys_equipe') then
        grant usage on schema vendas to gamekeys_equipe;
        grant select, insert, update, delete on all tables in schema vendas to gamekeys_equipe;
        grant usage, select on all sequences in schema vendas to gamekeys_equipe;
        alter default privileges in schema vendas
            grant select, insert, update, delete on tables to gamekeys_equipe;
        alter default privileges in schema vendas
            grant usage, select on sequences to gamekeys_equipe;
    end if;
end;
$$;
