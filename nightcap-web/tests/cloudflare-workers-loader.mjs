// Test-only ESM loader hook. Node has no built-in resolver for the
// "cloudflare:" URL scheme that Wrangler provides at real deploy time
// (see src/cloudflare-workers-module.d.ts for why room.ts imports
// DurableObject from "cloudflare:workers" rather than using it as a
// global). This hook substitutes a minimal stub so `node --test` can run
// the same source without a real Workers runtime. Preloaded via
// `node --import ./tests/register-cloudflare-workers-loader.mjs`.

const STUB_URL = "cloudflare-workers-stub:main";

export async function resolve(specifier, context, nextResolve) {
  if (specifier === "cloudflare:workers") {
    return { url: STUB_URL, shortCircuit: true };
  }
  return nextResolve(specifier, context);
}

export async function load(url, context, nextLoad) {
  if (url === STUB_URL) {
    return {
      format: "module",
      shortCircuit: true,
      source: `
        export class DurableObject {
          constructor(state, env) {
            this.ctx = state;
            this.env = env;
          }
        }
      `,
    };
  }
  return nextLoad(url, context);
}
