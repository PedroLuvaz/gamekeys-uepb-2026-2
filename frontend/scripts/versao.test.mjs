import assert from "node:assert/strict";
import test from "node:test";
import { versaoDoBuild } from "./versao.mjs";

test("o identificador do build expõe somente o SHA completo", () => {
  const sha = "a".repeat(40);
  assert.deepEqual(
    versaoDoBuild({ GAMEKEYS_COMMIT: sha, SEGREDO: "privado" }),
    {
      commit: sha,
    },
  );
  assert.deepEqual(versaoDoBuild({ VERCEL_GIT_COMMIT_SHA: sha }), {
    commit: sha,
  });
  assert.deepEqual(versaoDoBuild({ GAMEKEYS_COMMIT: "configuração privada" }), {
    commit: "desenvolvimento",
  });
});
