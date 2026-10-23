// Readiness para o CI: não executa migrações nem modifica dados.
const base = process.env.GAMEKEYS_FRONT_URL || "http://127.0.0.1:5173";
let pronta = false;
for (let tentativa = 0; tentativa < 30; tentativa += 1) {
  try {
    const resposta = await fetch(`${base}/api/saude/banco`, {
      signal: AbortSignal.timeout(2000),
    });
    if (resposta.ok) {
      pronta = true;
      break;
    }
  } catch {
    /* API ou Vite ainda iniciando. */
  }
  await new Promise((resolver) => setTimeout(resolver, 1000));
}
if (!pronta)
  throw new Error("A interface e a API não ficaram prontas para os testes.");
console.log("Interface e API prontas para a verificação integrada.");
