#!/usr/bin/env bash
# Task 39 dogfood harness — convenience runner. The CI-durable version is
# src/generator/dogfood.test.ts (run by `npx vitest run`). This script drives
# the built CLI end to end and exits non-zero on the first failure.
#
#   Run A       team-ai init, Arcwright as the preflight target  (needs the repo)
#   Run A-recon hand-authored files survive an adopt-existing run (needs the repo)
#   Run A-adopt team-ai adopt against the real Arcwright, read-only (needs the repo)
#   Run B       team-ai init for a Partner Solutions profile      (always)
#
# All generated output goes under .tmp-dogfood/ (gitignored). Arcwright is only
# ever read; the script asserts its git status is unchanged around each run.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ARCWRIGHT="${ARCWRIGHT_REPO:-C:/Users/nicke/OneDrive/Desktop/arcwright}"
CLI="node dist/cli.js"
WORK=".tmp-dogfood"
ARC_ANSWERS="test/fixtures/answers/dogfood-arcwright.yaml"
PARTNER_ANSWERS="test/fixtures/answers/dogfood-partner-solutions.yaml"

fail() { echo "DOGFOOD FAIL: $*" >&2; exit 1; }
have_arcwright() { [ -f "$ARCWRIGHT/AGENTS.md" ]; }

# The guarantee is "team-ai never writes into the measured repo", not "the repo
# is frozen" — a parallel process on the machine may edit Arcwright mid-run. So
# assert no team-ai output artifact shows up in its git status.
assert_arcwright_untouched() {
  if git -C "$ARCWRIGHT" status --porcelain \
      | grep -Eq 'adoption-plan|\.team-ai|team-profile\.yaml|index\.lock'; then
    git -C "$ARCWRIGHT" status --porcelain | grep -E 'adoption-plan|\.team-ai|team-profile\.yaml|index\.lock' >&2
    fail "team-ai wrote an artifact into Arcwright"
  fi
}

rm -rf "$WORK"
mkdir -p "$WORK"
[ -f dist/cli.js ] || fail "build first: npm run build"

six_checks() {
  local dir="$1"
  $CLI validate-kb --root "$dir/kb" --schema-only || fail "validate-kb ($dir)"
  $CLI validate-citations --root "$dir" || fail "validate-citations ($dir)"
  $CLI reindex --root "$dir" || fail "reindex ($dir)"
  $CLI search "charter" --root "$dir" --json \
    | node -e "let d='';process.stdin.on('data',c=>d+=c).on('end',()=>process.exit(JSON.parse(d).length?0:1))" \
    || fail "search returned no hits ($dir)"
  $CLI assemble-manifest --root "$dir" || fail "assemble-manifest ($dir)"
  $CLI doctor --root "$dir" || fail "doctor ($dir)"
}

