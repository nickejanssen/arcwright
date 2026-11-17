// Deterministic. No model calls. No network.
//
// Rewrites only the `id` and `namespace` scalar values inside the front-matter
// block. The value pattern stops before `\r`, so CRLF files keep their line
// endings. Refuses to touch any file while the plan contains a conflict.

import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import { locateRemapScalarSpans, type RemapItem, type RemapPlan } from "./plan.js";

function replaceScalar(raw: string, start: number, end: number, value: string): string {
  return `${raw.slice(0, start)}${value}${raw.slice(end)}`;
}

function renderItem(raw: string, item: RemapItem): string {
  const spans = locateRemapScalarSpans(raw);
  if (spans === null) {
    throw new Error(`refusing to apply: ${item.path} has an unsupported lexical form`);
  }
  if (spans.id.value === item.to_id && spans.namespace.value === item.to_namespace) {
    return raw;
  }
  if (spans.id.value !== item.from_id || spans.namespace.value !== item.from_namespace) {
    throw new Error(`refusing to apply: ${item.path} changed after planning`);
  }

  const replacements = [
    { ...spans.id, value: item.to_id },
    { ...spans.namespace, value: item.to_namespace },
  ].sort((a, b) => b.start - a.start);
  let next = raw;
  for (const replacement of replacements) {
    next = replaceScalar(next, replacement.start, replacement.end, replacement.value);
  }
  return next;
}

export function applyRemapPlan(plan: RemapPlan): { written: string[] } {
  const conflicts = plan.items.filter((i) => i.status === "conflict");
  if (conflicts.length > 0) {
    throw new Error(
      `refusing to apply: ${conflicts.length} conflict(s), first: ${conflicts[0]?.path} (${conflicts[0]?.reason ?? "conflict"})`,
    );
  }

  const prepared: { path: string; abs: string; content: string }[] = [];
  for (const item of plan.items) {
    if (item.status !== "remap") continue;
    const abs = join(plan.kbRoot, item.path);
    const raw = readFileSync(abs, "utf8");
    const next = renderItem(raw, item);
    if (next !== raw) prepared.push({ path: item.path, abs, content: next });
  }

  for (const item of prepared) {
    writeFileSync(item.abs, item.content, "utf8");
  }
  return { written: prepared.map((item) => item.path) };
}
