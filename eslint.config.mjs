import js from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    ignores: ["**/dist/**", "**/node_modules/**", "**/__pycache__/**"],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{js,cjs,mjs,jsx,ts,tsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
    },
    rules: {
      "no-debugger": "error",
    },
  },
  {
    files: [
      "**/scripts/**/*.{js,mjs,cjs}",
      "**/*.config.{js,mjs,cjs}",
      "**/tests/**/*.{js,mjs,cjs}",
    ],
    languageOptions: {
      globals: {
        console: "readonly",
        process: "readonly",
        Buffer: "readonly",
        __dirname: "readonly",
        __filename: "readonly",
        global: "readonly",
        globalThis: "readonly",
        setTimeout: "readonly",
        clearTimeout: "readonly",
        setInterval: "readonly",
        clearInterval: "readonly",
        TextEncoder: "readonly",
        TextDecoder: "readonly",
        fetch: "readonly",
      },
    },
  },
  {
    files: [
      "playtests/nightcap-paper-test-02-v3.0/app.js",
      "playtests/nightcap-paper-test-02-v3.0/config.js",
    ],
    languageOptions: {
      globals: {
        window: "readonly",
        document: "readonly",
        navigator: "readonly",
        sessionStorage: "readonly",
        innerWidth: "readonly",
        requestAnimationFrame: "readonly",
        cancelAnimationFrame: "readonly",
        setInterval: "readonly",
        clearInterval: "readonly",
        fetch: "readonly",
        console: "readonly",
        URL: "readonly",
        URLSearchParams: "readonly",
      },
    },
  },
  {
    files: ["playtests/nightcap-paper-test-02-v3.0/runtime.js"],
    languageOptions: {
      globals: {
        URL: "readonly",
        URLSearchParams: "readonly",
      },
    },
  },
  {
    files: ["playtests/nightcap-paper-test-02-v3.0/tests/**/*.{js,mjs,cjs}"],
    languageOptions: {
      globals: {
        URL: "readonly",
        URLSearchParams: "readonly",
      },
    },
  },
);
