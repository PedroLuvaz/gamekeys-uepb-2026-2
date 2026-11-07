# Plano de Qualidade e Testes — Release 2

## GameKeys \| Sprint 2 e Sprint 3 \| QA: Rodrigo Almeida Gomes \| Versão 1.0 — 07/11/2026

Situação: documento de acompanhamento. Resultados finais, aceites do PO e marcações da DoD serão preenchidos com evidência na Review. Esta versão não substitui as planilhas originais da Sprint 0; complementa-as e registra os controles da Release 2\.

# 1\. Objetivo, papéis e escopo

Garantir qualidade verificável no carrinho, na reserva de chaves e, posteriormente, no checkout completo. QA: Rodrigo (planejamento, testes, evidências, bugs e pareceres). PO/DevOps: Wagner (aceite de negócio, CI e homologação). SM: Pedro (impedimentos, registro de riscos e acompanhamento da DoD).  
Sprint 2 (03–12/11): adicionar jogo ao carrinho (GK-11/GK-118/GK-119); alterar/remover (GK-12); reserva segura e transação (GK-15/GK-46); driver de não duplicação (GK-72); estudo já integrado (GK-110); QA (GK-116), homologação (GK-135/GK-140). Sprint 3: fluxo de finalizar compra/pagamento e entrega da chave (GK-14/GK-16). Teste do experimento isolado ≠ aceite do checkout real.

# 2\. Metas da planilha oficial e forma de comprovar

Q-01 — Senhas protegidas. Meta: 100% dos testes de hash/ausência de senhas em respostas. Evidência: pytest e CI; confirmar regressão da R2.  
Q-02 — Controle de acesso. Meta: 100% das rotas protegidas cobertas por testes de negação. Testar token ausente/inválido/expirado, perfil indevido e isolamento entre clientes. Evidência: casos por rota; rotas de administrador ficam para a Release 3\.  
Q-03 — Chave única por pedido. Meta: 0 chaves associadas a mais de um pedido em 100 execuções concorrentes. Evidência exigida: 20 compras simultâneas por rodada, consulta SQL de duplicidade e relatório de 100 rodadas do FLUXO REAL (GK-15/GK-46/GK-72/GK-130). SITUAÇÃO: ainda pendente no fluxo real; GK-110 comprovou apenas o experimento isolado.  
Q-04 — Tratamento de erros. Meta: 100% dos fluxos principais com erro tratado e sem gravação parcial. Validar estoque insuficiente, idade, timeout, falha forçada e rollback. Evidência: pytest, exploração na API/UI e banco isolado.  
Q-05 — Facilidade de uso. Meta: pelo menos 4 de 5 colegas concluírem o fluxo de compra sem ajuda em até 5 min (mínimo aceitável 3/5). Planejar teste com 5 participantes quando fluxo de compra estiver disponível, registrando tempo, sucesso e dificuldades; se ainda indisponível na Sprint 2, marcar pendente, sem inventar resultados.  
Q-06 — Mensagens claras. Meta: 100% dos erros de validação com mensagem em português indicando o problema e o que fazer. Evidência: checklist e capturas das telas entregues.  
Q-07 — Bugs críticos/altos abertos no fechamento. Meta: 0\. Evidência: busca/filtro de bugs do Jira, severidade e status na Review.  
Q-08 — Execução de casos. Meta: 100% dos casos associados a histórias entregues executados. Evidência: matriz da seção 3 com resultado, data, ambiente e link.  
Q-09 — Critérios de aceite. Meta: 100% das histórias com cenários Gherkin de sucesso e exceção antes do desenvolvimento. Responsável pela definição: PO; QA confere testabilidade e casos negativos.  
Q-10 — Estabilidade do escopo. Meta: ≤ 20% das histórias adicionadas/alteradas depois da Planning. Responsável: PO/SM; contar a partir do histórico do Jira e justificar mudanças.  
Q-11 — Revisão de código. Meta: 100% dos PRs mesclados com uma aprovação independente. Evidência: aba Reviews e branch protection do GitHub. PR \#24 aguardava aprovação de Rodrigo na consulta de 07/11; não confundir comentário com aprovação formal.  
Q-12 — Estabilidade do pipeline. Meta: ≥ 90% de execuções verdes na main. Responsável: DevOps; calcular no fechamento a partir do histórico do Actions, sem usar apenas o CI de PR.  
Q-13 — Previsibilidade. Meta: diferença planejado × entregue ≤ 20%. Responsável: SM; registrar story points e velocity após fechamento, sem antecipar resultado final.  
Q-14 — Análise estática. Meta: 0 erros Ruff na main. Evidência: job backend do CI e URL da execução.  
Q-15 — README e documentação. Meta: 100% do checklist da release (descrição, como executar e testar). Evidência: README, contratos de API, relatórios e links do Drive/Jira.

