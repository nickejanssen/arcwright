// Deterministic. No model calls. No network.
//
// proposeNamespaceMap lines a repo's top-level doc folders up against a
// namespace preset shape. It matches on exact name, then singular/plural, then a
// small fixed synonym table; anything left over gets the three closest preset
// names by edit distance plus a `custom` escape hatch, for a human to pick from.

export interface NamespaceMatch {
  folder: string;
  namespace: string;
}

export interface NamespaceUnmatched {
  folder: string;
  candidates: string[];
}

export interface NamespaceProposal {
  matched: NamespaceMatch[];
  unmatched: NamespaceUnmatched[];
}

// Only the unambiguous synonyms. `prd` / `product` / `requirements` and
// `story-bibles` are deliberately left to fall through to the candidate list.
const SYNONYMS: Record<string, string> = {
  arch: "architecture",
  adr: "decisions",
  adrs: "decisions",
  runbooks: "playbooks",
  guides: "playbooks",
  examples: "patterns",
  charter: "operating",
  team: "operating",
};

function levenshtein(a: string, b: string): number {
  const rows = a.length + 1;
  const cols = b.length + 1;
  const dist: number[] = new Array<number>(rows * cols).fill(0);
  for (let i = 0; i < rows; i += 1) dist[i * cols] = i;
  for (let j = 0; j < cols; j += 1) dist[j] = j;
  for (let i = 1; i < rows; i += 1) {
    for (let j = 1; j < cols; j += 1) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      const del = (dist[(i - 1) * cols + j] ?? 0) + 1;
      const ins = (dist[i * cols + (j - 1)] ?? 0) + 1;
      const sub = (dist[(i - 1) * cols + (j - 1)] ?? 0) + cost;
      dist[i * cols + j] = Math.min(del, ins, sub);
    }
  }
  return dist[rows * cols - 1] ?? 0;
}

function matchFolder(folder: string, presetShape: string[]): string | null {
  const f = folder.toLowerCase();
  if (presetShape.includes(f)) return f;

  for (const preset of presetShape) {
    if (`${preset}s` === f || `${f}s` === preset) return preset;
    if (f.endsWith("s") && f.slice(0, -1) === preset) return preset;
    if (preset.endsWith("s") && preset.slice(0, -1) === f) return preset;
  }

  return SYNONYMS[f] ?? null;
}

function closestNames(folder: string, presetShape: string[]): string[] {
  return [...presetShape]
    .map((name) => ({ name, distance: levenshtein(folder.toLowerCase(), name) }))
    .sort((a, b) => a.distance - b.distance || (a.name < b.name ? -1 : a.name > b.name ? 1 : 0))
    .slice(0, 3)
    .map((entry) => entry.name);
}

export function proposeNamespaceMap(folders: string[], presetShape: string[]): NamespaceProposal {
  const matched: NamespaceMatch[] = [];
  const unmatched: NamespaceUnmatched[] = [];

  for (const folder of folders) {
    const namespace = matchFolder(folder, presetShape);
    if (namespace !== null) {
      matched.push({ folder, namespace });
    } else {
      unmatched.push({ folder, candidates: [...closestNames(folder, presetShape), "custom"] });
    }
  }

  matched.sort((a, b) => (a.folder < b.folder ? -1 : a.folder > b.folder ? 1 : 0));
  return { matched, unmatched };
}
