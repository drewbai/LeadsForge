import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const __dirname = dirname(fileURLToPath(import.meta.url));
const pkg = JSON.parse(readFileSync(join(__dirname, "package.json"), "utf8"));

export default defineConfig({
  plugins: [react()],
  define: {
    __LF_FRONTEND_PKG_VERSION__: JSON.stringify(pkg.version ?? "0.0.0"),
  },
  server: {
    proxy: {
      "/leads": { target: "http://127.0.0.1:8000", changeOrigin: true },
      "/enrichment": { target: "http://127.0.0.1:8000", changeOrigin: true },
      "/scoring": { target: "http://127.0.0.1:8000", changeOrigin: true },
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./tests/setup.js",
  },
});
