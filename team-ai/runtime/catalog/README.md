# Catalog

The catalog is the set of presets team-ai ships: reusable, team-agnostic
building blocks you select from when standing up an instance. Nothing here names
a real team, company, or product — placeholders like `<name>` and `<domain>`
mark where your own values go.

## Subdirectories

| Dir           | Kind                | Format     | Schema                             |
| ------------- | ------------------- | ---------- | ---------------------------------- |
| `namespaces/` | Knowledge namespace | `*.yaml`   | `schemas/namespace-preset.schema.json` |
| `roles/`      | Role archetype      | `*.yaml`   | `schemas/role.schema.json`         |
| `skills/`     | Skill catalog entry | `*.yaml`   | `schemas/skill-catalog.schema.json` |
| `personas/`   | Persona (tone only) | `*.md`     | none — front matter + prose        |

Each entry is keyed by its filename without the extension (`roles/architect.yaml`
→ `architect`).

## Three-layer resolution

`resolveCatalog` reads three layers in order and later layers win:

1. **toolkit** — this directory, shipped with the framework.
2. **org** — an optional shared layer for a fork used by several teams.
3. **instance** — an optional per-team layer inside a generated instance.

For a given key, a later layer **replaces** the earlier entry outright (no field
merge) and the resolved item records its `origin` (`toolkit` / `org` /
`instance`). A missing layer, or a missing kind subdir within a layer, is
skipped.

## Overriding a shipped entry

Add a file with the **same stem** under the instance (or org) `catalog/`
subdir. `catalog/roles/architect.yaml` in your instance fully replaces the
toolkit `architect` role. YAML entries are still validated against the schema
above; a malformed or invalid file fails resolution with
`catalog: <file>: <reason>`.

## Adding a custom entry

For a namespace, role, skill, or persona the toolkit does not ship, generate a
fill-in stub with `generateStub(name, kind)` (`src/catalog/stub.ts`). The stub
lays out every required field with a `# TODO:` on each value — it never guesses
content. Fill in every TODO before the entry is used.
