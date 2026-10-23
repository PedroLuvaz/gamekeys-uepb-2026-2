-- GK-57 / GK-90: estrutura da Sprint 1 (cadastro, login, listagem e detalhe de jogos).
-- Compra, pedidos e chaves de ativação ficam para as próximas releases (schema vendas).

create schema if not exists core;
create schema if not exists catalogo;

create or replace function core.definir_atualizado_em() returns trigger
language plpgsql as $$
begin
    new.atualizado_em := now();
    return new;
end;
$$;

-- core: contas de acesso -------------------------------------------------------

create table core.usuarios (
    id              bigint generated always as identity primary key,
    nome            text        not null check (length(btrim(nome)) between 2 and 120),
    email           text        not null check (email ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
    -- Hash bcrypt gerado pela API (GK-7): sempre 60 caracteres começando por $2a$, $2b$ ou $2y$.
    senha_hash      text        not null check (senha_hash ~ '^\$2[aby]\$\d{2}\$.{53}$'),
    data_nascimento date        not null check (data_nascimento >= date '1900-01-01'),
    perfil          text        not null default 'cliente'
                                check (perfil in ('cliente', 'administrador')),
    ativo           boolean     not null default true,
    criado_em       timestamptz not null default now(),
    atualizado_em   timestamptz not null default now()
);

-- E-mail único sem diferenciar maiúsculas: Ana@x.com e ana@x.com são a mesma conta.
create unique index usuarios_email_unico on core.usuarios (lower(email));

create trigger usuarios_atualizado_em before update on core.usuarios
    for each row execute function core.definir_atualizado_em();

-- catalogo: jogos à venda ------------------------------------------------------

create table catalogo.categorias (
    id    bigint generated always as identity primary key,
    nome  text not null unique check (length(btrim(nome)) between 2 and 60),
    slug  text not null unique check (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$')
);

create table catalogo.jogos (
    id                    bigint generated always as identity primary key,
    categoria_id          bigint        not null references catalogo.categorias (id),
    slug                  text          not null unique
                                        check (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
    nome                  text          not null check (length(btrim(nome)) between 1 and 150),
    descricao             text          not null,
    preco                 numeric(10, 2) not null check (preco >= 0),
    plataforma            text          not null,
    classificacao         text          not null
                                        check (classificacao in ('L', '10', '12', '14', '16', '18')),
    capa_url              text,
    -- Disponibilidade da Sprint 1: contador simples. Zero = Esgotado (GK-9, cenário 2).
    -- Quando as chaves virarem tabela própria (vendas), este campo passa a ser calculado.
    chaves_disponiveis    integer       not null default 0 check (chaves_disponiveis >= 0),
    ativo                 boolean       not null default true,
    criado_em             timestamptz   not null default now(),
    atualizado_em         timestamptz   not null default now()
);

create index jogos_categoria on catalogo.jogos (categoria_id);
-- Listagem paginada só de jogos ativos, em ordem de nome (GK-9).
create index jogos_ativos_por_nome on catalogo.jogos (nome, id) where ativo;

create trigger jogos_atualizado_em before update on catalogo.jogos
    for each row execute function core.definir_atualizado_em();
