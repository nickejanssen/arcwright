# 00-How-This-Workspace-Works

**Version:** 1.0

**Last Updated:** May 1, 2026

**Audience:** Founder, future co-founders, future hires, advisors, counsel

**Purpose:** Explain how this workspace is organized, what each artifact is for, and the conventions for keeping it useful over time.

---

## Why this workspace exists

This Notion workspace is the **source of truth** for all foundational documents for Adaptive Experiences Co. Strategy, decisions, open questions, naming, technical architecture, story bibles, and competitive landscape all live here.

Claude Project chats are where strategic conversations happen and artifacts get drafted and refined. Notion is where the canonical, editable, queryable, version-controlled versions live. Project knowledge in [Claude.ai](http://Claude.ai) is a context-loading mechanism: it holds copies of these artifacts so Claude can reference them in future chats, but the versions in Project knowledge are downstream of Notion.

The flow is always: **draft and refine in Claude chats → canonical version in Notion → export and re-upload to Project knowledge with version increment.**

---

## What each artifact is for

### 00-How-This-Workspace-Works (this document)

The usage guide. Explains conventions and processes. Read this first if you're new to the workspace.

### 01-Strategy-Document

The master strategy. Nine sections covering company overview, strategic pillars, three-horizon roadmap, vertical strategy, capital strategy, team and hiring philosophy, proof signal framework, tool stack, and references. This is the document you re-read when making any significant decision, to check whether the decision is consistent with stated strategy.

### 02-Decisions-Log (database)

Append-only record of significant decisions. Every time a meaningful decision is made (about strategy, hiring, capital, product scope, naming, etc.), it gets a new entry. Reversals are logged as new entries, not edits to old ones. This is the audit trail.

Properties: Decision (title), Date, Rationale, Status (Committed / Tentative / Reversed / Watchpoint), Section (which Strategy Doc section the decision relates to), Tags.

### 03-Open-Questions-Log (database)

Questions that need to be resolved, where they will be resolved, and current status. When a question is resolved, the entry stays in the log with status changed to Resolved and resolution notes added. Do not delete resolved questions; the audit trail matters.

Properties: Question (title), Status (Open / In Progress / Resolved / Parked / Blocked), Where Resolved, Resolution Notes, Date Opened, Date Resolved, Priority (Critical / High / Medium / Low), Category.

### 04 through 11 (planned)

Naming and Brand, Competitive Landscape, Technical Architecture, Story Bibles, Enterprise Sales Playbook, IP Protection Tracker, Monthly Review Log. Created as needed, not all at once.

---

## Core conventions

### Version control

Every artifact has a version number in the title (e.g., `01-Strategy-Document-v1`). When the artifact is meaningfully updated, increment the version. Use semantic versioning logic:

- **Major version (v1 → v2):** Significant restructuring, large additions, or changes that materially shift the meaning of the document.
- **Minor version (v1.0 → v1.1):** Updates, corrections, additions of new entries, or refinements that don't change the document's structure.
- **Patch (v1.0 → v1.0.1):** Typos, formatting fixes, link corrections.

When a major version increments, archive the old version (rename the page to include `-archived`) before creating the new one. Old versions are reference material, not active documents.

### The append-only rule for Decisions Log

Do not edit existing decision entries. If a decision is reversed, add a new entry on the date of reversal that explains the reversal and references the original entry. This preserves the audit trail and lets you see how thinking evolved.

### The do-not-delete rule for Open Questions Log

When a question is resolved, change Status to Resolved and add Resolution Notes. Do not delete the entry. Resolved questions are evidence of what got worked through.

### When to add a Decisions Log entry

Add an entry when any of the following happens:

- A choice is made that constrains future options (vertical, capital structure, hiring, tooling).
- A change is made to anything in the Strategy Document.
- A reversal of a previously logged decision.
- A watchpoint is identified (decision made, but flagged for monitoring).

Do not add an entry for routine task-level choices. The bar is: would a future-me or a future-co-founder need to know this decision was made deliberately?

### When to add an Open Questions Log entry

Add an entry when any of the following happens:

- A question is raised that needs resolution but cannot be resolved now.
- A decision is deferred with a known trigger (e.g., "resolve when proof signals hit").
- A research, legal, or external dependency is identified.
- An idea worth capturing for later (parked status).

### Watchpoints

A watchpoint is a decision that has been committed to but flagged for monitoring because it carries risk or could need course-correction. Watchpoints get the orange Watchpoint status in the Decisions Log. They are reviewed in monthly review. If a watchpoint triggers an actual change, that change gets logged as a new entry.

Current watchpoints (as of v1):

- 6-month floor for Horizon 1 is aggressive while building part-time. Treat as ambitious-stretch goal, not commitment.
- First co-founder/hire role decision deferred. Must be evaluated deliberately before talking to candidates, not while talking to them.
- Horizon 1 hiring rule is case-by-case (no hard contractor-only mandate). Equity-bearing collaborators require deliberate written justification, vesting schedule, and reverse-vesting clause.

---

## Working with Claude

### What gets drafted in Claude chats

Strategic conversations, planning, analysis, story development, technical design, and artifact updates. All foundational artifacts are produced and refined in Claude Project chats before being canonicalized in Notion.

### What gets written directly in Notion

Minor edits, formatting fixes, link corrections, status updates on existing log entries, and any quick captures that don't need conversation to surface. Anything substantive should still go through a Claude chat first to get the thinking right.

### Direct connector writes

Claude has a Notion connector that can read and write to this workspace directly. When updates are made in a chat, Claude can write them directly to the relevant page or database instead of producing markdown blocks for manual paste. This is the preferred workflow.

### Project knowledge sync

After major version increments, export the updated artifact from Notion (page menu → Export → Markdown) and upload to Project knowledge in [Claude.ai](http://Claude.ai). This keeps Project knowledge in sync with Notion. Project knowledge is downstream of Notion, not the other way around.

For minor edits made directly in Notion, sync to Project knowledge is not urgent. Sync at most monthly, or when entering a new chat where the updated context matters.

### Claude operating instructions

The Claude-facing operating instructions for this project live in Project knowledge as `00-Project-Operating-Instructions`. That document tells Claude how to behave: tone, scope of help, what to push back on, copyright discipline, IP flagging, artifact output conventions. It is the Claude-facing complement to this Notion-facing usage guide.

---

## Monthly review process

Monthly review is the recurring discipline that keeps the system honest. It happens once per month, ideally on a fixed date.

### What gets reviewed

1. **Proof signal scorecard.** Status of each of the six signals (3 product + 3 business). Are we hitting them? What's the evidence? What's blocking the ones we're not hitting?
2. **Watchpoints.** Each watchpoint in the Decisions Log gets a status check. Has the situation changed? Should the watchpoint be cleared, escalated, or course-corrected?
3. **Scope drift check.** Are platform and games both getting protected time? Is one starving the other? Strategic Pillar 3.
4. **Open questions triage.** Any open questions stale or blocked? Any new ones surfacing that should be added?
5. **Decisions made since last review.** Quick scan of Decisions Log entries from the past month. Anything tentative that should now be committed? Anything that needs revisiting?
6. **Calendar vs. proof signals.** Are we ahead of schedule, on schedule, behind schedule, or off-track? Is the calendar drift a signal that the part-time pace is the bottleneck, or that the product needs more iteration, or that the market is different than hypothesized?

### Where it gets logged

Monthly Review Log (Document 11, not yet created). Each review is a new entry with date, scorecard snapshot, watchpoint status, scope drift assessment, and any decisions or questions that emerged from the review.

---

## Operating principles for the system itself

### Document the conventions, not just the content

The artifacts (strategy, decisions, questions) are the content. The conventions (append-only, version increments, monthly review, watchpoints) are how the content stays useful. Skipping the conventions makes the artifacts decay. This document exists because conventions need to be documented as deliberately as the artifacts themselves.

### Future-you is not as smart as present-you about present-you's reasoning

The rationale field in the Decisions Log is for future-you. Write it as if a future co-founder is reading it cold and trying to understand why this decision was made. Don't write "because of the reasons we discussed." Write the reasons.

### When in doubt, log it

The cost of an extra Decisions Log entry is a few minutes. The cost of a missing one is months of confusion later about why something is the way it is. Err on the side of logging more.

### When the workspace gets cluttered, restructure

If the workspace becomes hard to navigate (too many pages, unclear hierarchy, archived versions cluttering the sidebar), restructure deliberately. Move archives into an Archive folder. Consolidate related documents. The workspace is a tool, not a museum.

---

## Onboarding a new collaborator

If a future co-founder, hire, advisor, or contractor needs access to this workspace, give them the following in this order:

1. **This document** (00-How-This-Workspace-Works). They need to know how the system works before they can use it.
2. **01-Strategy-Document.** They need to know what the company is and what it's not.
3. **02-Decisions-Log.** They need to see the decisions that have been made and the reasoning, so they don't relitigate settled ground.
4. **03-Open-Questions-Log.** They need to see what's unresolved, so they know what's open for discussion.
5. **Other documents as relevant to their role.**

Do not give a new collaborator write access to the Decisions Log or Strategy Document until they understand the conventions in this guide.

---

## What this workspace is not

This workspace is not:

- A task tracker (use Linear or GitHub Projects when build starts).
- A code repository (use GitHub).
- A CRM (use HubSpot or equivalent when enterprise outreach begins).
- A document collaboration platform for external parties (export to Google Docs or PDF for sharing with counsel, investors, or partners).
- A wiki or knowledge base for the product itself (separate documentation site when public-facing).

Keep this workspace focused on foundational strategy and decision-making. Other functions belong in other tools.

---

## Versioning of this guide

This guide is itself an artifact and follows the same conventions. Updates increment the version number. Major restructurings get a new version with the old archived. The current version always lives at the top of the workspace.