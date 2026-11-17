// Approximate — ~1.3 tokens/word heuristic, no tokenizer dependency (deterministic).

import type { FrontMatter } from "../schema/types.js";
import { scanLines } from "./headings.js";
import { slug } from "./slugify.js";
import type { KbDoc } from "./types.js";

// Re-exported for existing importers; canonical home is ./slugify.js.
export { slug } from "./slugify.js";

export interface Chunk {
  doc_id: string;
  chunk_id: string;
  path: string;
  heading_path: string;
  text: string;
  metadata: FrontMatter;
}

// Hard ceiling for a single chunk; sections above this are split at paragraphs.
const HARD_CAP = 1200;
// Greedy packing target when splitting an oversized section.
const TARGET = 800;

export function estimateTokens(text: string): number {
  const wordCount = text.trim().split(/\s+/).filter(Boolean).length;
  return Math.ceil(wordCount * 1.3);
}

interface Section {
  headingPath: string;
  text: string;
}

function splitSections(body: string, title: string): Section[] {
  const sections: Section[] = [];
  const stack: [string | undefined, string | undefined] = [undefined, undefined];
  let currentLines: string[] = [];
  let currentPath = title;
  let inPreamble = true;

  const headingPath = (): string =>
    [title, stack[0], stack[1]].filter((s): s is string => Boolean(s)).join(" > ");

  const flush = (): void => {
    if (inPreamble) {
      const text = currentLines.join("\n").trim();
      if (text.length === 0) return;
      sections.push({ headingPath: currentPath, text });
      return;
    }
    // Non-preamble sections open with their heading line; skip any whose body
    // (everything after that line) is empty or whitespace-only.
    const headingLine = (currentLines[0] ?? "").replace(/\s+$/, "");
    const body = currentLines.slice(1).join("\n").trim();
    if (body.length === 0) return;
    sections.push({ headingPath: currentPath, text: `${headingLine}\n${body}` });
  };

  scanLines(body, (line, heading) => {
    if (heading && (heading.level === 2 || heading.level === 3)) {
      flush();
      inPreamble = false;
      if (heading.level === 2) {
        stack[0] = heading.text;
        stack[1] = undefined;
      } else {
        stack[1] = heading.text;
      }
      currentPath = headingPath();
      currentLines = [line];
    } else {
      currentLines.push(line);
    }
  });
  flush();

  return sections;
}

// Greedily pack paragraphs toward TARGET without exceeding HARD_CAP where
// avoidable. A single paragraph over HARD_CAP stays whole.
function packParagraphs(paragraphs: string[]): string[] {
  const parts: string[] = [];
  let buffer: string[] = [];
  let bufferTokens = 0;

  for (const paragraph of paragraphs) {
    const tokens = estimateTokens(paragraph);
    if (buffer.length === 0) {
      buffer = [paragraph];
      bufferTokens = tokens;
      continue;
    }
    const combined = bufferTokens + tokens;
    if (bufferTokens < TARGET && combined <= HARD_CAP) {
      buffer.push(paragraph);
      bufferTokens = combined;
    } else {
      parts.push(buffer.join("\n\n"));
      buffer = [paragraph];
      bufferTokens = tokens;
    }
  }
  if (buffer.length > 0) parts.push(buffer.join("\n\n"));
  return parts;
}

function sectionTexts(section: Section): string[] {
  if (estimateTokens(section.text) <= HARD_CAP) return [section.text];
  const paragraphs = section.text
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .filter(Boolean);
  return packParagraphs(paragraphs);
}

export function chunkDoc(doc: KbDoc): Chunk[] {
  const sections = splitSections(doc.body, doc.frontmatter.title);
  const chunks: Chunk[] = [];
  // Keyed by the slug (not the raw heading path) so distinct heading paths that
  // slug to the same value disambiguate via the ordinal (::0, ::1, ...) instead
  // of colliding on an identical chunk_id.
  const ordinals = new Map<string, number>();

  for (const section of sections) {
    const headingSlug = slug(section.headingPath);
    for (const text of sectionTexts(section)) {
      const ordinal = ordinals.get(headingSlug) ?? 0;
      ordinals.set(headingSlug, ordinal + 1);
      chunks.push({
        doc_id: doc.id,
        chunk_id: `${doc.id}::${headingSlug}::${ordinal}`,
        path: doc.path,
        heading_path: section.headingPath,
        text,
        metadata: doc.frontmatter,
      });
    }
  }

  return chunks;
}
