import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { pluginVersao } from "./scripts/versao.mjs";

export default defineConfig({
  plugins: [react(), pluginVersao()],
  server: {
    proxy: {
      "/api": {
        target: process.env.GAMEKEYS_PROXY_API || "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
