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
- [Registro de Riscos](https://docs.google.com/document/d/1oSEonzAulY87ssaz6TzGdNFTCswyxCbSTtn1_LtVj8g/edit)
- [Drivers Arquiteturais](https://docs.google.com/document/d/10U9jLK5_RB2MYaO2PXomXmlro3rJidd3Zxs0wIVX7TE/edit)

Uma cópia em .docx de cada um fica na pasta `docs/`.

Documentos nos templates da disciplina (no Drive, em `docs/` e anexados no Jira):

- [DoD de Sprint e Release](https://drive.google.com/file/d/1Mr-6oT0po8POyaRGD75hCEQjqA-TzI4Q/view): Definition of Done de sprint e de release (anexo da GK-38)
- [Análise de Riscos Baseada em Defeitos](https://drive.google.com/file/d/1-V-hE9YR3ZEPaU3jr15yCcHHMzlV64ej/view): 9 riscos, 3 atributos de qualidade × 3 integrantes (anexo do épico GK-64)
- [Plano de Qualidade (planilha)](https://drive.google.com/file/d/1oFIoArPRYugK9tnwQFsLC75rlv7r4TiK/view): itens de qualidade com métrica, meta, forma de medição e responsável (anexo da GK-36)
- [Plano de Teste](https://drive.google.com/file/d/1qXmh7E59SYTYdfxeKzZtY5n8A1jDZK6s/view): escopo, estratégia, casos de teste ligados às US e cronograma (anexo da GK-36)

A DoR e a DoD de cada história ficam no modelo de US, dentro de cada história no Jira.

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

- Branch: `<tipo>/GK-<número>-descricao-curta` (ex.: `feature/GK-12-carrinho-alterar-itens`)
- Commit: `tipo: GK-<número> descrição` (ex.: `feat: GK-12 cadastro de cliente`). O hook `scripts/hooks/commit-msg` confere o formato; ative com `scripts/gk.sh install-hooks`
- Branch e PR podem ser abertos com `scripts/gk.sh` (veja `scripts/gk.sh ajuda`) ou pela skill do Claude Code em `.claude/skills/jira-gamekeys/`
- Toda mudança entra por pull request revisado por outro integrante.
