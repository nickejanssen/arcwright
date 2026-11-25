import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [
      {
        // Mini-game packages import the kit by this name; the dashboard's
        // copy lives in src/mini-game-kit (AW-329).
        find: /^@arcwright\/mini-game-kit$/,
        replacement: "/src/mini-game-kit/index.ts",
      },
    ],
  },
  server: {
    allowedHosts: true,
    // Package renderers and definitions live in nightcap/mini_games/, outside
    // dashboard/.
    fs: {
      allow: [".."],
      deny: [
        ".env",
        ".env.*",
        "*.{crt,pem}",
        "**/nightcap/mini_games/*/server/**",
        "**/engine/**",
      ],
    },
    proxy: {
      "/v1": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
