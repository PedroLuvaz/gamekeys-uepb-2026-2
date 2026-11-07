import { defineConfig } from "cypress";
import createBundler from "@bahmutov/cypress-esbuild-preprocessor";
import configuracaoBase from "./cypress.config.mjs";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const backend = fileURLToPath(new URL("../backend/", import.meta.url));
const python =
  process.env.GAMEKEYS_PYTHON ||
  (process.platform === "win32"
    ? path.join(backend, ".venv/Scripts/python.exe")
    : "python");

function fixtureCarrinho(acao, dados = {}) {
  return JSON.parse(
    execFileSync(python, ["-m", "qa.gk11_carrinho", acao], {
      cwd: backend,
      input: JSON.stringify(dados),
      encoding: "utf8",
      timeout: 20000,
      windowsHide: true,
      env: { ...process.env, PYTHONUTF8: "1" },
    }),
  );
}

// A suíte real não gera Cucumber JSON: preserva as evidências dos cenários Gherkin.
export default defineConfig({
  ...configuracaoBase,
  // Identificador público consultado no banco local pelo CI; nenhuma credencial vai ao navegador.
  expose: {
    jogoInativoId: Number(process.env.GAMEKEYS_JOGO_INATIVO_ID || 0),
  },
  reporterOptions: {
    ...configuracaoBase.reporterOptions,
    mochaFile: "cypress/reports/integracao-real-[hash].xml",
  },
  e2e: {
    ...configuracaoBase.e2e,
    specPattern: "cypress/integracao/**/*.cy.ts",
    supportFile: "cypress/support/integracao.ts",
    setupNodeEvents(on, config) {
      on("file:preprocessor", createBundler());
      on("task", {
        "carrinho:preparar": () => fixtureCarrinho("preparar"),
        "carrinho:estado": (dados) => fixtureCarrinho("estado", dados),
        "carrinho:limpar": (dados) => fixtureCarrinho("limpar", dados),
      });
      return config;
    },
  },
});
