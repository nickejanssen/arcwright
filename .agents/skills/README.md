# Codex skill launchers

These are thin launchers that expose Arcwright's canonical role skills to Codex through the `.agents/skills/<name>` discovery path. Each `SKILL.md` here carries only frontmatter (name and description, for discovery and triggering) and a pointer to the canonical contract under `docs/skills/`. The role logic lives only in `docs/skills/`, so there is one source of truth.

Why pointers and not symlinks or copies:

- Symlinks are not used because this repository has `core.symlinks = false`; a committed symlink would arrive as a broken text file on other clones (notably on Windows). 
- Copies are not used because they would duplicate the role logic and drift from the canonical `docs/skills/` contract, which the repo's thin-launcher rule forbids.

To change a role's behavior, edit the canonical file under `docs/skills/<name>/SKILL.md`. These launchers should not need to change unless the skill is renamed or its trigger description changes.

Instruction source: Codex reads `AGENTS.md` (root-down) as the always-on rules. These launchers do not restate rules.
