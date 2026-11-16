-- GK-13: trilha transacional das mudanças de status do pedido.
create table vendas.historico_status_pedido (
    id bigint generated always as identity primary key,
    pedido_id bigint not null references vendas.pedidos (id) on delete cascade,
    status_anterior text,
    status_novo text not null,
    responsavel_id bigint not null references core.usuarios (id),
    alterado_em timestamptz not null default now(),
    check (status_anterior is null or status_anterior in
        ('aguardando_pagamento', 'pago', 'entregue', 'cancelado')),
    check (status_novo in ('aguardando_pagamento', 'pago', 'entregue', 'cancelado')),
    check (status_anterior is null or status_anterior <> status_novo)
);

create index historico_status_por_pedido
    on vendas.historico_status_pedido (pedido_id, id);

do $$
begin
    if exists (select from pg_roles where rolname = 'gamekeys_equipe') then
        revoke update, delete on vendas.historico_status_pedido from gamekeys_equipe;
        grant select, insert on vendas.historico_status_pedido to gamekeys_equipe;
        grant usage, select on sequence vendas.historico_status_pedido_id_seq
            to gamekeys_equipe;
    end if;
end;
$$;
