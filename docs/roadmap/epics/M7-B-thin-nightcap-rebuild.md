---
id: productroadmap.roadmap.epics.m7-b-thin-nightcap-rebuild
namespace: product-roadmap
title: "M7-B: Thin Nightcap Rebuild"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
tags: []
supersedes: []
x-scope-evidence: "D-112, D-113"
---

# M7-B: Thin Nightcap Rebuild

**Milestone:** M7  

## Plain-English Summary

Build the thin, complete version of the Master GDD game: three beats as rounds, each with one or more mini-games, skinned to the story when natural (D-136, D-143), then Last Call, the final theory and the ending.

## Why This Matters

The playable build is the superseded Couch Race design. The founder chose a thin, complete game on the 30-day date (D-112).

## Tasks

- [AW-300: Thin-Version Inventory Of The Current Build](../tasks/AW-300-thin-version-inventory-of-the-current-build.md)
- [AW-301: Walk The Current Build On A TV And Two Phones And Record Every Screen](../tasks/AW-301-walk-the-current-build-on-a-tv-and-two-phones-and-record-every-screen.md)
- [AW-302: Write The Three Combined Rebuild Specs](../tasks/AW-302-write-the-three-combined-rebuild-specs.md)
- [AW-303: Make Mini-Games Start, Time Out And Return To The Story Inside A Session](../tasks/AW-303-make-mini-games-start-time-out-and-return-to-the-story-inside-a-session.md)
- [AW-304: Make Play Records Game-Agnostic](../tasks/AW-304-make-play-records-game-agnostic.md)
- [AW-305: Load The First Case, Pass The Fairness Check, And Report Readiness Without Spoilers](../tasks/AW-305-load-the-first-case-pass-the-fairness-check-and-report-readiness-without-spoilers.md)
- [AW-306: Connect One Story-Writing Tool Through An Importer](../tasks/AW-306-connect-one-story-writing-tool-through-an-importer.md)
- [AW-307: State "Players Want One More Game" As A Goal In The Game Design Document](../tasks/AW-307-state-players-want-one-more-game-as-a-goal-in-the-game-design-document.md)
- [AW-309: Build-Versus-Adopt Review For The Layers Session 1 Needs](../tasks/AW-309-build-versus-adopt-review-for-the-layers-session-1-needs.md)
- [AW-317: Propose A Minimal Read-Only Viewer Of The Story And The Live Session](../tasks/AW-317-propose-a-minimal-read-only-viewer-of-the-story-and-the-live-session.md)
- [AW-319: Try The Detective Agency Framing As A Wrapper On The First Case](../tasks/AW-319-try-the-detective-agency-framing-as-a-wrapper-on-the-first-case.md)
- [AW-320: Friend-Voiced Characters, Recorded Lines First](../tasks/AW-320-friend-voiced-characters-recorded-lines-first.md)
- [AW-322: Prove A Mini-Game Can Be Built And Played On Its Own, And List The Gaps](../tasks/AW-322-prove-a-mini-game-can-be-built-and-played-on-its-own-and-list-the-gaps.md)
- [AW-324: Build The Written Case Format, Its Fairness Check, And What Each Player Holds](../tasks/AW-324-build-the-written-case-format-its-fairness-check-and-what-each-player-holds.md)
- [AW-325: Make Rounds Move By Rule, With A Saved Investigation Budget](../tasks/AW-325-make-rounds-move-by-rule-with-a-saved-investigation-budget.md)
- [AW-326: Build Last Call, The Private Lock, The Theory Check And The Winner Rule](../tasks/AW-326-build-last-call-the-private-lock-the-theory-check-and-the-winner-rule.md)
- [AW-327: Build The Closing Sequence And Prove A Full Game Headless](../tasks/AW-327-build-the-closing-sequence-and-prove-a-full-game-headless.md)
- [AW-328: Give The Mini-Game Winner One Extra Investigation](../tasks/AW-328-give-the-mini-game-winner-one-extra-investigation.md)
- [AW-337: Design And Build The Mini-Game Mechanics For A Playthrough](../tasks/AW-337-give-small-groups-a-mini-game-that-fits.md)
- [AW-338: Tighten Four Round Rules Found In The AW-325 Review](../tasks/AW-338-tighten-four-round-rules-found-in-the-aw-325-review.md)
- [AW-348: Play a minigame live with Nightcap offline](../tasks/AW-348-play-a-minigame-live-with-nightcap-offline.md)
- [AW-349: Prove a browser minigame port and reuse the same package in an Arcwright experience](../tasks/AW-349-prove-browser-minigame-port-and-package-reuse.md)
- [AW-347: Send Mini-Game Package Screens The State They Read, Safely Per Audience](../tasks/AW-347-send-mini-game-renderers-the-state-they-read.md)
- [AW-351: Make The Tell Me Something True Screen And The Engine Agree On The Step And The Spotlight](../tasks/AW-351-make-the-tell-me-something-true-screen-and-engine-agree.md)
- AW-291 (existing task; see `docs/roadmap/index.json`)
- AW-274 (existing task; see `docs/roadmap/index.json`)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- Any open decision is recorded before dependent work starts.

## Dependencies

- Parent milestone: M7
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not bypass the architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.
