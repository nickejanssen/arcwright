import { KbValidationError, loadKb } from "../kb/loader.js";
import { checkRelations } from "../kb/relations.js";
import { resolveKbScope } from "../retrieval/index-lock.js";

export interface ValidateKbOptions {
  root?: string;
  instance?: string;
  schemaOnly?: boolean;
}

export async function run(opts: ValidateKbOptions): Promise<number> {
  const scope =
    opts.instance === undefined
      ? { root: opts.root ?? "kb", exclude: [] }
      : resolveKbScope(opts.instance);
  const schemaOnly = opts.schemaOnly ?? false;

  const loaded = await load(scope.root, scope.exclude);
  if (!loaded.ok) {
    for (const line of loaded.errors) console.error(line);
    return 1;
  }
  const docs = loaded.docs;

  if (schemaOnly) {
    console.log(`OK ${docs.length} document(s)`);
    return 0;
  }

  const knownRoles = new Set(docs.map((doc) => doc.frontmatter.owner));
  const relationErrors = checkRelations(docs, knownRoles);
  if (relationErrors.length > 0) {
    for (const err of relationErrors) {
      console.error(
        `${err.doc_id}: relation '${err.relation}' value '${err.value}' — ${err.reason}`,
      );
    }
    return 1;
  }

  console.log(`OK ${docs.length} document(s), relations valid`);
  return 0;
}

type LoadOutcome =
  { ok: true; docs: Awaited<ReturnType<typeof loadKb>> } | { ok: false; errors: string[] };

async function load(root: string, exclude: string[]): Promise<LoadOutcome> {
  try {
    return { ok: true, docs: await loadKb(root, { exclude }) };
  } catch (err) {
    if (err instanceof KbValidationError) {
      return { ok: false, errors: err.failures.map((f) => `${f.file}: ${f.error}`) };
    }
    return { ok: false, errors: [err instanceof Error ? err.message : String(err)] };
  }
}
