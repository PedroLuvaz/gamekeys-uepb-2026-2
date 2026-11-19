// Guarda somente o identificador da operação. O servidor determina cliente, itens e valores.
const UUID =
  /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const chaveDoCliente = (clienteId: number) =>
  `gamekeys.finalizacao.${clienteId}`;

export function lerFinalizacao(clienteId: number): string | null {
  const valor = sessionStorage.getItem(chaveDoCliente(clienteId));
  if (valor !== null && !UUID.test(valor))
    throw new Error(
      "Não foi possível recuperar a finalização desta sessão. Confira seus pedidos com a equipe antes de tentar novamente.",
    );
  return valor;
}

export function prepararFinalizacao(clienteId: number): string {
  const existente = lerFinalizacao(clienteId);
  if (existente) return existente;
  const chave = crypto.randomUUID();
  sessionStorage.setItem(chaveDoCliente(clienteId), chave);
  if (lerFinalizacao(clienteId) !== chave)
    throw new Error(
      "Não foi possível preparar a finalização nesta sessão. Verifique o armazenamento do navegador e tente novamente.",
    );
  return chave;
}

export function limparFinalizacao(clienteId: number) {
  sessionStorage.removeItem(chaveDoCliente(clienteId));
}
