// Neutral slug helper shared by the chunker, citation resolver, and heading tools.

// Lowercase, collapse runs of non-[a-z0-9] to a single `-`, trim leading/trailing `-`.
export function slug(headingPath: string): string {
  return headingPath
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+/, "")
    .replace(/-+$/, "");
}
