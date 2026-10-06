# GameKeys

Loja web de jogos digitais vendidos por chave de ativação.
Disciplina Gerência de Projeto — UEPB, 2026.2 — Prof.ª Ana Isabella Muniz Leite.

## Problema

Quem vende chaves de ativação precisa garantir que a mesma chave nunca seja entregue a dois compradores.
O GameKeys controla o estoque de chaves, os pedidos e a entrega, mantendo separados os dados de cada usuário.

## Perfis

- **Visitante:** navega e busca no catálogo.
- **Cliente:** compra (pagamento simulado) e acessa suas chaves.
- **Administrador:** cadastra jogos e chaves e acompanha os pedidos.

## Equipe

| Integrante | Papel na Release 1 |
|---|---|
| Pedro Lucas Vaz de Andrade | Product Owner e DevOps |
| Wagner Tiburcio da Silva Junior | QA |
| Rodrigo Almeida Gomes | Scrum Master |

Os papéis mudam ao fim de cada release. Quem é PO também é DevOps.

## Responsabilidades

- **PO:** responsável pelo produto. Cadastra e prioriza o backlog, define o objetivo de cada sprint, aceita ou recusa as entregas e apresenta o produto.
- **Scrum Master:** cuida do processo. Organiza as cerimônias, mantém o Jira em dia, registra atas e riscos e garante que os documentos estejam acessíveis.
- **QA:** cuida da qualidade. Planeja e executa os testes, registra bugs e confere se cada história atende aos critérios de aceite e à Definition of Done.
- **DevOps:** cuida do repositório, do pipeline de CI e do ambiente de desenvolvimento.

## Releases

| Release | Até | O que será entregue |
|---|---|---|
| 1 | 29/10 | Cadastro, login e catálogo navegável |
| 2 | 26/11 | Compra completa: carrinho, pagamento simulado e entrega da chave |
| 3 | 22/12 | Biblioteca, cancelamento, busca e administração de jogos e chaves |
| 4 | 18/02 | Painel de pedidos, indicadores, avaliações e apresentação final |

## Gestão

O backlog, as sprints e as releases ficam no Jira.

## Documentos

Pasta no Google Drive: https://drive.google.com/drive/folders/1m_lYvzaFOp2JcKruRJZfTtRMfyEVXKPt

- [Proposta](https://docs.google.com/document/d/1cvCfppfFUyMrlR5vKW8kzUz7ld3SvadsuaLUz4l3nRc/edit)
- [Definition of Ready e Definition of Done](https://docs.google.com/document/d/1_e2WubM4swRMEKqpYfDwmfMXpO8Ydn_ZSthgrmniWns/edit)
- [Plano de Qualidade](https://docs.google.com/document/d/1-ida9PUMd68Y-JBPOhpodR9vXwBqo3jekPJESSyKMBU/edit)
- [Plano da Sprint 1](https://docs.google.com/document/d/1e_3jWniPo1ayAMduJLj30WU7ZRu9x5FYl6XWfpK0WSM/edit)

Uma cópia em .docx de cada um fica na pasta `docs/`.

## Tecnologias

Python 3.12 com FastAPI, PostgreSQL, React com TypeScript e GitHub Actions.

## Como rodar o back-end

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # no Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn app.main:app --reload
```

A API sobe em http://127.0.0.1:8000 (verificação em `/saude`).

## Commits e branches

- Branch: `GK-<número>-descricao-curta`
- Commit: `tipo: GK-<número> descrição` (ex.: `feat: GK-12 cadastro de cliente`)
- Toda mudança entra por pull request revisado por outro integrante.
