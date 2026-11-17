import type { AdoptionPlan } from "../adopt/types.js";
import type { NamespacePreset, RoleArchetype, SkillCatalogEntry } from "../catalog/types.js";
import type { QuestionBankFile } from "../interview/types.js";
import { loadValidator, type SchemaName } from "./load.js";
import type {
  AgentDef,
  FrontMatter,
  GoldenQuestion,
  Manifest,
  SpokeConfig,
  TeamProfile,
} from "./types.js";

export interface SchemaTypeMap {
  frontmatter: FrontMatter;
  agent: AgentDef;
  manifest: Manifest;
  spoke: SpokeConfig;
  "team-profile": TeamProfile;
  golden: GoldenQuestion;
  "namespace-preset": NamespacePreset;
  role: RoleArchetype;
  "skill-catalog": SkillCatalogEntry;
  questions: QuestionBankFile;
  "adoption-plan": AdoptionPlan;
}

export type ValidateResult<T> = { ok: true; value: T } | { ok: false; errors: string[] };

interface AjvErrorLike {
  instancePath?: string;
  message?: string;
  keyword?: string;
  params?: Record<string, unknown>;
}

function formatError(error: AjvErrorLike): string {
  const where = error.instancePath ?? "";
  const prefix = where.length > 0 ? where : "(root)";
  let message = error.message ?? "is invalid";
  const params = error.params ?? {};

  if (error.keyword === "additionalProperties" && typeof params.additionalProperty === "string") {
    message += ` (${params.additionalProperty})`;
  }

  const allowed: unknown = params.allowedValues;
  if (error.keyword === "enum" && Array.isArray(allowed)) {
    const values = (allowed as unknown[]).map((v) => String(v)).join(", ");
    message += ` (allowed: ${values})`;
  }

  return `${prefix} ${message}`.trim();
}

export function validate<N extends SchemaName>(
  name: N,
  data: unknown,
): ValidateResult<SchemaTypeMap[N]> {
  const v = loadValidator(name);
  if (!v) return { ok: false, errors: [`schema ${name} not found`] };
  if (v(data)) return { ok: true, value: data as SchemaTypeMap[N] };
  const errors = (v.errors ?? []).map((e) => formatError(e));
  return { ok: false, errors: errors.length > 0 ? errors : ["schema validation failed"] };
}
