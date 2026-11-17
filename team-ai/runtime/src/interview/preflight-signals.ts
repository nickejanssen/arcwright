// Deterministic. No model calls. No network.
//
// Editable signal lists for the preflight scan (interview-spec.md §4,
// architecture.md §4). A fork edits these to match its own environment; the
// scanner in preflight.ts carries no hardcoded paths of its own, so every
// signal it looks for is visible and overridable here.

export const MCP_CONFIG_FILES = [".mcp.json", ".cursor/mcp.json", ".vscode/mcp.json"];

export const AGENT_CONFIG_FILES = ["CLAUDE.md", "AGENTS.md", ".github/copilot-instructions.md"];
export const AGENT_CONFIG_DIRS = [".claude", ".codex", ".cursor", ".agents"];

export const VECTOR_ENV_HINTS = [
  "PINECONE_",
  "WEAVIATE_",
  "QDRANT_",
  "PGVECTOR",
  "LANCEDB",
  "CHROMA_",
  "MILVUS_",
];

// Marker files/paths that indicate an org-wide enterprise-search deployment
// already covers this content. Generic and editable.
// Add your org's enterprise-search marker paths here.
export const ORG_SEARCH_MARKERS = [".confluence-ai", ".glean", "docs/.enterprise-search"];

export const SKILL_PLUGIN_DIRS = ["skills", ".claude/skills", ".claude/commands"];
