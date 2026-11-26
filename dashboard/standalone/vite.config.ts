import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";

export default defineConfig({
  root: fileURLToPath(new URL(".", import.meta.url)),
  publicDir: false,
  resolve: {
    alias: {
      "@arcwright/mini-game-kit": fileURLToPath(
        new URL("../src/mini-game-kit/index.ts", import.meta.url),
      ),
    },
  },
});
