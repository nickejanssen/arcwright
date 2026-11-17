import { describe, expect, it } from "vitest";

import { NotImplementedError } from "./not-implemented.js";
import {
  GraphAdapter,
  HybridAdapter,
  VectorEmbeddedAdapter,
  VectorHostedAdapter,
  VectorPgvectorAdapter,
} from "./stubs.js";

const cases = [
  ["graph", new GraphAdapter()],
  ["hybrid", new HybridAdapter()],
  ["vector-embedded", new VectorEmbeddedAdapter()],
  ["vector-hosted", new VectorHostedAdapter()],
  ["vector-pgvector", new VectorPgvectorAdapter()],
] as const;

describe("stub adapters", () => {
  for (const [name, adapter] of cases) {
    it(`${name}: every method rejects with NotImplementedError naming the driver + checkpoint`, async () => {
      await expect(adapter.search("q")).rejects.toThrow(NotImplementedError);
      await expect(adapter.search("q")).rejects.toThrow(new RegExp(name));
      await expect(adapter.search("q")).rejects.toThrow(/phase-8|§19|architecture\.md/);
      await expect(adapter.get("x")).rejects.toThrow(NotImplementedError);
      await expect(adapter.reindex()).rejects.toThrow(NotImplementedError);
    });
  }
});