if have_arcwright; then
  echo "== Run A: team-ai init (Arcwright preflight) =="
  $CLI init --dir "$WORK/arcwright" --answers "$ARC_ANSWERS" \
    --preflight-target "$ARCWRIGHT" --on-conflict adopt-existing | tee "$WORK/runA-init.log"
  grep -q "Assessment: EXTEND" "$WORK/runA-init.log" || fail "Run A preflight not EXTEND"
  grep -q "agent config file: AGENTS.md" "$WORK/runA-init.log" || fail "Run A missing AGENTS.md asset"
  six_checks "$WORK/arcwright"
  node -e "require('yaml').parse(require('fs').readFileSync('$WORK/arcwright/.github/workflows/validate.yml','utf8'))" \
    || fail "Run A validate.yml is not valid YAML"
  grep -q "validate-kb.reusable.yml@v0" "$WORK/arcwright/.github/workflows/validate.yml" \
    || fail "Run A validate.yml does not reference the reusable workflow"

  echo "== Run A reconciliation (adopt-existing) =="
  mkdir -p "$WORK/arcwright-recon/agents"
  cp "$ARCWRIGHT/AGENTS.md" "$WORK/arcwright-recon/AGENTS.md"
  printf '# HAND AUTHORED SENTINEL\n' > "$WORK/arcwright-recon/agents/sme.yaml"
  A0="$(sha256sum < "$WORK/arcwright-recon/AGENTS.md")"
  S0="$(sha256sum < "$WORK/arcwright-recon/agents/sme.yaml")"
  $CLI init --dir "$WORK/arcwright-recon" --answers "$ARC_ANSWERS" \
    --preflight-target "$ARCWRIGHT" --on-conflict adopt-existing > "$WORK/runA-recon.log" 2>&1
  [ "$(sha256sum < "$WORK/arcwright-recon/AGENTS.md")" = "$A0" ] || fail "AGENTS.md changed"
  [ "$(sha256sum < "$WORK/arcwright-recon/agents/sme.yaml")" = "$S0" ] || fail "sme.yaml changed"
  [ ! -e "$WORK/arcwright-recon/agents/sme.yaml.team-ai-new" ] || fail "unexpected sibling in adopt-existing"
  grep -q "Coexistence boundary" "$WORK/arcwright-recon/docs/architecture.md" || fail "no coexistence boundary"
  grep -q "AGENTS.md" "$WORK/arcwright-recon/docs/architecture.md" || fail "coexistence boundary omits AGENTS.md"

  echo "== Run A reconciliation (siblings) =="
  mkdir -p "$WORK/arcwright-recon-sib/agents"
  printf '# HAND AUTHORED SENTINEL\n' > "$WORK/arcwright-recon-sib/agents/sme.yaml"
  $CLI init --dir "$WORK/arcwright-recon-sib" --answers "$ARC_ANSWERS" \
    --preflight-target "$ARCWRIGHT" --on-conflict siblings > "$WORK/runA-recon-sib.log" 2>&1
  [ -e "$WORK/arcwright-recon-sib/agents/sme.yaml.team-ai-new" ] || fail "siblings mode wrote no .team-ai-new"
  grep -q "HAND AUTHORED SENTINEL" "$WORK/arcwright-recon-sib/agents/sme.yaml" || fail "sentinel clobbered"

  echo "== Run A-adopt (read-only against real Arcwright) =="
  $CLI adopt --root "$ARCWRIGHT" --out "$WORK/arcwright-adopt" --horizon-days 180 | tee "$WORK/runA-adopt.log"
  [ -f "$WORK/arcwright-adopt/adoption-plan.yaml" ] || fail "no adoption-plan.yaml"
  [ -f "$WORK/arcwright-adopt/docs/adoption-plan.md" ] || fail "no adoption-plan.md"
  node -e "
    const y=require('yaml'),fs=require('fs');
    const p=y.parse(fs.readFileSync('$WORK/arcwright-adopt/adoption-plan.yaml','utf8'));
    if(p.gap.length!==17) throw new Error('gap length '+p.gap.length);
    if(p.backfill.length===0) throw new Error('no backfill');
    if(p.namespace_map.decisions.length===0) throw new Error('no namespace decisions');
  " || fail "adoption plan shape wrong"
  grep -q "archived/generated docs" "$WORK/runA-adopt.log" || fail "Run A-adopt missing archived-skip line"

  assert_arcwright_untouched
  echo "Arcwright carries no team-ai artifacts."
else
  echo "== Arcwright repo not found at $ARCWRIGHT — skipping Run A / A-adopt =="
fi

echo "== Run B: team-ai init (Partner Solutions) =="
$CLI init --dir "$WORK/partner-solutions" --answers "$PARTNER_ANSWERS" | tee "$WORK/runB-init.log"
six_checks "$WORK/partner-solutions"
ROLE_FILES="$(find "$WORK/partner-solutions/agents/roles" -type f \( -name '*.yaml' -o -name '*.md' \) 2>/dev/null | wc -l)"
[ "$ROLE_FILES" -eq 0 ] || fail "Run B (size 1-3) generated role subagent files"
grep -q "when a 2nd coding client appears" "$WORK/partner-solutions/docs/architecture.md" || fail "Run B missing local-stdio gate note"
grep -q "after 2 asks from people who cannot clone the repo" "$WORK/partner-solutions/docs/architecture.md" || fail "Run B missing remote gate note"

echo
echo "DOGFOOD OK"
rm -rf "$WORK"
