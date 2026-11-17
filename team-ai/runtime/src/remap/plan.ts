// Deterministic. No model calls. No network. Reads only; writes live in apply.ts.

import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

import { hasFrontmatter } from "../adopt/backfill.js";
import { namespaceIdSegment } from "../adopt/infer.js";
import { parseFrontmatter } from "../kb/frontmatter.js";
import { isExcluded } from "../kb/loader.js";
import { resolveKbScope } from "../retrieval/index-lock.js";

export interface RemapMapping {
  namespaces: Record<string, string>;
  files: Record<string, string>;
}

export type RemapStatus = "remap" | "unchanged" | "skipped" | "conflict";

export interface RemapItem {
  path: string;
  status: RemapStatus;
  from_namespace: string;
  to_namespace: string;
  from_id: string;
  to_id: string;
  reason?: string;
}

export interface RemapPlan {
  kbRoot: string;
  items: RemapItem[];
}

const FRONT_MATTER = /^(---\r?\n)([\s\S]*?)(\r?\n---(?:\r?\n|$))/;
const ID_VALUE = "[a-z0-9]+(?:\\.[a-z0-9-]+)+";
const NAMESPACE_VALUE = "[a-z0-9][a-z0-9/-]*";
const DESTINATION_NAMESPACE = /^[a-z0-9][a-z0-9/-]*$/;

interface ScalarSpan {
  start: number;
  end: number;
  value: string;
}

export interface RemapScalarSpans {
  id: ScalarSpan;
  namespace: ScalarSpan;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function validateMappingSection(value: unknown, section: string): Record<string, string> {
  if (value === undefined) return {};
  if (!isRecord(value)) {
    throw new Error(`invalid remap mapping: ${section} must be an object`);
  }

  const validated: Record<string, string> = {};
  for (const [key, target] of Object.entries(value)) {
    if (key.length === 0 || /[\r\n]/.test(key)) {
      throw new Error(`invalid remap mapping: ${section} contains an invalid key`);
    }
    if (typeof target !== "string" || !DESTINATION_NAMESPACE.test(target)) {
      throw new Error(
        `invalid remap mapping: ${section}.${key} destination must match ^[a-z0-9][a-z0-9/-]*$`,
      );
    }
    validated[key] = target;
  }
  return validated;
}

export function validateRemapMapping(value: unknown): RemapMapping {
  if (!isRecord(value)) {
    throw new Error("invalid remap mapping: expected an object");
  }
  const unknown = Object.keys(value).find((key) => key !== "namespaces" && key !== "files");
  if (unknown !== undefined) {
    throw new Error(`invalid remap mapping: unknown key '${unknown}'`);
  }
  return {
    namespaces: validateMappingSection(value.namespaces, "namespaces"),
    files: validateMappingSection(value.files, "files"),
  };
}

function findScalarSpan(
  block: string,
  blockOffset: number,
  key: string,
  valuePattern: string,
): ScalarSpan | null {
  const pattern = new RegExp(`^(${key}:[ \\t]+)(${valuePattern})([ \\t]*)(?=\\r?$)`, "gm");
  const matches = [...block.matchAll(pattern)];
  if (matches.length !== 1) return null;
  const match = matches[0];
  const prefix = match?.[1];
  const value = match?.[2];
  if (match?.index === undefined || prefix === undefined || value === undefined) return null;
  const start = blockOffset + match.index + prefix.length;
  return { start, end: start + value.length, value };
}

export function locateRemapScalarSpans(raw: string): RemapScalarSpans | null {
  const frontMatter = FRONT_MATTER.exec(raw);
  const open = frontMatter?.[1];
  const block = frontMatter?.[2];
  if (frontMatter === null || open === undefined || block === undefined) return null;
  const blockOffset = open.length;
  const id = findScalarSpan(block, blockOffset, "id", ID_VALUE);
  const namespace = findScalarSpan(block, blockOffset, "namespace", NAMESPACE_VALUE);
  return id === null || namespace === null ? null : { id, namespace };
}

function walk(dir: string, prefix = ""): string[] {
  const out: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const rel = prefix === "" ? entry.name : `${prefix}/${entry.name}`;
    if (entry.isDirectory()) out.push(...walk(join(dir, entry.name), rel));
    else if (entry.isFile() && entry.name.endsWith(".md")) out.push(rel);
  }
  return out;
}

export function rewriteId(id: string, toNamespace: string): string {
  const dot = id.indexOf(".");
  const first = namespaceIdSegment(toNamespace);
  return dot === -1 ? first : `${first}${id.slice(dot)}`;
}

function ownMappingValue(mapping: Record<string, string>, key: string): string | undefined {
  return Object.hasOwn(mapping, key) ? mapping[key] : undefined;
}

export function buildRemapPlan(opts: { instance: string; mapping: unknown }): RemapPlan {
  const mapping = validateRemapMapping(opts.mapping);
  const { root, exclude } = resolveKbScope(opts.instance);
  const items: RemapItem[] = [];
  const blank = { from_namespace: "", to_namespace: "", from_id: "", to_id: "" };

  for (const rel of walk(root)
    .filter((r) => !isExcluded(r, exclude))
    .sort()) {
    const raw = readFileSync(join(root, rel), "utf8");
    if (!hasFrontmatter(raw)) {
      items.push({ path: rel, status: "skipped", ...blank, reason: "no front matter" });
      continue;
    }
    let data: Record<string, unknown>;
    try {
      ({ data } = parseFrontmatter(raw));
    } catch (err) {
      const reason =
        err instanceof Error ? (err.message.split("\n")[0] ?? err.message) : String(err);
      items.push({
        path: rel,
        status: "conflict",
        ...blank,
        reason: `front matter does not parse: ${reason}`,
      });
      continue;
    }
    if (data.id === undefined && data.namespace === undefined) {
      items.push({
        path: rel,
        status: "skipped",
        ...blank,
        reason: "front matter is not KB front matter",
      });
      continue;
    }
    const fromNs = typeof data.namespace === "string" ? data.namespace : "";
    const fromId = typeof data.id === "string" ? data.id : "";
    const base = { path: rel, from_namespace: fromNs, from_id: fromId };
    if (fromNs === "" || fromId === "") {
      items.push({
        ...base,
        status: "conflict",
        to_namespace: "",
        to_id: "",
        reason: "missing id or namespace",
      });
      continue;
    }
    const spans = locateRemapScalarSpans(raw);
    if (spans === null || spans.id.value !== fromId || spans.namespace.value !== fromNs) {
      items.push({
        ...base,
        status: "conflict",
        to_namespace: "",
        to_id: "",
        reason: "unsupported id/namespace lexical form",
      });
      continue;
    }
    const toNs = ownMappingValue(mapping.files, rel) ?? ownMappingValue(mapping.namespaces, fromNs);
    if (toNs === undefined) {
      items.push({
        ...base,
        status: "conflict",
        to_namespace: "",
        to_id: "",
        reason: `no mapping rule for namespace '${fromNs}'`,
      });
      continue;
    }
    items.push(
      toNs === fromNs
        ? { ...base, status: "unchanged", to_namespace: fromNs, to_id: fromId }
        : { ...base, status: "remap", to_namespace: toNs, to_id: rewriteId(fromId, toNs) },
    );
  }

  return { kbRoot: root, items };
}

export function formatInventory(plan: RemapPlan): string {
  const lines = plan.items.map((i) =>
    [i.path, i.status, i.from_namespace, i.to_namespace].join("\t"),
  );
  return `path\tstatus\tfrom\tto\n${lines.join("\n")}\n`;
}
