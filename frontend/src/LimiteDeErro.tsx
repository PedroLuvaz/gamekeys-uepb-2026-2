import { Component } from "react";
import type { ReactNode } from "react";

type Propriedades = {
  // Muda a cada navegação: sair da tela com falha limpa o erro e volta a renderizar.
  chave: string;
  children: ReactNode;
};

type Estado = { chave: string; falhou: boolean };

// GK-48 e GK-77: se uma tela lançar um erro inesperado ao desenhar, o cliente vê
// esta mensagem com saída, nunca uma página em branco.
export default class LimiteDeErro extends Component<Propriedades, Estado> {
  state: Estado = { chave: this.props.chave, falhou: false };

  static getDerivedStateFromProps(
    propriedades: Propriedades,
    estado: Estado,
  ): Estado | null {
    return propriedades.chave === estado.chave
      ? null
      : { chave: propriedades.chave, falhou: false };
  }

  static getDerivedStateFromError(): Partial<Estado> {
    return { falhou: true };
  }

  componentDidCatch(erro: unknown) {
    // Só o console do navegador: nada de detalhe técnico na tela do cliente.
    console.error("Falha ao desenhar a tela.", erro);
  }

  render() {
    if (!this.state.falhou) return this.props.children;
    return (
      <section className="estado-tela" role="alert" data-cy="erro-inesperado">
        <span className="estado-icone" aria-hidden="true">
          !
        </span>
        <h2>Algo deu errado nesta tela</h2>
        <p>
          Não foi possível mostrar esta página. Recarregue para tentar de novo
          ou volte ao catálogo.
        </p>
        <button className="botao" onClick={() => window.location.reload()}>
          Recarregar a página ↻
        </button>
        <a href="/" className="botao botao-secundario">
          Ir para o catálogo →
        </a>
      </section>
    );
  }
}
