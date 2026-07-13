// The DurableObject base class is a real runtime import at Cloudflare
// Workers deploy time (not an ambient global) — it must come from the
// "cloudflare:workers" virtual module, matching actual runtime behavior.
//
// This ambient module declaration must live in a file with no top-level
// import/export of its own. In a file that is itself a module (like
// cloudflare.d.ts, which has `export {}`), `declare module "x"` means
// "augment the existing module x" rather than "declare a new ambient
// module x", and TypeScript rejects it because no real "cloudflare:workers"
// module can be resolved to augment.
declare module "cloudflare:workers" {
  export class DurableObject {
    constructor(state: DurableObjectState, env: unknown);
  }
}
