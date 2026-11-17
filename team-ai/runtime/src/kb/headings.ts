// Fence-aware ATX heading scanning shared by the KB loader and chunker. Tracks
// ``` / ~~~ fenced code blocks so heading-looking lines inside them are ignored.

const ATX_HEADING = /^(#{1,6})\s+(.+)$/;
const FENCE = /^(```|~~~)/;

export interface ScannedHeading {
  level: number;
  text: string;
}

// Walk every line of `body` in document order. `visit` receives the raw line
// and, when the line is an ATX heading outside a fenced code block, its parsed
// level and text; otherwise `null`.
export function scanLines(
  body: string,
  visit: (line: string, heading: ScannedHeading | null) => void,
): void {
  let inFence = false;
  for (const rawLine of body.split("\n")) {
    const line = rawLine.replace(/\r$/, "");
    if (FENCE.test(line)) {
      inFence = !inFence;
      visit(line, null);
      continue;
    }
    if (inFence) {
      visit(line, null);
      continue;
    }
    const match = ATX_HEADING.exec(line);
    const hashes = match?.[1];
    const text = match?.[2];
    visit(line, hashes && text ? { level: hashes.length, text: text.trim() } : null);
  }
}

// Extract ATX heading text in document order, ignoring headings inside fences.
export function extractHeadings(body: string): string[] {
  const headings: string[] = [];
  scanLines(body, (_line, heading) => {
    if (heading) headings.push(heading.text);
  });
  return headings;
}
