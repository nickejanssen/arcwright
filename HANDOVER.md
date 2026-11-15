# HANDOVER

> Read `AGENTS.md` first, then this file, before touching code. It is the short start-of-session brief for every agent (Claude, Codex, Copilot) and for the founder. If it disagrees with a current source, investigate before acting, then fix this file. Keep it short and link to the owner of each detail.

Last updated: 2026-11-15, against main `14f12e2`.

## System map

**Arcwright** is the engine: the dungeon master for any game built on it. It runs a human-written story, tracks who knows what, voices characters, paces play, and decides outcomes by rule. Python, in `engine/` and `api/`. See `docs/architecture/01-overview.md`, sections 1.6 and 1.7.

**Nightcap** is the first game on it: a murder mystery on a TV with phones. Its design authority is `docs/gdd/nightcap/`. Its content lives in `nightcap/`. Its screens live in `dashboard/` and `nightcap-web/` (two sets; AW-300 picks one).

Keep them apart. Nothing in `engine/` may name Nightcap or assume a murder mystery.

## Where things stand

- The playable build is the older Couch Race design. The current design (the Master GDD) is not built.
- The rebuild plan is `docs/specs/0092-nightcap-gdd-rebuild.md`. Draft, not approved. Building is blocked on the founder's approval (issue #303).
- Target: a thin, complete game played by friends at the founder's house on 12 or 13 December 2026 (D-112). Plan, scope and cut order: `docs/product/nightcap-status.md`.
- Nothing is deployed to the cloud. The game runs from the founder's PC through a tunnel.
- The online paper test is paused (D-111). Do not restart it.
- AI tooling is frozen to break-fixes until the rebuild's first TV session (D-110, D-111).

## Where work lives

| You want | Look here |
| --- | --- |
| What to do next, and whether it is open | GitHub issues, milestone M7. `python scripts/roadmap_status.py --milestone M7` |
| What a task is and why | `docs/roadmap/tasks/AW-NNN-*.md`, found through `docs/roadmap/index.json` |
| Why the work exists | `docs/product/2026-11-15-reset-audit.md` (findings and the issue audit) |
| Decisions | `docs/product/decisions-log.csv` and `docs/decisions/` |
| The stack and what we adopt | `docs/architecture/02-technology-stack.md` section 2.11, ADR-0026 |
| How work flows | `docs/roadmap/operations/working-model.md` |

Work is never left in chat. If you find work, it becomes a roadmap task record and a GitHub issue in the same session (D-119).

## Current work

| Work | Task | State on 2026-11-15 |
| --- | --- | --- |
| Fix the specialist agents in worktree sessions | AW-296 | A separate session is on it |
| Rebuild the index, score the ten questions | AW-297 | Waits on AW-296 |
| Require all checks before merge | AW-298 | Founder action |
| Finish reconciling the tracker | AW-299 | Open |
| Approve spec 0092 for the thin version | Issue #303 | Founder decision |
| Inventory, screen walkthrough, build-versus-adopt | AW-300, AW-301, AW-309 | AW-300 waits on the approval |
| First case | AW-305 | In progress in another session; spoiler rules apply |

## Known issues

- **Specialist agents fail in worktree sessions.** The docs guard takes the repository root from its own file location and refuses the worktree's `docs`. AW-296.
- **Mini-games never start in a real session.** The runtime is tested, but no product code creates, starts or times a run. AW-303.
- **Two sets of screen code exist.** The August rehearsal used `dashboard/`. The mini-game kit is in `nightcap-web/`. AW-300 picks one.
- **The host's written lines have no code that reads them.** AW-291 is the planned reader. Verified 2026-11-15.
- **Only one check is required to merge.** `verify` covers Python lint, types and engine tests. Web tests, TypeScript checks, the secret scan and knowledge-base validation are not required, so read every check on a pull request. AW-298. Verified 2026-11-15.
- **The tracker still partly describes Couch Race.** Labels and comments were applied on 2026-11-15; bodies and milestone criteria are AW-299.
- **Another session holds unsaved work.** Branch `claude/lido-case-and-spec-followups` had an uncommitted edit to spec 0092 and an untracked case folder on 2026-11-15. Do not open the case folder.

## Working facts every session needs

These were learned the hard way and used to live only in one tool's private notes.

- **Sync first.** Run `git fetch origin` and check open pull requests before starting. Parallel sessions duplicated work in July 2026.
- **A closed issue is not proof the work was done.** Check code and merged commits before counting it.
- **An answer from a specialist agent is a lead, not a finding.** Check it against the source that owns the claim.
- **State-machine guards fail silently.** A guarded transition is ignored, not raised. After firing one in a test, check the resulting state. (From an earlier session; re-verify before relying on it.)
- **Push before you link.** A link to a file promises the founder can open it. Push the branch before creating issues or sending links.
- **Plan in one session, implement in another.** The handoff cites a pushed spec or issue and names the exact skill to use.
- **Every phase spec carries a numbered "Your steps" section** for the founder, with click-level instructions.
- **Follow the GDD by default.** Ask only if a newer decision exists, the GDD is silent or ambiguous, or it is worth reconsidering.
- **Story moments are staged sequences of animation and audio** (D-070). Content events carry presentation hints.
- **One case method log per case**, in `docs/design/authoring/case-method-logs/`. There is no universal method.
- **Creative tasks need the founder interview first.** AW-267 and AW-281 both skipped it.
- **On this Windows machine:** hooks declared in agent front matter never run; hooks in `.claude/settings.json` do, and see `agent_type`. A process started with `DETACHED_PROCESS` opens a console window; `CREATE_NO_WINDOW` loses output that is not captured.
- **`team-ai adopt` only backfills front matter.** Agents come from `team-ai init` and `emit`; `team-ai/team-profile.yaml` is the check.

## Deliberate choices: do not "fix" these

| Choice | Owner | Reopen only if |
| --- | --- | --- |
| Rules decide outcomes; AI only voices them | `AGENTS.md`, principle 2 | Never without a founder decision |
| The founder stays unspoiled on the first case | Spec 0092, Q7 | The founder says so |
| Two players is the floor | GDD decision ledger | Play evidence shows it does not work |
| Earned-only Leverage, six investigations per player | Spec 0092, Q4 and Q5 | Session evidence |
| In Nightcap a beat is one round, ending in a story-wrapped mini-game. "Round" is not an engine concept | D-113 | Session evidence |
| Adopt existing tools; build only what is unique | D-114, ADR-0026 | A tool lacks a feature, costs too much, or a strong purpose exists |
| Play data is captured at engine level, in one shape for every game | D-115 | A founder decision |

## Next safe action

Open the task you were given on GitHub. Confirm its prerequisites against main. Write a plan and stop for founder approval, unless the task says it is a break-fix or documentation-only.

## Log

Add one dated entry per merged pull request: what changed, why, which checks covered it, and what is still open.

- **2026-11-15** Reset consolidation. Recorded decisions D-112 to D-119 and ADR-0026; added milestone M7 and tasks AW-296 to AW-317 with matching GitHub issues; added the full target stack (technology stack 2.11), the creator roles (architecture 1.7), the reset audit, the knowledge-base upkeep routine, this file and the task issue template; rewrote the Nightcap status page. Documentation only. Open: everything in "Current work".
- **2026-11-14** Added the dungeon master section and the founder communication style (PR #346). Documentation only.
