export {};

declare global {
  interface DurableObjectId {
    toString(): string;
  }

  interface DurableObjectStorage {
    get<T>(key: string): Promise<T | undefined>;
    put<T>(key: string, value: T): Promise<void>;
    delete(key: string): Promise<void>;
  }

  interface DurableObjectState {
    id: DurableObjectId;
    storage: DurableObjectStorage;
  }

  interface DurableObjectNamespace<T = unknown> {
    idFromName(name: string): DurableObjectId;
    get(id: DurableObjectId): T;
  }

  class DurableObject {
    constructor(state: DurableObjectState, env: unknown);
  }

  interface ExecutionContext {
    waitUntil(promise: Promise<unknown>): void;
  }

  // Service-style binding used by Cloudflare's [assets] directive and any
  // other Worker-to-Worker fetch. We model only what the worker calls.
  interface Fetcher {
    fetch(request: Request): Promise<Response>;
  }
}
