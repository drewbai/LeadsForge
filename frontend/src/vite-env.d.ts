/// <reference types="vite/client" />

declare const __LF_FRONTEND_PKG_VERSION__: string;

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  /** Commit injected at build (e.g. CI). */
  readonly VITE_BUILD_COMMIT?: string;
}
