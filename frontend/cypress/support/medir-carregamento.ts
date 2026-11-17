type JanelaComMedicoes = Window & {
  __gk77CarregamentoMs?: Record<string, number>;
  MutationObserver: typeof MutationObserver;
};

export function medirAteAparecer(
  janela: Window,
  chave: string,
  seletor: string,
) {
  const janelaMedida = janela as JanelaComMedicoes;
  const inicio = janela.performance.now();
  janelaMedida.__gk77CarregamentoMs ??= {};

  const registrar = () => {
    if (!janela.document.querySelector(seletor)) return false;
    janelaMedida.__gk77CarregamentoMs![chave] =
      janela.performance.now() - inicio;
    observador.disconnect();
    return true;
  };

  const observador = new janelaMedida.MutationObserver(registrar);
  if (!registrar()) {
    observador.observe(janela.document, { childList: true, subtree: true });
  }
}

export function confirmarEmAteUmSegundo(chave: string) {
  cy.window().should((janela) => {
    const tempo = (janela as JanelaComMedicoes).__gk77CarregamentoMs?.[chave];
    expect(tempo, `tempo para exibir o indicador ${chave}`).to.be.a("number");
    expect(tempo, `tempo para exibir o indicador ${chave}`).to.be.at.most(1000);
  });
}
