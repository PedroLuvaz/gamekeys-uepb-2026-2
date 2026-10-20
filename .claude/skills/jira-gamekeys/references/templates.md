# Modelos de texto

Descrições vão em Markdown (`contentFormat: markdown`). Os modelos espelham `.github/ISSUE_TEMPLATE/user-story.yml` e `bug.yml` e as histórias já existentes (ex.: GK-7).

## Título

- US e Task: `[US-NN] Título curto` (NN = número da chave, com zero à esquerda abaixo de 10: GK-7 vira `[US-07]`). RNF: `[US-NN] RNF: ...`.
- Bug: `[BUG] Título curto do problema`.

## US / Task

```markdown
| Campo | Valor |
| --- | --- |
| Feature / Épico | <Nome do épico> (GK-<n>) |
| Release | R<N> |
| Sprint | <Sprint N ou "a definir no Planning"> |
| Prioridade | <Muito alta | Alta | Média | Baixa> |
| Story Points | <1|2|3|5|8|13> |
| Responsável | <nome ou "a definir no Planning"> |
| Papel de revisão | <QA | PO> |

### História de usuário

Eu como **<perfil>**, preciso **<ação>**, de modo que **<benefício>**.

### Contexto e observações

<regras de negócio, links, dependências de outras US; ou "Sem observações adicionais.">

### Critérios de aceite

**Cenário 1 (sucesso): <título>**

* **Dado que** <contexto>
* **Quando** <ação>
* **Então** <resultado>

**Cenário 2 (exceção): <título>**

* **Dado que** <contexto>
* **Quando** <ação>
* **Então** <resultado>

### Definition of Ready (DoR) - preencher antes da Sprint Planning

- [ ] História escrita no formato "Eu como... preciso... de modo que..."
- [ ] Critérios de aceite escritos em Gherkin
- [ ] Estimativa de Story Points definida pela equipe
- [ ] Prioridade definida pelo PO
- [ ] Dependências identificadas
- [ ] Cabe em uma sprint

### Definition of Done (DoD) - conferir na Sprint Review

- [ ] Código revisado e integrado via Pull Request
- [ ] Critérios de aceite atendidos e validados pelo QA
- [ ] Testes escritos e passando
- [ ] Pipeline de CI sem falhas
- [ ] Implantado em ambiente de homologação (quando exigido na release)
- [ ] Documentação atualizada
- [ ] Aceita pelo PO
```

US técnica (banco, infra, back-end, gestão): mesmo modelo. No lugar do perfil use "a equipe" ou "desenvolvedor" (ex.: "Eu como **desenvolvedor**, preciso **subir o PostgreSQL com Docker**, de modo que **todos rodem o ambiente igual**") e cenários verificáveis (ex.: "Dado que o Docker está instalado, Quando rodo o compose, Então o banco sobe na porta 5432"). As Tasks dessa US só são criadas quando ela entrar na sprint.

## Driver arquitetural

Título: `[DA-SEG-I1-01] Resumo curto`. Descrição na ficha da professora (a mesma do documento dos Drivers no Drive). Cada medida precisa de número e unidade.

```markdown
### 1. Identificação

| Campo | Valor |
| --- | --- |
| ID do driver | DA-<SEG|CON|USA>-I<1|2|3>-<nº> |
| Título | <resumo curto> |
| Equipe / Projeto | GameKeys |
| Integrante responsável | <nome> |
| Atributo de qualidade | <Segurança | Confiabilidade | Usabilidade> |
| Versão / Data / Release alvo | 1.0 / <dd/mm/aaaa> / <R1..R4> |
| Status | <Rascunho | Validado pelo PO | Em implementação | Verificado> |

### 2. Descrição do driver

O sistema deve <...>.

### 3. Cenário arquitetural

| Parte | Conteúdo |
| --- | --- |
| Fonte do estímulo | <quem ou o que gera o estímulo> |
| Estímulo | <a condição que o sistema precisa tratar> |
| Artefato | <parte do sistema afetada> |
| Ambiente | <em que condições o sistema está> |
| Resposta | <o que o sistema deve fazer> |
| Medida da resposta | <como saber que foi atendido, com número e unidade> |

### 4. Prioridade

Importância para o negócio: <Alta | Média | Baixa>. Dificuldade técnica: <Alta | Média | Baixa>.

### 5. Decisão arquitetural

Decisão: <...>. Alternativa considerada: <... e por que foi descartada>.

### 6. Ligações

Itens do Jira: <GK-N, ...>. Risco ligado: <atributo / integrante: defeito (risco N, estratégia)> (planilha de Análise de Riscos Baseada em Defeitos). Plano de Qualidade: <atributo>.

### 7. Verificação

* **Como o cenário será testado ou medido:** <...>
* **Ferramenta / quem executa / quando:** <...>
* **Critério de aceite (Gherkin):** Dado que <contexto>; Quando <estímulo>; Então <resposta com a medida>
* **Resultado obtido / Atendeu?:** <valor> / <Sim | Não | Parcial>
* **Evidência:** <link ou arquivo>

### 8. Checklist do driver

- [ ] Atributo de qualidade identificado
- [ ] Declaração do driver clara, em uma frase
- [ ] As seis partes do cenário preenchidas (fonte, estímulo, artefato, ambiente, resposta, medida)
- [ ] Medida da resposta com número e unidade, verificável
- [ ] Prioridade definida (importância e dificuldade)
- [ ] Ligado a pelo menos uma US e a um risco ou item do plano de qualidade
- [ ] Forma de verificação definida
- [ ] Validado pelo PO
```

## Bug

```markdown
| Campo | Valor |
| --- | --- |
| Release | R<N> |
| Sprint | <N> |
| Severidade | <Crítica | Alta | Média | Baixa> |
| Prioridade | <Alta | Média | Baixa> |
| US relacionada | GK-<n> (e cenário do Plano de Teste, ex.: CT-02) |
| Reportado por (QA) | <@usuario-github> |
| Responsável | <@usuario-github ou "a definir"> |
| Ambiente | <local | homologação | produção> |
| Navegador / SO | <Chrome 130 / Windows 11> |
| Versão / commit / branch | <main, a1b2c3d> |

### Descrição

<o que está errado, em uma ou duas frases>

### Passos para reproduzir

1. ...
2. ...
3. ...

### Resultado esperado

...

### Resultado obtido

...

### Evidências

<capturas, vídeo, logs, mensagens de erro>

### Critério de correção (Gherkin, opcional)

**Dado que** ... **Quando** ... **Então** ...

### Checklist de encerramento

- [ ] Causa identificada e registrada nos comentários
- [ ] Correção feita via Pull Request que referencia esta issue
- [ ] Teste de regressão criado ou atualizado
- [ ] Correção verificada pelo QA
```

Severidade (Plano de Qualidade): Crítica = impede o uso ou entrega chave errada/duplicada (corrigir no mesmo dia, bloqueia a Review). Alta = função importante não funciona (dentro da sprint). Média = funciona com contorno (nesta sprint ou na próxima). Baixa = visual ou texto (backlog, PO decide). Mapa severidade → prioridade Jira sugerido: Crítica = Highest, Alta = High, Média = Medium, Baixa = Low.
