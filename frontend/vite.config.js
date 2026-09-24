import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// The FastAPI application does not expose CORS middleware. Keeping requests on
// the Vite origin avoids browser preflight requests during local development.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const backendUrl = env.VITE_BACKEND_URL || "http://localhost:8000";

  return {
    plugins: [react()],
    server: {
      proxy: {
        "/api": {
          target: backendUrl,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ""),
        },
      },
    },
  };
});
