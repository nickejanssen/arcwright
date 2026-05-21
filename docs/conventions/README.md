# Conventions and Guidelines

This directory contains team conventions for code, testing, and contributions. These documents establish shared standards and make it easier for multiple contributors (especially AI agents) to understand and maintain the codebase.

## Structure

- **coding-style.md**: Python and TypeScript style, naming, file organization
- **testing.md**: Test structure, coverage, unit vs. integration testing philosophy
- **ai-contributions.md**: How AI agents should approach code changes, context, and uncertainty
- **ai-cost-policy.md**: Guidelines for token usage, model selection, batch operations, and budget awareness

## Using These Conventions

### For Code Contributors

1. Read the applicable convention file (e.g., coding-style.md for style, testing.md for tests)
2. Follow the style and structure described
3. When uncertain, default to existing code patterns in the repo

### For AI Agents

1. **Before starting work**: Read ai-contributions.md and ai-cost-policy.md
2. **During work**: Check coding-style.md and testing.md
3. **For new patterns**: Propose them in ai-contributions.md with ADR support

### For Maintainers

1. Use these documents to onboard new contributors
2. Link to conventions in code review comments
3. Update conventions when they become outdated

## Adding or Updating Conventions

- Propose changes as ADRs if they affect architecture or significant policy
- Update existing files directly for clarifications or new patterns
- Keep conventions concise and linked to actual code examples

---

See the individual files for details on each area.
