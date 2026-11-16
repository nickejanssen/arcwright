# HANDOVER

> Read `AGENTS.md` first, then this file, before touching code. It is the short start-of-session brief for every agent (Claude, Codex, Copilot) and for the founder. If it disagrees with a current source, investigate before acting, then fix this file. Keep it short and link to the owner of each detail.

Last updated: 2026-11-16, against main `bd7f32c`.

## System map

**Arcwright** is the engine: the dungeon master for any game built on it. It runs a human-written story, tracks who knows what, voices characters, paces play, and decides outcomes by rule. Python, in `engine/` and `api/`. See `docs/architecture/01-overview.md`, sections 1.6 and 1.7.

**Nightcap** is the first game on it: a murder mystery on a TV with phones. Its design authority is `docs/gdd/nightcap/`. Its content lives in `nightcap/`. Its screens live in `dashboard/` and `nightcap-web/` (two sets; AW-300 picks one).

Keep them apart. Nothing in `engine/` may name Nightcap or assume a murder mystery.

## Where things stand

- The playable build is the older Couch Race design. The current design (the Master GDD) is not built.
- The first rebuild spec, `docs/specs/0093-engine-spine-for-the-thin-version.md`, was approved on 2026-11-16 (D-124). Its build tasks may write plans; each plan needs the founder's approval before code.
- The second rebuild spec, `docs/specs/0094-endgame-for-the-thin-version.md` (the endgame), was approved on 2026-11-16 (D-125). A mini-game win gives the top-ranked one extra investigation (D-126, AW-328).
- **Working rule from the founder (D-127): move fast, stay open to change, and prefer choices that are cheap to undo.** An approved spec is the current best plan, not a fixed contract. If you find a better way, say so on the task's issue with a recommendation; do not build the worse thing in silence and do not change the plan in silence. Hard rules and plan approval still apply.
- The rebuild plan is `docs/specs/0092-nightcap-gdd-rebuild.md`. Approved for the thin version only on 2026-11-15 (D-123, issue #303). That permits the inventory (AW-300). Building waits on the three combined specs (AW-302), each with its own founder approval.
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
| Rebuild the index, score the ten questions | AW-297 | Scored live: 10 of 10 correct, 7 of 10 citing the owning record. Scores in `docs/conventions/knowledge-base-upkeep.md` |
| Rerun the roadmap questions in a fresh session; close the three citation misses | AW-318 | Open |
| Require all checks before merge | AW-298 | Founder action |
| Finish reconciling the tracker | AW-299 | Open |
| Approve spec 0092 for the thin version | Issue #303 | Done 2026-11-15 (D-123), with the stretch goals as a condition |
| Inventory of the current build | AW-300 | Written 2026-11-15, reviewed by the founder 2026-11-16 (issue #353): `docs/specs/0092-wp0-thin-version-inventory.md`. Still open: a reviewer session's sample check |
| Engine-spine spec | AW-302 | Approved 2026-11-16 (D-124, issue #355): `docs/specs/0093-engine-spine-for-the-thin-version.md` |
| Endgame spec | AW-302 | Approved 2026-11-16 (D-125, issue #355): `docs/specs/0094-endgame-for-the-thin-version.md` |
| Screens spec | AW-302 | Not started. The two interview answers are recorded (D-128, D-129); better after the walkthrough (AW-301) |
| Build tasks under those specs, in order | AW-324, AW-325, AW-303, AW-304, AW-328, AW-326, AW-327 | AW-324 may start: it writes a plan and stops for approval. The rest wait on the task before them. AW-328 is the mini-game reward (D-126) |
| Screen walkthrough on a TV and two phones | AW-301 | Open; needs the founder, Docker, a TV and two phones |
| Build-versus-adopt review | AW-309 | Done 2026-11-15: section 2.11.7 of the technology stack. Session 1 needs no paid plan and no new tool |
| Competitor comparison | AW-316, AW-323 | Done by reading: `docs/product/2026-11-15-competitor-and-prior-art.md`. Playing the two closest is AW-323 (founder) |
| Mini-game on its own | AW-322 | Headless half done; findings in the task file. TV run and the trial mini-game are open |
| First case | AW-305 | In progress in another session; spoiler rules apply |

## Known issues

- **Specialist agents work in worktree sessions again (PR #352), with two catches.** The search index is per checkout and not in git: after pulling, run `python scripts/team_ai_cli.py reindex --root team-ai` in that checkout, or ranked search is stale or missing. A session keeps the agent instructions it loaded when it started, so a change under `.claude/agents/` reaches only sessions started after it merges and the main checkout pulls. Observed 2026-11-15.
- **The roadmap specialist cites summary pages instead of the owning decision.** Three of ten in the live check of 2026-11-15. Its answers were correct; treat the citation as a lead and open the decisions log yourself. AW-318.
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

### Run order from 2026-11-16

Work the list top to bottom. Building starts only at step 7. Whether a step is done is on GitHub: `python scripts/roadmap_status.py --milestone M7`.

| # | Step | Who | Starts when |
| --- | --- | --- | --- |
| 1 | Done 2026-11-16: inventory reviewed; specs 0093 and 0094 approved (D-124, D-125); mini-game reward answered (D-126). Pull request #385 merged 2026-11-16. | Founder, 1 minute | Now |
| 2 | Require the two extra checks before merge (AW-298, #350) | Founder, about 10 minutes | Now |
| 3 | Tell the session on branch `claude/lido-case-and-spec-followups` to commit, push and open a pull request | Founder, 2 minutes | Now |
| 4 | Done 2026-11-16: the two interview questions are answered (D-128: the screens protect "I outsmarted you" first; D-129: the first outside creator is a writer who cannot code) | Founder with any session | Done |
| 5 | Drafted 2026-11-16 (spec 0093). Also send the case-writing session the message under "Owner actions" in that spec | Founder, 2 minutes | Now |
| 6 | Walk the current build on a TV and two phones (AW-301, #354), then write the screens spec (AW-302). The endgame spec is approved (0094, D-125) | Founder starts Docker; one session | After steps 4 and 5 |
| 7 | Build, one task per session, in this order: AW-324, AW-325, then AW-303 beside AW-304, then AW-328, AW-326, AW-327; AW-306, then AW-308 | Build sessions, at most two at once | When the spec that covers the task is approved |
| Any time | AW-318 (fresh session only), AW-299, AW-322's TV half | One session each | Now |

**To start any task in a fresh session, type:** `/implement AW-NNN`. To check a pull request before merging, type `/review-pr`. A session that is not Claude Code is given this instead: "Read `AGENTS.md` and `HANDOVER.md`. Run `python scripts/roadmap_status.py --task AW-NNN`. Do that task as its task file says, and stop at the first founder gate."

**What needs the founder's approval before a build task starts:** its spec, and separately anything on the hard-rule list in `AGENTS.md` (database changes, changes across engine modules, new dependencies, prompts). The inventory found that most of the rebuild is wiring across engine modules, so expect one hard-rule approval per spec.

## Log

Add one dated entry per merged pull request: what changed, why, which checks covered it, and what is still open.

- **2026-11-16** Founder answered the two interview questions. D-128: Nightcap's screens protect the feeling "I outsmarted you" first (private thinking on the phone, a big public reveal on the TV). D-129: Arcwright's first outside creator is a writer who cannot code, authoring a case in the story tool. Both were choices among written options. Still open: the evidence for opening the platform; the screens spec itself. Checks: knowledge-base validators; no code changed.
- **2026-11-16** AW-324 built (spec 0093, Parts A and B; plan approved by the founder the same day). The engine now has a written-case format and a fairness check: `engine/case/authored/` (models, rules A1 to A6, the two reports, loader, and `python -m engine.case.authored <case.json> --arc-id <id>`, which prints the safe summary by default). What a participant holds: `engine/knowledge/holdings.py` (`concepts_held`, `grant_concept`). Session start: `engine/session/case_seating.py` saves each cast character's `knows` list (with each concept's written text, so character generation sees what it says) and gives every non-host participant the opening, when the arc names a `case_file` (new optional field on `ArcDefinition`; the old arcs have none and run as before). No table change, no new dependency, no model call. Choices a plan made that the spec did not state: an accepted answer lists the concepts a player must hold to give it (`needs`); wrong answers are the other nameable cast members, or any other obtainable concept (a player may pick any concept they hold, spec 0094), and an accepted cast answer must be a nameable cast member; the check takes the arc's beat order and the budget (default 6, constant `DEFAULT_CHOICE_BUDGET`; AW-325 moves it into the arc file); a malformed file is refused as `malformed_file`. Checks: see the pull request. Still open: the case-writing session has not confirmed its draft fits the format (a field change is an edit to `models.py` and `rules.py` only); a participant who joins after start misses the opening (AW-325); AW-325 builds phases, the menu and the budget on top of this.

- **2026-11-16** Founder approved spec 0094, the endgame ("Approved Spec 0094 (endgame)."; D-125, issue #355), and answered spec 0093's Q1: a mini-game win gives the top-ranked one extra investigation (D-126). New task AW-328 builds the reward and the standing on each run; AW-326 now waits on it. Founder's working rule recorded as D-127: move fast, stay open to change, prefer choices that are cheap to undo. Not approved: any plan or code. Open: the screens spec; the case-writing session has not confirmed its draft fits the case format. Checks: knowledge-base validators; no code changed.
- **2026-11-16** Founder approved spec 0093, the engine spine ("Approve 0093"; D-124, issue #355). It permits AW-324, AW-325, AW-303 and AW-304 to write plans; AW-324 is first and is unblocked. Not approved: any plan or code, spec 0094, the spec's Q1. Open: the case-writing session has not confirmed its draft fits the case format. Checks: knowledge-base validators; no code changed.
- **2026-11-16** Founder reviewed the inventory ("Inventory reviewed", issue #353). Engine-spine spec drafted, the first of three (AW-302): `docs/specs/0093-engine-spine-for-the-thin-version.md`. Draft, not approved. It covers the written-case format and fairness check, what each player holds, rounds that move by rule, the saved budget of six, mini-game start and return, and play records. It needs no table change and no new dependency; it crosses engine modules. New build tasks AW-324 and AW-325. Found while writing it and added to the inventory as a correction: nothing sends a beat's written scene to the screens; a mini-game run does not record its beat; pausing a session does not pause its run. Checks: knowledge-base validators; no code changed. Not done: the case-writing session has not confirmed its draft fits the format; one open question (what a mini-game win gives). Endgame spec drafted the same day: `docs/specs/0094-endgame-for-the-thin-version.md` (Last Call and the private lock, the rule-based theory check, the winner rule, the closing sequence; no table change, no model call). New build tasks AW-326 and AW-327. It proposes leaving `engine/scoring` untouched instead of lifting the countdown out of it, which changes one inventory row; noted in the inventory.
- **2026-11-15** Founder approved spec 0092 for the thin version, on condition that the stretch goals are included (D-123, issue #303); the detective agency framing (AW-319) was added to the status page as a stretch goal. The approval permits the inventory only. AW-300 inventory written the same evening: `docs/specs/0092-wp0-thin-version-inventory.md`. Main finding: the API reaches only nine engine modules; investigation choices, scoring, the case module and Leverage are built and tested but cannot be reached from a live session, and a live session today moves on only when every player has typed once. The inventory recommends `dashboard/` as the one client. Checks: knowledge-base validators; no code changed. Not done: nothing was run on a TV (AW-301); the founder has not reviewed the inventory.
- **2026-11-15** AW-309 and AW-316, pulled forward at the founder's request. Build-versus-adopt review: section 2.11.7 of `docs/architecture/02-technology-stack.md`; session 1 needs no paid plan and no new tool; two founder decisions added to `docs/product/open-questions-log.csv` (React in the surviving client; Kokoro for sample host lines). Competitor comparison: `docs/product/2026-11-15-competitor-and-prior-art.md`. It corrects the reset audit: Hidden Door sells something close to a story engine for any world, and "rules decide, the AI only voices" is not unique; nobody was found directing a group in one room on a TV with phones. D-122 rules out Ink and Yarn Spinner as the main story tool (no editable graph); the shortlist for AW-306 is Twine, articy:draft X FREE and Arcweave. New task AW-323: the founder plays the two closest neighbours. AW-322 headless half: 93 mini-game tests pass and the standalone preview runs with no case, but it does not run the Python rules and is not playable. Checks: knowledge-base validators only; no code changed. Not done: no product was played; prices not on a maker's page are labelled third party.
- **2026-11-16** Captured four founder ideas as tasks under D-119 (PR #383), with issues #379 to #382: AW-319 (detective agency framing as a wrapper on the first case; tone is comedic with depth), AW-320 (friends' recorded voices, no cloning; last in the session 1 fit order and first to cut), AW-321 (map a book or film into the story map; priority 2, waits for Nightcap to be live) and AW-322 (prove a mini-game can be built and played on its own, list the gaps). AW-314 gained the founder's story notes as material. Founder decision the same day (D-122): story viewing, editing and building are one tool, adopted first (AW-306) and built only if adoption falls short; AW-317 moved to M7-B as a stretch item for the thin version. Documentation only. Checks: `scripts/verify_human_collaboration.py --phase global` passes; no code changed, so engine tests were not run. Still open: none of the four is approved build scope; the founder chooses the framing comparison method and decides each gap from AW-322.
- **2026-11-15** AW-297: rebuilt the search index in the main checkout and ran the ten-question check live from a worktree session (PR #378). Result: 10 of 10 answered and correct, 7 of 10 citing the owning record, the one known conflict flagged. Reading the decisions log works live (D-120). Also added the missing GitHub issue numbers for AW-291 and AW-296 to AW-317 to `docs/roadmap/index.json`, and recorded D-121. Documentation only; no agent or hook file changed. Open: AW-318.
- **2026-11-15** PR #352 (AW-296, AW-297): the knowledge-base guard accepts a worktree of the registered checkout, so specialist agents can search and read `docs/` from worktree sessions. Also: the specialist search considers 64 candidates before namespace filtering, `python scripts/roadmap_status.py --task AW-NNN` gives exact task lookup, and the session-start text tells agents how to resolve a task and record a handoff (D-121). Checks: 197 script tests and ruff passed on `5ab3f2a`, checked independently by the reset session.
- **2026-11-15** Knowledge-base agents can now read `docs/product/decisions-log.csv` (D-120, a deliberate exception to the tooling freeze). `SHARED_SOURCES` in `scripts/hooks/guard_kb_agents.py` allows Read and Grep content for that one file; the CSV carries no namespace, so the guard had refused it, and specialists answered from derived pages. Checks: hook tests pass except `test_registered_hooks_run_from_a_subdirectory`, which also fails on `main` here because `bash` resolves to the WSL launcher. Each of the 14 agent sources in `team-ai/agents/` now says when and how to open the log, and `.claude/agents/team-ai-*.md` were regenerated with the CI `emit` recipe. Still open: the log is not in the ranked index, so agents reach it by Grep on a decision ID; no live specialist read has been run yet.
- **2026-11-15** Reset consolidation. Recorded decisions D-112 to D-119 and ADR-0026; added milestone M7 and tasks AW-296 to AW-317 with matching GitHub issues; added the full target stack (technology stack 2.11), the creator roles (architecture 1.7), the reset audit, the knowledge-base upkeep routine, this file and the task issue template; rewrote the Nightcap status page. Documentation only. Open: everything in "Current work".
- **2026-11-14** Added the dungeon master section and the founder communication style (PR #346). Documentation only.
