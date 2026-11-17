import matter from "gray-matter";
import { Document, parse as parseYaml, visit } from "yaml";

export interface ParsedDoc {
  data: Record<string, unknown>;
  body: string;
}

// Matches ISO-8601 date / date-time scalars (e.g. `2027-01-01`, `2027-01-01T09:00:00Z`).
const ISO_DATE = /^\d{4}-\d{2}-\d{2}([T ][\d:.+-]*(Z)?)?$/;

// Serialize front matter with the `yaml` package, force-quoting any string that
// looks like an ISO date. The `yaml` core schema keeps bare `2027-01-01` as a
// string, but YAML-1.1 consumers (js-yaml, GitHub) re-coerce it to a timestamp;
// quoting keeps the value a string wherever a serialized doc is later read.
// Note: YAML comments and anchors in front matter are NOT preserved on round-trip.
function stringifyFrontmatterYaml(value: object): string {
  const doc = new Document(value);
  visit(doc, {
    Scalar(_key, node) {
      if (typeof node.value === "string" && ISO_DATE.test(node.value)) {
        node.type = "QUOTE_DOUBLE";
      }
    },
  });
  return doc.toString();
}

// Parse and serialize both go through the `yaml` package so the two operations
// are symmetric. gray-matter's bundled js-yaml engine coerces bare `2027-01-01`
// scalars into `Date` objects, which would break front matter validation and
// round-tripping; the `yaml` core schema keeps them as strings.
const engines = {
  yaml: {
    parse: (input: string): object => {
      const parsed: unknown = parseYaml(input);
      return parsed !== null && typeof parsed === "object" ? parsed : {};
    },
    stringify: (input: object): string => stringifyFrontmatterYaml(input),
  },
};

// Front matter schema property order. Serialization emits known keys in this
// order, then any remaining keys in insertion order.
const KEY_ORDER = [
  "id",
  "namespace",
  "title",
  "owner",
  "status",
  "review_by",
  "sensitivity",
  "source",
  "source_url",
  "tags",
  "supersedes",
  "relations",
] as const;

export function parseFrontmatter(raw: string): ParsedDoc {
  const parsed = matter(raw.replace(/\r\n?/g, "\n"), { engines });
  const data: Record<string, unknown> = { ...parsed.data };
  return {
    data,
    body: parsed.content.replace(/^\s+/, ""),
  };
}

export function serializeFrontmatter(data: Record<string, unknown>, body: string): string {
  const ordered: Record<string, unknown> = {};
  for (const key of KEY_ORDER) {
    if (Object.prototype.hasOwnProperty.call(data, key)) ordered[key] = data[key];
  }
  for (const key of Object.keys(data)) {
    if (!Object.prototype.hasOwnProperty.call(ordered, key)) ordered[key] = data[key];
  }
  return `---\n${stringifyFrontmatterYaml(ordered)}---\n\n${body.replace(/^\s+/, "")}\n`;
}
