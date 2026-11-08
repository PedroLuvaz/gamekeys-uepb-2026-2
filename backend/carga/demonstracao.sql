-- GK-91: carga de demonstração idempotente (pode rodar quantas vezes quiser).
-- Jogos fictícios: 23 ativos (um esgotado) e 1 inativo, para testar GK-9 e GK-10.

insert into catalogo.categorias (nome, slug) values
    ('Ação', 'acao'),
    ('Aventura', 'aventura'),
    ('RPG', 'rpg'),
    ('Estratégia', 'estrategia'),
    ('Esportes', 'esportes'),
    ('Corrida', 'corrida'),
    ('Terror', 'terror'),
    ('Indie', 'indie')
on conflict (slug) do update set nome = excluded.nome;

insert into catalogo.jogos
    (categoria_id, slug, nome, descricao, preco, plataforma, classificacao,
     chaves_disponiveis, ativo)
select c.id, j.slug, j.nome, j.descricao, j.preco, j.plataforma, j.classificacao,
       j.chaves_disponiveis, j.ativo
from (values
    ('acao', 'lamina-do-sertao', 'Lâmina do Sertão', 'Ação em mundo aberto no agreste.', 149.90, 'PC', '16', 40, true),
    ('acao', 'cidade-de-neon', 'Cidade de Neon', 'Perseguições noturnas numa metrópole futurista.', 199.90, 'PC', '18', 25, true),
    ('acao', 'esquadrao-zero', 'Esquadrão Zero', 'Tiro tático em equipe.', 89.90, 'PC', '16', 60, true),
    ('aventura', 'ilha-do-farol', 'Ilha do Farol', 'Exploração e quebra-cabeças numa ilha isolada.', 59.90, 'PC', '10', 30, true),
    ('aventura', 'trilhas-da-serra', 'Trilhas da Serra', 'Aventura de escalada e sobrevivência.', 79.90, 'PC', '12', 18, true),
    ('aventura', 'reliquia-perdida', 'Relíquia Perdida', 'Caça ao tesouro em ruínas antigas.', 69.90, 'PC', '12', 22, true),
    ('rpg', 'cronicas-de-borborema', 'Crônicas de Borborema', 'RPG de fantasia com escolhas que mudam a história.', 179.90, 'PC', '14', 35, true),
    ('rpg', 'reino-de-cristal', 'Reino de Cristal', 'RPG tático por turnos.', 129.90, 'PC', '12', 12, true),
    ('rpg', 'herdeiros-do-vento', 'Herdeiros do Vento', 'RPG de ação cooperativo.', 99.90, 'PC', '14', 28, true),
    ('estrategia', 'imperio-de-areia', 'Império de Areia', 'Estratégia em tempo real no deserto.', 119.90, 'PC', '12', 20, true),
    ('estrategia', 'colonia-orbital', 'Colônia Orbital', 'Construa e administre uma estação espacial.', 89.90, 'PC', 'L', 45, true),
    ('estrategia', 'general-de-bolso', 'General de Bolso', 'Estratégia rápida em partidas de 15 minutos.', 29.90, 'PC', '10', 80, true),
    ('esportes', 'gol-de-placa', 'Gol de Placa', 'Futebol arcade com campeonato online.', 199.90, 'PC', 'L', 50, true),
    ('esportes', 'quadra-livre', 'Quadra Livre', 'Basquete de rua 3x3.', 49.90, 'PC', 'L', 33, true),
    ('esportes', 'onda-perfeita', 'Onda Perfeita', 'Surfe com física realista.', 39.90, 'PC', 'L', 15, true),
    ('corrida', 'asfalto-quente', 'Asfalto Quente', 'Corridas de rua com carros personalizados.', 159.90, 'PC', '10', 26, true),
    ('corrida', 'rali-do-cariri', 'Rali do Cariri', 'Rali em estradas de terra do Nordeste.', 69.90, 'PC', 'L', 19, true),
    ('terror', 'casa-14', 'Casa 14', 'Terror psicológico em primeira pessoa.', 79.90, 'PC', '18', 21, true),
    ('terror', 'hospital-abandonado', 'Hospital Abandonado', 'Sobrevivência com recursos escassos.', 59.90, 'PC', '16', 14, true),
    ('indie', 'pixel-e-cafe', 'Pixel e Café', 'Simulador aconchegante de cafeteria.', 24.90, 'PC', 'L', 70, true),
    ('indie', 'jardim-silencioso', 'Jardim Silencioso', 'Quebra-cabeças narrativo.', 19.90, 'PC', 'L', 55, true),
    ('indie', 'robo-saudade', 'Robô Saudade', 'Plataforma 2D sobre um robô em busca de casa.', 34.90, 'PC', 'L', 42, true),
    -- Esgotado: ativo, mas sem chaves (GK-9, cenário 2).
    ('acao', 'tempestade-de-aco', 'Tempestade de Aço', 'Combate de robôs gigantes.', 139.90, 'PC', '14', 0, true),
    -- Inativo: não aparece no catálogo nem no detalhe (GK-9 cenário 3, GK-10 cenário 2).
    ('rpg', 'lenda-esquecida', 'Lenda Esquecida', 'Jogo retirado da loja.', 49.90, 'PC', '12', 10, false)
) as j (categoria, slug, nome, descricao, preco, plataforma, classificacao,
        chaves_disponiveis, ativo)
join catalogo.categorias c on c.slug = j.categoria
on conflict (slug) do update set
    categoria_id = excluded.categoria_id,
    nome = excluded.nome,
    descricao = excluded.descricao,
    preco = excluded.preco,
    plataforma = excluded.plataforma,
    classificacao = excluded.classificacao,
    chaves_disponiveis = excluded.chaves_disponiveis,
    ativo = excluded.ativo;

-- GK-124: códigos explicitamente fictícios, somente pela carga de demonstração.
-- Conta técnica inativa: não há senha utilizável nem acesso administrativo pela API.
insert into core.usuarios (nome, email, senha_hash, data_nascimento, perfil, ativo)
values ('Carga de demonstração', 'chaves-demo@example.invalid',
        '$2b$12$' || repeat('x', 53), date '1990-01-01', 'administrador', false)
on conflict (lower(email)) do nothing;

insert into catalogo.chaves (jogo_id, codigo, cadastrada_por)
select j.id, 'GK-DEMO-SEM-VALOR-' || j.slug || '-' || n,
       (select id from core.usuarios where lower(email) = 'chaves-demo@example.invalid')
from catalogo.jogos j
cross join lateral generate_series(1, j.chaves_disponiveis) as n
where j.slug in (
    'lamina-do-sertao', 'cidade-de-neon', 'esquadrao-zero', 'ilha-do-farol',
    'trilhas-da-serra', 'reliquia-perdida', 'cronicas-de-borborema', 'reino-de-cristal',
    'herdeiros-do-vento', 'imperio-de-areia', 'colonia-orbital', 'general-de-bolso',
    'gol-de-placa', 'quadra-livre', 'onda-perfeita', 'asfalto-quente', 'rali-do-cariri',
    'casa-14', 'hospital-abandonado', 'pixel-e-cafe', 'jardim-silencioso', 'robo-saudade',
    'tempestade-de-aco', 'lenda-esquecida'
)
on conflict (codigo) do nothing;

-- Rerodar a carga não libera chaves já reservadas/vendidas nem repõe códigos consumidos.
update catalogo.jogos j set chaves_disponiveis = (
    select count(*) from catalogo.chaves c where c.jogo_id = j.id and c.status = 'disponivel'
);
