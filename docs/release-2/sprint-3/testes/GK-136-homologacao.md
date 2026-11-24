# GK-136 — Publicação contínua em homologação

Preparado por Wagner Tiburcio da Silva Junior (PO e DevOps) em 23/11/2026.
Branch: `feature/GK-136-homologacao-segura`. Base: `main` `9c83939`, incluindo
a GK-73 e o acompanhamento da Sprint 3 integrados em 23/11.

## Situação conferida

- A publicação inicial e a integração Git do Vercel foram feitas por Pedro na
  GK-135. Permanecem os projetos `gamekeys-api` e `gamekeys-web`, no plano Hobby.
- O ruleset `Proteção da main` (ID 26445087) exige uma aprovação independente e os
  checks `frontend`, `backend` e `imagens Docker`. Wagner tem acesso de escrita,
  mas não de administrador; não consegue alterar esse ruleset.
- Os status `Vercel – gamekeys-api` e `Vercel – gamekeys-web` existem e passaram no
  commit `9fcf42b` do PR #62. O configurador acrescenta exatamente esses nomes,
  preservando as regras e checks anteriores.
- Não havia segredos de GitHub Actions configurados no repositório na consulta.
  Não foi consultado ou publicado o valor de nenhum segredo.
- Consulta somente de leitura ao Neon `gamekeys`, branch `production`, confirmou
  as migrações 0001 a 0006 aplicadas. A conta `gamekeys_equipe` ainda não tinha
  `SELECT` sobre `public.migracoes_aplicadas`. A migração 0007 deste PR concede
  apenas essa leitura; foi validada em PostgreSQL local, ainda não aplicada ao Neon.

## Fluxo implementado

1. O CI existente continua executando builds, smoke, regressão, concorrência e
   integração a cada push e PR. Acrescenta validação dos workflows com actionlint
   1.7.7 e um teste do identificador público do build web.
2. `.github/workflows/homologacao.yml` reage apenas à conclusão de CI de **push na
   main do próprio repositório**. CI de PR ou fork não recebe os segredos de
   homologação. Uma repetição manual também exige `main` e CI aprovado do commit atual.
3. `qa.gk136_homologacao` confirma novamente, via API do GitHub, o workflow
   `.github/workflows/ci.yml`, evento, repositório, branch, conclusão, SHA e checkout.
   Um CI antigo não pode sobrescrever um commit mais novo da main.
4. O registro das migrações é lido em transação PostgreSQL **READ ONLY**, com
   limites de conexão e consulta. Não há `CREATE`, `ALTER`, `DROP`, carga ou
   migração automática no banco compartilhado. Conexão remota sem TLS, pooler,
   banco diferente de `gamekeys`, credencial administrativa ou registro divergente
   bloqueiam a publicação antes de qualquer build ou promoção.
5. O CLI oficial Vercel 65.2.0 prepara os dois projetos com
   `deploy --prod --skip-domain`, usando o checkout do SHA aprovado. O SHA público
   é enviado explicitamente como `GAMEKEYS_COMMIT` no build e na execução.
6. Antes da promoção, `vercel curl` verifica as URLs protegidas: versão da API,
   conexão com o banco e versão do build web. Os dois builds precisam passar.
   A main e o registro de migrações são conferidos novamente.
7. API e web são promovidas em sequência. A verificação pública confere os
   identificadores, o banco e o proxy `/api` do site. Uma falha durante promoção
   ou verificação dispara tentativa de restaurar os deployments anteriores, com
   confirmação pelo projeto. Falha de restauração é registrada como
   **não confirmada**, sem anunciar sucesso.
8. Data, commit, CI de origem, migrações conferidas, URLs e resultado ficam no
   resumo do workflow e em `homologacao-<run_id>/homologacao.json`, inclusive em
   caso de bloqueio. A GK-148 poderá consolidar esse artefato.

`git.deploymentEnabled.main=false` nos dois `vercel.json` impede que a integração
Git publique a main antes do CI. Os previews das demais branches continuam
habilitados. O CLI não depende desse gatilho Git para publicar.

## Ativação pelo Pedro — antes do merge

**Não integrar este PR antes de configurar os dois segredos.** Sem eles, o novo
workflow recusa a publicação e o deploy direto da main estará desabilitado. As
URLs atuais continuam servindo a versão anterior.

1. Fazer checkout da branch deste PR. Como responsável pelo banco, aplicar as
   migrações pendentes pelo processo habitual, com conexão direta do proprietário:
   em `backend`, `python -m app.migrar`, sem `--carga`. A única migração nova é
   `0007_leitura_registro_migracoes.sql`: concede `SELECT` no registro à equipe.
   Não colocar a credencial do proprietário nos segredos do GitHub nem no Vercel.