# 3\. Matriz de testes e rastreabilidade (QA)

Status válidos: PLANEJADO, BLOQUEADO, EXECUTADO/APROVADO, EXECUTADO/FALHOU, NÃO APLICÁVEL. Só preencher EXECUTADO após conferir comando ou gravação, resultado e URL da evidência.  
QA-R2-001 / GK-11: adicionar jogo autenticado com estoque → cria item (API 200\) e persiste no próprio carrinho. API no PR \#24: testes e CI verdes; homologação e validação final do QA ainda devem ser registradas.  
QA-R2-002 / GK-11: adicionar novamente → soma quantidades, sem segunda linha. Coberto pelos testes do PR \#24; validar depois de aplicar migração em homologação.  
QA-R2-003 / GK-11: ultrapassar estoque → HTTP 409, nenhuma mudança persistida. Coberto no PR \#24; validar fluxo publicado.  
QA-R2-004 / GK-11: classificação etária superior à idade → HTTP 403 com mensagem e sem adicionar. Coberto no PR \#24; verificar interface na GK-119.  
QA-R2-005 a 007 / GK-12: aumentar, diminuir e remover → total recalculado corretamente; bloquear quantidade acima do estoque. BLOQUEADO pela conclusão/integracão da GK-11.  
QA-R2-008 / GK-15/GK-46: reservar chave para pedido autenticado → chave vinculada uma única vez. PLANEJADO, aguarda implementação real.  
QA-R2-009 / GK-72/GK-130: 100 rodadas × 20 compras simultâneas da última chave → 1 sucesso e 19 negativas por rodada, 0 duplicações. PLANEJADO para fluxo real; não reaproveitar resultado do experimento como aceite.  
QA-R2-010 / GK-46: falha provocada antes do commit → rollback de pedido, item e chave. PLANEJADO na implementação real.  
QA-R2-011 / Segurança: dois clientes não podem ler ou modificar carrinhos/pedidos de outro; rejeitar JWT ausente ou inválido. Verificar endpoint e depois API completa.  
QA-R2-012 / Homologação GK-140: abrir frontend e API publicados, conferir /saude/banco, login, catálogo e POST carrinho com migração aplicada. Não executar testes destrutivos na homologação compartilhada.  
QA-R2-013 / Regressão: cadastro, login, catálogo, detalhes, autenticação, testes de segurança e UI da R1. Executar após merges relevantes e antes da Review.

# 4\. Riscos prioritários e providências

RISCO 20 — CONFIABILIDADE (origem: planilha de riscos, Pedro I1): a mesma chave ser vendida a mais de um comprador devido a concorrência. Probabilidade P=2, severidade S=5, risco=(6−2)×5=20: VERMELHO / EVITAR. Resposta: transação com SELECT ... FOR UPDATE SKIP LOCKED, restrição de unicidade, testes 20×100 e consulta SQL na base de testes. Evidência: GK-110 (experimento integrado), GK-15/GK-46/GK-72, GK-129/GK-130. SITUAÇÃO: aberto para o checkout real, apesar do experimento isolado aprovado.  
RISCO DE ACESSO (Segurança, Rodrigo I3 na planilha): sessão expirada ainda válida ou permissão de perfil incorreta. P=3, S=4, risco=12 (AMARELO / MITIGAR). Executar testes de token expirado, assinatura adulterada e acesso cruzado; rotas admin ficam para R3.  
RISCO DE GRAVAÇÃO PARCIAL (Confiabilidade, Rodrigo I3): parte de um lote/pedido persistir após falha. Planilha original P=3, S=3, risco=9 (AMARELO / MITIGAR). Na R2, testar rollback da reserva; lote de chaves pertence à R3.  
RISCO DE INTEGRAÇÃO: API do carrinho depende da migração 0003\_carrinho.sql aplicada no ambiente correto antes do deploy. Responsável pelo tratamento: Wagner/DevOps. Conferir GK-118, GK-119, GK-135/GK-140; não aplicar DDL automaticamente no Neon e não expor credenciais.  
RISCO DE PRAZO: demonstração marcada para 11/11 às 9h; fechar desenvolvimento e revisão prioritários até 10/11, reservar período para ensaio. Se GK-15/GK-46/GK-12 não estiverem prontas, mostrar a situação real e registrar pendência/ajuste de escopo com PO/SM.

# 5\. Conferência da DoD pelo QA

Por história: critérios de aceite com evidência; testes passando e regressão do afetado; CI verde no commit integrado; PR com aprovação de outra pessoa; documentação/API atualizadas; homologação quando exigida; aceite do PO registrado no Jira. Não marcar uma caixa por promessa ou por resultado de experimento diferente.  
Sprint 2: conferir objetivo da Sprint, todos os itens concluídos com DoD, bugs com severidade e plano, regressão, risco 20, Q-03, Q-08, Q-11 e Q-14, Jira atualizado e atas reais. SM organiza o fechamento; QA entrega parecer; PO aprova/recusa.  
Release 2: testar fluxo completo de carrinho→pedido→pagamento simulado→chave, homologação, relatório de qualidade, release notes, pipeline, tag/release, documentação e acessos. Quando algo não se aplicar, usar N/A justificado.

