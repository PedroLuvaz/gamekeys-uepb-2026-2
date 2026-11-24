// Identificador público do build; não inclui outras variáveis de ambiente.
export function versaoDoBuild(ambiente = process.env) {
  const commit =
    ambiente.GAMEKEYS_COMMIT || ambiente.VERCEL_GIT_COMMIT_SHA || "";
  return { commit: /^[0-9a-f]{40}$/.test(commit) ? commit : "desenvolvimento" };
}

export function pluginVersao() {
  return {
    name: "gamekeys-versao",
    generateBundle() {
      this.emitFile({
        type: "asset",
        fileName: "versao.json",
        source: JSON.stringify(versaoDoBuild()),
      });
    },
  };
}