2. Em uma máquina autenticada no GitHub CLI como Pedro, com as dependências do
   backend instaladas, executar:

   ```powershell
   cd backend
   .venv/Scripts/python.exe -m qa.gk136_configurar --aplicar
   ```

   O configurador pede, com entrada oculta:

   - Um token Vercel do Pedro, com acesso aos dois projetos no escopo
     `pedro-andrades-projects-abe06b11`. Pode ser criado em
     [Tokens do Vercel](https://vercel.com/account/tokens).
   - A conexão direta de `gamekeys` usando `gamekeys_equipe`, com TLS. Essa conta
     não é dona do banco e passa a ter a leitura necessária pela migração 0007.

   Ele valida o banco e os projetos antes de configurar `VERCEL_TOKEN` e
   `HOMOLOGACAO_DATABASE_URL_UNPOOLED` via stdin do `gh secret set`. Em seguida,
   acrescenta os dois checks Vercel ao ruleset existente e confirma o resultado.
   Não imprime credenciais, não as grava em arquivo e não reduz as aprovações.
   Sem `--aplicar`, apenas mostra um diagnóstico, sem alterar configuração.
3. Após revisão independente e CI verde, integrar o PR. Conferir a primeira
   execução **Homologação** na main e guardar seu artefato. As URLs e o commit
   publicado devem ser os do relatório. Se for necessário repetir, usar
   `workflow_dispatch` na main depois de corrigir o impedimento; o script verifica
   novamente o CI, sem permitir ignorar os bloqueios.

Não é necessário adicionar Wagner à equipe paga do Vercel. O token protegido é
usado somente pelo workflow de código integrado na main. Revogação ou expiração
desse token exige sua atualização pelo responsável da conta.

## Como verificar

Em um PostgreSQL local descartável `gamekeys_teste` (Docker do projeto: porta
5433), a partir de `backend`, definir explicitamente:

```powershell
$env:PYTHON_DOTENV_DISABLED = '1'
$env:TEST_DATABASE_URL = 'postgresql://gamekeys:gamekeys@127.0.0.1:5433/gamekeys_teste?sslmode=disable'
$env:DATABASE_URL = $env:TEST_DATABASE_URL
$env:DATABASE_URL_UNPOOLED = $env:TEST_DATABASE_URL
.venv/Scripts/python.exe -m pytest tests/test_homologacao.py tests/test_saude.py -v
.venv/Scripts/python.exe -m pytest -q --junitxml=relatorios/gk136/backend-completo.xml
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m ruff format --check .
```

O pytest recria schemas **somente desse banco local**. Na validação de Wagner, foi
usada uma instância exclusiva na porta 55438. O teste real do checker usa o papel
limitado da equipe e confirma que a consulta ocorre em READ ONLY; outro teste
recusa o proprietário. Os demais testes de publicação, promoção e restauração
usam substitutos dos serviços externos: não publicam nem alteram Vercel ou Neon.

Em `frontend`, `pnpm build` e `node --test scripts/versao.test.mjs` verificam a
tipagem, o build e a identificação pública. O resultado é `/versao.json` com
somente o commit. A API oferece `/saude/versao`, também com somente o commit;
`/saude` mantém seu contrato anterior. Em execução local sem SHA válido, o valor
é `desenvolvimento`.

## Resultado e limites das evidências

- Testes de bloqueio, sucesso e restauração simulada aprovados localmente.
- Regressão completa local: **330 testes aprovados em 47,65 s**, sem falhas ou
  testes pulados. Inclui 36 novos testes da GK-136. Há apenas um aviso de
  depreciação já existente do `TestClient`.
- Build e TypeScript do frontend, teste Node da versão e actionlint 1.7.7
  aprovados. Ruff e formatação aprovados.
- Resultado da regressão completa e execuções de push/PR são registrados no
  relatório individual do PR, com links dos artefatos do respectivo commit.
- Nenhum teste foi executado no Neon. A consulta ao Neon citada acima foi somente
  de leitura. Nenhuma configuração de Vercel ou ruleset foi alterada por Wagner.

As migrações são comparadas por **nome registrado**, conforme o mecanismo vigente;
isso não detecta edição de SQL já aplicado. Não editar migrações históricas.
Mudanças futuras de banco precisam preservar compatibilidade com a versão que
continua no ar; o pipeline não desfaz DDL nem restaura dados. Os dois projetos não
têm promoção atômica conjunta: existe uma janela entre API e web, e falha parcial
é tratada com tentativa de restauração e registro explícito do resultado.

Os testes e o CI comprovam a implementação. **Ativação, publicação real,
restauração real, verificação funcional do QA e aceite do PO ainda não são
comprovados por este documento.** Concluir a GK-136 somente após configurar os
acessos, integrar o PR, verificar a primeira execução e registrar os aceites.

## Referências técnicas

- [Vercel: configuração dos gatilhos Git](https://vercel.com/docs/project-configuration/git-configuration).
- [Vercel: deploy com skip-domain](https://vercel.com/docs/cli/deploy).
- [Vercel: promoção de deployments](https://vercel.com/docs/deployments/promoting-a-deployment).
- [Vercel: curl com proteção de deployment](https://vercel.com/docs/cli/curl).
- [Vercel: rollback no plano Hobby](https://vercel.com/docs/instant-rollback).
- [GitHub: eventos workflow_run e suas permissões](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).
