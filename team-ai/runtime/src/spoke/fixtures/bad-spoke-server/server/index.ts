// Fixture only: a spoke must not ship server-side retrieval code like this.
// Retrieval, server code, and indexing all live in the core repo.
export function handleQuery(query: string): string {
  return `the core repo owns retrieval, not the spoke: ${query}`;
}
