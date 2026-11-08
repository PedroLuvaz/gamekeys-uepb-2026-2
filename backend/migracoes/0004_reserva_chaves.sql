-- GK-15 / GK-124: reserva real, sem expor códigos antes da entrega (GK-16).
create table catalogo.chaves (
    id bigint generated always as identity primary key,
    jogo_id bigint not null references catalogo.jogos (id),
    codigo text not null unique check (length(btrim(codigo)) between 1 and 200),
    status text not null default 'disponivel'
        check (status in ('disponivel', 'reservada', 'vendida', 'invalidada')),
    cadastrada_por bigint not null references core.usuarios (id),
    criado_em timestamptz not null default now(),
    unique (id, jogo_id)
);
create index chaves_disponiveis_por_jogo on catalogo.chaves (jogo_id, id)
    where status = 'disponivel';
create index chaves_por_cadastrador on catalogo.chaves (cadastrada_por);

create table vendas.pedidos (
    id bigint generated always as identity primary key,
    usuario_id bigint not null references core.usuarios (id),
    chave_idempotencia uuid not null,
    status text not null default 'aguardando_pagamento'
        check (status in ('aguardando_pagamento', 'pago', 'cancelado')),
    valor_total numeric(10,2) not null check (valor_total >= 0),
    criado_em timestamptz not null default now(),
    pago_em timestamptz,
    cancelado_em timestamptz,
    unique (usuario_id, chave_idempotencia)
);
create table vendas.itens_pedido (
    id bigint generated always as identity primary key,
    pedido_id bigint not null references vendas.pedidos (id),
    jogo_id bigint not null references catalogo.jogos (id),
    chave_id bigint not null unique,
    preco_unitario numeric(10,2) not null check (preco_unitario >= 0),
    foreign key (chave_id, jogo_id) references catalogo.chaves (id, jogo_id)
);
create index itens_pedido_por_pedido on vendas.itens_pedido (pedido_id, jogo_id);
create index itens_pedido_por_jogo on vendas.itens_pedido (jogo_id);

-- O contador passa a refletir chaves físicas disponíveis. A migração não inventa códigos.
-- Sem carga de chaves, o catálogo fica esgotado. --carga usa apenas códigos fictícios.
update catalogo.jogos set chaves_disponiveis = 0;
create function catalogo.sincronizar_estoque_chaves() returns trigger language plpgsql as $$
declare
    variacao integer;
begin
    if TG_OP = 'UPDATE' and new.jogo_id <> old.jogo_id then
        raise exception 'Uma chave não pode mudar de jogo';
    end if;
    variacao := case when TG_OP <> 'DELETE' and new.status = 'disponivel' then 1 else 0 end
              - case when TG_OP <> 'INSERT' and old.status = 'disponivel' then 1 else 0 end;
    if variacao <> 0 then
        update catalogo.jogos set chaves_disponiveis = chaves_disponiveis + variacao
        where id = case when TG_OP = 'DELETE' then old.jogo_id else new.jogo_id end;
    end if;
    return null;
end;
$$;
create trigger chaves_sincronizar_estoque after insert or update or delete on catalogo.chaves
    for each row execute function catalogo.sincronizar_estoque_chaves();

do $$
begin
    if exists (select from pg_roles where rolname = 'gamekeys_equipe') then
        grant select, insert, update, delete on catalogo.chaves to gamekeys_equipe;
        grant usage, select on sequence catalogo.chaves_id_seq to gamekeys_equipe;
        grant select, insert, update, delete on vendas.pedidos, vendas.itens_pedido
            to gamekeys_equipe;
        grant usage, select on sequence vendas.pedidos_id_seq, vendas.itens_pedido_id_seq
            to gamekeys_equipe;
    end if;
end;
$$;
