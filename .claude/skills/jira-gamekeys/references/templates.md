# Modelos de texto

Descrições vão em Markdown (`contentFormat: markdown`). US e Driver seguem o conteúdo do modelo da disciplina, no formato **legível** aprovado em 20/10/2026 (tabela de campos, títulos `###`, **Dado que/Quando/Então** em negrito, caixas clicáveis). Não use bloco de código: ele força rolagem horizontal. Bug espelha `.github/ISSUE_TEMPLATE/bug.yml`.

## Título

- US: `[US-NN] Título curto` (NN = número da chave, com zero à esquerda abaixo de 10: GK-7 vira `[US-07]`). RNF: `[US-NN] RNF: ...`.
- Bug: `[BUG] Título curto do problema`.

## US

O número da US é o da chave. Campos em aberto: "a definir no Planning". Exemplos prontos: GK-7 (RF) e GK-61.

```markdown
| Campo | Valor |
| --- | --- |
| **TÍTULO** | [US-XX] <Título curto da funcionalidade> |
| **FEATURE / ÉPICO** | <ex.: Conta e acesso (GK-1)> |
| **RELEASE** | <R1 | R2 | R3 | R4> |
| **SPRINT** | <0 a 7 | a definir no Planning> |
| **PRIORIDADE** | <Muito alta | Alta | Média | Baixa> |
| **STORY POINTS** | <1, 2, 3, 5, 8, 13 | a estimar no Planning Poker> |
| **RESPONSÁVEL** | <nome | a definir no Planning> |
| **PAPEL DE REVISÃO** | <PO | QA> |

### HISTÓRIA DE USUÁRIO

Eu como **<perfil de usuário>**,

preciso **<ação ou funcionalidade>**,

de modo que **<benefício ou valor de negócio>**.

### CONTEXTO E OBSERVAÇÕES (opcional)

<Regras de negócio, protótipos, links, dependências de outras US>

### CRITÉRIOS DE ACEITE

**Cenário 1: <situação principal (caminho feliz)>**

* **Dado que** <contexto inicial>
* **Quando** <ação do usuário>
* **Então** <resultado esperado>

**Cenário 2: <situação alternativa ou de erro>**

* **Dado que** <contexto inicial>
* **Quando** <ação do usuário>
* **Então** <resultado esperado>
* **E** <resultado adicional, se houver>

### DEFINITION OF READY (DoR) - preencher antes da Sprint Planning

- [ ] História escrita no formato "Eu como... preciso... de modo que..."
- [ ] Critérios de aceite escritos em Gherkin
- [ ] Estimativa de Story Points definida pela equipe
- [ ] Prioridade definida pelo PO
- [ ] Dependências identificadas
- [ ] Cabe em uma sprint

### DEFINITION OF DONE (DoD) - conferir na Sprint Review

- [ ] Código revisado e integrado via Pull Request
- [ ] Critérios de aceite atendidos e validados pelo QA
- [ ] Testes escritos e passando
- [ ] Pipeline de CI sem falhas
- [ ] Implantado em ambiente de homologação (quando exigido na release)
- [ ] Documentação atualizada
- [ ] Aceita pelo PO
```

Marque `[x]` na DoR só o que foi conferido. US técnica (banco, infra, back-end, gestão): mesmo modelo, com "a equipe" ou "desenvolvedor" no lugar do perfil e cenários verificáveis. As Tasks (Subtasks) só nascem quando a US entra na sprint.

## Driver arquitetural

Título no Jira: `[DA-SEG-I1-01] Resumo curto`. Descrição neste formato (seções 1, 2, 3, 7 e 8 do modelo da professora); prioridade, ligações com US e release ficam nos campos do Jira (Prioridade, links "relates to", Versões corrigidas). Cada medida precisa de número e unidade. Responsável do Jira = integrante responsável. Exemplo pronto: GK-69.

```markdown
## DRIVER ARQUITETURAL - GAMEKEYS

### 1. IDENTIFICAÇÃO

| Campo | Valor |
| --- | --- |
| **ID do driver** | <DA-SEG-I1-01> (DA-<sigla do atributo>-<integrante>-<nº do driver>) |
| **Título** | <resumo curto> |
| **Equipe / Projeto** | GameKeys |
| **Integrante responsável** | <nome> |
| **Atributo de qualidade** | <Segurança | Confiabilidade | Usabilidade | outro> |
| **Versão** | 1.0 |
| **Data** | <dd/mm/aaaa> |
| **Release alvo** | <R1 | R2 | R3 | R4> |
| **Status** | <Rascunho | Validado pelo PO | Em implementação | Verificado> |

### 2. DESCRIÇÃO DO DRIVER

**Declaração** (uma frase, começando por "O sistema deve..."):

<O sistema deve ...>

### 3. CENÁRIO ARQUITETURAL

| Parte | Conteúdo |
| --- | --- |
| **Fonte do estímulo** (quem ou o que gera o estímulo) | <...> |
| **Estímulo** (a condição que o sistema precisa tratar) | <...> |
| **Artefato** (parte do sistema afetada) | <...> |
| **Ambiente** (em que condições o sistema está) | <...> |
| **Resposta** (o que o sistema deve fazer) | <...> |
| **Medida da resposta** (como saber que foi atendido, com número e unidade) | <...> |

### 7. VERIFICAÇÃO

**Como o cenário será testado ou medido:**

<...>

**Ferramenta / quem executa / quando:**

<...>

**Critério de aceite (Gherkin, opcional):**

* **Dado que** <contexto>
* **Quando** <estímulo>
* **Então** <resposta com a medida>

**Resultado obtido:** <valor medido | a medir na release alvo>

**Atendeu?** <Sim | Não | Parcial | ->

**Evidência (link ou arquivo):** <... | ->

### 8. CHECKLIST DO DRIVER

- [ ] Atributo de qualidade identificado
- [ ] Declaração do driver clara, em uma frase
- [ ] As seis partes do cenário preenchidas (fonte, estímulo, artefato, ambiente, resposta, medida)
- [ ] Medida da resposta com número e unidade, verificável
- [ ] Prioridade definida (importância e dificuldade)
- [ ] Ligado a pelo menos uma US e a um risco ou item do plano de qualidade
- [ ] Forma de verificação definida
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