# 6\. Modelo curto de bug e parecer de QA

BUG — título objetivo; US relacionada; ambiente/commit; severidade (Crítica, Alta, Média ou Baixa); passos para reproduzir; esperado; obtido; evidência (captura/log/CI); responsável; resultado do reteste. Criar issue de Bug no Jira e comentar no PR relacionado.  
PARECER DE QA NO PR: “Revisei \[escopo\]. Conferi \[testes/CI e critérios\]. \[Aprovado para integração / Ajustes solicitados\]. Pendente: \[ambiente, UI, cenário ou aceite\].” A aprovação formal deve ser dada na aba Files changed → Review changes; um comentário isolado não substitui o review.  
PARECER DE QA NO JIRA: “GK-118: conferi contrato e testes da API; CI do PR \#24 verde. Integração/homologação e interface GK-119 ainda pendentes.” Registrar aceite do PO separadamente; QA não decide aceitação de negócio.

# 7\. Evidências já disponíveis e pendências de 07/11

GK-110 / PR \#18: experimento isolado de concorrência aprovado com 100×20 tentativas (2.000), 100 reservas e 1.900 recusas, sem falhas; 92 testes backend locais; PR mesclado com CI verde. Não comprova checkout da aplicação.  
GK-118 / PR \#24 (Wagner): backend POST /carrinho/itens, migração 0003 e testes; CI verde em https\://github.com/PedroLuvaz/gamekeys-uepb-2026-2/actions/runs/42372978858. PR ainda aberto na conferência de 07/11; 144 testes backend informados e cobertura dos cenários de estoque, idade e concorrência. QA deve registrar review formal manualmente; migração na homologação e tela GK-119 são entregas separadas.  
GK-129 / PR \#27: automação do teste de concorrência no CI em revisão por Wagner; não preencher Q-03 como comprovada no checkout completo sem conferir alvo real do teste.  
GK-142: publicar este Plano de Qualidade da R2 no Drive, vincular no Jira e, em PR de documentação, adicionar ao README de R2 e espelhar em docs/. GK-116: manter matriz atualizada com evidência por cenário.

# 8\. Cronograma de trabalho e ponto de controle

07/11 (sábado): revisar PR \#24; publicar este plano; registrar situação de Q-03, riscos e itens pendentes; solicitar aprovação manual do review se ferramenta não permitir.  
09/11 (segunda): ponto de controle GK-112; confirmar PR \#24 mesclado, endpoint e tela GK-119 integrados, responsáveis por GK-12/GK-15/GK-46, homologação GK-140 e plano de testes.  
10/11 (terça): executar/registrar testes do incremento disponível; evidências de regressão e risco 20; atualizar planilha de qualidade e risco, pareceres QA, documentos da Review, fotos/links; ensaiar.  
11/11 (quarta, 9h): apresentar o incremento real e evidências. Não afirmar conclusão de histórias ou critérios sem aceite; a Review/Retrospectiva de encerramento formal pode seguir o calendário do Jira em 12/11.

# 9\. Fontes e links oficiais

Plano de Qualidade (planilha matriz Q01–Q15): https\://docs.google.com/spreadsheets/d/1oFIoArPRYugK9tnwQFsLC75rlv7r4TiK/edit  
Análise de Riscos baseada em defeitos: https\://docs.google.com/spreadsheets/d/1-V-hE9YR3ZEPaU3jr15yCcHHMzlV64ej/edit  
DoD Sprint e Release: https\://docs.google.com/spreadsheets/d/1Mr-6oT0po8POyaRGD75hCEQjqA-TzI4Q/edit  
Plano de Teste R1: https\://docs.google.com/document/d/1qXmh7E59SYTYdfxeKzZtY5n8A1jDZK6s/edit  
Plano da Release 2: https\://docs.google.com/document/d/1TBzpeiyrZG81ur2l\_uoBKzavjskJAV71tsItetSN9JM/edit  
Jira GK-116: https\://pedrolucas0721.atlassian.net/browse/GK-116 \| Jira GK-142: https\://pedrolucas0721.atlassian.net/browse/GK-142 \| PR \#24: https\://github.com/PedroLuvaz/gamekeys-uepb-2026-2/pull/24

Planilha de acompanhamento da Release 2 (Q-01–Q-15, testes e riscos): https\://docs.google.com/spreadsheets/d/1ZJsomiV2\_mLoEhCEVhpdOIKnlsPTkwyq43jIpFViLOQ/edit  
