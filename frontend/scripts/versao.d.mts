import type { Plugin } from "vite";

export function versaoDoBuild(ambiente?: Record<string, string | undefined>): {
  commit: string;
};
export function pluginVersao(): Plugin;
