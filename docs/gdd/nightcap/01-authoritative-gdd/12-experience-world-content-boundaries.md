# Nightcap — Experience, World, and Content Boundaries

**Status:** Current authoritative GDD page.  
**Migration source:** durable creative constraints retained from the former Nightcap Story Bibles, reconciled against the current Decision Ledger, `docs/design/the-host.md`, and `docs/design/nightcap-art-direction.md`.

## Purpose

This page preserves the Nightcap experience, tone, world, content, and authoring-quality boundaries that remain compatible with the current game. It does **not** restore superseded Couch Race, Imposter, player-count, scoring, beat-count, accusation-token, or fully-generative-content rules.

## DECIDED — World Frame

- A Nightcap case is framed as a **social gathering**. Era, occasion, location, and aesthetic may vary, but the social gathering gives players an immediately legible human context for relationships, secrets, status, and suspicion.
- Nightcap is a **cinematic competitive murder mystery**. Death is the premise; investigation, deduction, competition, social interpretation, and the eventual reveal are the experience.
- The setting and fiction may vary substantially between cases, but variation may not change the canonical murder truth, fairness standard, or player-facing victory rules defined elsewhere in the GDD.

## DECIDED — Tone

- Nightcap is witty, suspenseful, irreverent, darkly comedic, and willing to be strange without making the murder meaningless.
- **The death and the mystery are taken seriously.** Humor comes from character behavior, social dysfunction, specificity, timing, and the absurdity surrounding the situation rather than treating death itself as disposable.
- Tension is investigative and social rather than psychological horror aimed at distressing the player.
- Premium story moments should feel authored, cinematic, specific, and human rather than generic or obviously model-generated.

## DECIDED — Host Authority

- **Vesper is Nightcap's Host.** Her specialist character/voice authority remains `docs/design/the-host.md` unless a later Nightcap GDD decision explicitly reopens it.
- The Nightcap GDD owns what the Host may reveal or imply about gameplay, truth, fairness, and player reasoning. The Host bible owns Vesper's voice, characterization, performance language, and specialist presentation rules where those do not conflict with the GDD.
- Vesper never decides murder truth, solution validity, or the winner. Arcwright resolves those states deterministically; presentation expresses the resolved result.
- Vesper may use playful, behavior-grounded roasts consistent with the GDD's truthful-exaggeration boundary. She may not invent player beliefs or target personal identity.

## DECIDED — Visual Authority

- `docs/design/nightcap-art-direction.md` remains the specialist authority for visual identity, wrappers, moodboards, motion, typography, color, and Vesper's visual staging where it does not conflict with current GDD gameplay.
- The GDD has precedence on gameplay structure. Older art-direction references to a Couch Race, fixed six-beat arc, or former Story Bible are historical implementation context rather than current Nightcap game-design authority.

## DECIDED — Content Territory

Nightcap may include murder, deception, betrayal, greed, jealousy, ambition, desperation, embarrassing or professionally damaging secrets, morally messy relationships, social satire, and dark comedy when they serve the mystery and remain within the experience's entertainment-first tone.

Nightcap does not use:

- graphic violence, gore, or lingering depictions of physical suffering;
- sexual content;
- content targeting real people, living or dead;
- hate speech, slurs, or content that demeans people based on identity;
- harmful content involving minors;
- player-directed psychological horror or content intentionally designed to provoke trauma responses.

The method of death may be discovered and reconstructed as evidence, but presentation should favor implication, forensic/investigative detail, and cinematic reconstruction over graphic depiction.

## DECIDED — Generation Boundary

- The former Story Bible rule that *every specific story element is generated* is **superseded**.
- Current authority is the Decision Ledger's hybrid-content direction plus the Arcwright runtime boundary: deterministic authored truth/state first, generative expression only within that resolved state.
- Nightcap may use authored libraries, generated dressing, generated character expression, and other hybrid techniques when they preserve authorial intent, case fairness, continuity, and premium quality.

## DECIDED — Player-Facing Writing Quality

Paper Test #2 v2.2 reinforced that copy quality and terminology are part of the game model, not cosmetic polish.

Player-facing writing should:

- use plain, stable, contextual language for mechanics and consequences;
- favor specific human detail over generic exposition;
- distinguish system state from fictional observation without sounding like database output;
- give evidence enough texture to reason from without interpreting it for the player;
- avoid abrupt labels, unexplained resource jargon, and inconsistent names for the same concept;
- preserve character voice and scene rhythm while keeping actionable state legible.

Internal implementation names do not automatically become player-facing vocabulary. A term is acceptable on screen only if a first-time player can understand what it represents from the fiction and immediate context.

## DECIDED — Open-Source Skill Use for Authoring and Editorial Work

Arcwright should **actively use high-confidence, high-quality, appropriately licensed open-source skills when they materially improve a writing, continuity, editing, research, or authoring problem**.

This is an Arcwright-native orchestration policy, not an external dependency becoming product authority.

### Selection standard

Prefer upstream skills with strong evidence such as:

- compatible open licensing;
- transparent methodology and readable source;
- concrete examples and documentation;
- meaningful tests, evals, deterministic checks, or explicit review process;
- active maintenance or recent validation;
- clear boundaries around what the skill does and does not decide.

Popularity alone is not validation.

### Current strong references

- **`danjdewhurst/story-skills` (MIT):** strong reference for structured story planning, continuity state, promises/payoffs, timelines, and deterministic continuity-checking patterns.
- **`forjd/better-writing` (MIT):** strong reference for voice calibration, specificity, anti-generic/anti-slop review, factual preservation, and final prose-quality passes.
- **`Calliope-Editor/writing-skills` (MIT):** strong reference for augmentation-only developmental editing, continuity review, line editing, character analysis, scene architecture, and beta-reader-style critique; its reviewed-skill model is useful as a quality benchmark.

These may be installed, adapted, forked, or used as references only when the concrete workflow benefits. Arcwright should avoid importing an upstream story schema wholesale when the Arcwright case graph/knowledge architecture already owns the underlying state more appropriately.

### Authority boundary

Open-source skills may help authors:

- brainstorm;
- structure;
- draft;
- revise;
- critique;
- continuity-check;
- run quality gates;
- identify generic writing or weak scene craft.

They may **not** override:

- the current Nightcap GDD;
- founder-approved authorial intent;
- Arcwright's deterministic case truth;
- the knowledge graph;
- fairness/solvability rules;
- safety boundaries;
- canonical solution validation;
- founder approval gates.

Where an upstream skill has a useful deterministic validator, prefer integrating the principle or adapting it to Arcwright's own authored graph/state rather than creating a second competing truth model.

## Superseded Former-Bible Rules

The following former Story Bible concepts are retained only in archive/history unless separately re-approved:

- Couch Race as the fixed V1 game definition;
- four-human-player V1 floor;
- fixed 2–8 player range;
- fixed six-beat Couch Race as current Nightcap structure;
- human-player killer / Imposter mode as the default current V1 game;
- accusation-token majority-vote win conditions;
- Standing as the current credibility/winner system;
- numerical or subjective case-strength scoring;
- the rule that all Nightcap story content must be fully generative.

When an archived Story Bible, historical ADR, product decision, implementation spec, or roadmap item conflicts with the current GDD, preserve the historical record but use the current GDD for new Nightcap design decisions. Implementation differences must be reconciled explicitly rather than silently treating old behavior as current design.