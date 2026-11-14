-- GK-16: pagamento simulado e entrega das chaves do pedido.
-- O histórico de status e a validação das transições pertencem à GK-13.
alter table vendas.pedidos drop constraint pedidos_status_check;
alter table vendas.pedidos add constraint pedidos_status_check
    check (status in ('aguardando_pagamento', 'pago', 'entregue', 'cancelado'));
alter table vendas.pedidos add column entregue_em timestamptz;

create table vendas.pagamentos (
    id bigint generated always as identity primary key,
    pedido_id bigint not null unique references vendas.pedidos (id),
    metodo text not null check (metodo in ('cartao', 'pix', 'boleto')),
    status text not null check (status in ('aprovado', 'recusado')),
    valor numeric(10,2) not null check (valor >= 0),
    criado_em timestamptz not null default now()
);

do $$
begin
    if exists (select from pg_roles where rolname = 'gamekeys_equipe') then
        grant select, insert, update, delete on vendas.pagamentos to gamekeys_equipe;
        grant usage, select on sequence vendas.pagamentos_id_seq to gamekeys_equipe;
    end if;
end;
$$;
