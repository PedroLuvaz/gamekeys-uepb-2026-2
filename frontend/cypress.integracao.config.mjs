import { defineConfig } from "cypress";
import createBundler from "@bahmutov/cypress-esbuild-preprocessor";
import configuracaoBase from "./cypress.config.mjs";

// A suíte real não gera Cucumber JSON: preserva as evidências dos cenários Gherkin.
export default defineConfig({
  ...configuracaoBase,
  reporterOptions: {
    ...configuracaoBase.reporterOptions,
    mochaFile: "cypress/reports/integracao-real-[hash].xml",
  },
  e2e: {
    ...configuracaoBase.e2e,
    specPattern: "cypress/integracao/**/*.cy.ts",
    setupNodeEvents(on, config) {
      on("file:preprocessor", createBundler());
      return config;
    },
  },
});
