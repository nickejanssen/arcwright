# Nightcap — Experience, World, and Content Boundaries

**Status:** Current authoritative GDD page.  
**Migration source:** durable creative constraints retained from the former Nightcap Story Bibles, reconciled against the current Decision Ledger, `docs/design/the-host.md`, and `docs/design/nightcap-art-direction.md`.

## Purpose

This page preserves the parts of the former Nightcap Story Bibles that remain compatible with the current game after the gameplay redesign. It does **not** restore superseded Couch Race, Imposter, player-count, scoring, beat-count, accusation-token, or fully-generative-content rules.

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
