import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { Ajv2020 } from "ajv/dist/2020.js";
import type { AnySchema } from "ajv/dist/2020.js";
import type { AnyValidateFunction } from "ajv/dist/core.js";
import addFormatsModule from "ajv-formats";

// Under NodeNext + verbatimModuleSyntax the CommonJS `ajv-formats` default
// import resolves to the module namespace; the callable plugin is `.default`.
const addFormats = addFormatsModule.default;

export type SchemaName =
  | "frontmatter"
  | "agent"
  | "manifest"
  | "spoke"
  | "team-profile"
  | "golden"
  | "namespace-preset"
  | "role"
  | "skill-catalog"
  | "questions"
  | "adoption-plan";

const ajv = addFormats(new Ajv2020({ allErrors: true, strict: true }));

export function schemaPath(name: SchemaName): string {
  return fileURLToPath(new URL(`../../schemas/${name}.schema.json`, import.meta.url));
}

export function loadValidator(name: SchemaName): AnyValidateFunction<unknown> | undefined {
  const key = `team-ai/${name}`;
  const existing = ajv.getSchema(key);
  if (existing) return existing;
  const schema = JSON.parse(readFileSync(schemaPath(name), "utf8")) as AnySchema;
  ajv.addSchema(schema, key);
  return ajv.getSchema(key);
}
