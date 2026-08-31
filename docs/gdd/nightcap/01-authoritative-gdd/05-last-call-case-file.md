# Nightcap — Last Call & Case File — Structured Reconstruction

**Status:** V1 endgame direction DECIDED; interface details TESTING  
**Type:** GDD system one-pager

## Purpose

Last Call converts open investigation into commitment.

The V1 endgame does **not** ask the player to write an argument, assemble a legal brief, or persuade an AI judge.

The player-facing job is simpler:

> **Lock your theory: who did it, and what actually happened?**

The finale must feel like deduction and payoff, not paperwork, essay-writing, or a lecture.

## Last Call

Nightcap uses a **hybrid trigger**.

Each case has an authored dramatic window in which Last Call belongs narratively, but the case must also satisfy a **minimum fair-solvability condition** before commitment becomes unavoidable.

This does not mean every player must personally possess the solution, encounter every useful clue, or receive extra opportunities because they are behind. It means the case architecture has offered a legitimate route to the correct solution from the same fair starting state. Players remain responsible for what they pursue, notice, believe, ignore, and successfully reconstruct. A player may investigate badly, reach the wrong conclusion, and lose.

Last Call should create pressure. It should not compensate for weak investigation or become a catch-up system. The pressure belongs on **making and committing to the decision**, not on typing speed, menu dexterity, or how quickly someone can operate the interface.

## V1 Interaction — Structured Reconstruction

V1 uses **Structured Reconstruction**.

At Last Call, each player:

1. selects the person they believe committed the murder, and
2. constructs a short causal reconstruction from facts, actions, objects, events, or relationships that are legitimately available in that character's case state.

The interaction should feel closer to assembling a compact theory from meaningful pieces than filling out a questionnaire.

A simple illustrative shape is:

> **Rhea** → **used the staff corridor** → **tampered with the decanter before the toast**

This is an example of interaction grammar, not a universal murder template.

Nightcap should not force every case into fixed categories such as `killer / weapon / motive / room`. Each authored case defines the small set of **essential truths** a player must understand to count as having solved that particular murder.

## Player Knowledge and Available Pieces

The reconstruction interface may offer case concepts the player legitimately encountered, acquired, or heard, including misleading claims, lies, red herrings, incomplete facts, and mistaken testimony. Arcwright retains the distinction between a claim the player heard and a fact/proof state the player actually established.

Nightcap must **not** filter the player's available material down to only the correct or important pieces. Doing so would solve the mystery for them.

Arcwright automatically tracks what the player encountered, heard, acquired, verified, or owns so eligibility does not become bookkeeping. It may not tell the player which piece matters, which combination is correct, or what conclusion to draw.

## Deterministic Resolution

A player's theory is resolved against the authored case/solution graph.

The model does **not** judge whether prose sounds persuasive. No language model, free-text classifier, or subjective argument score determines the winner.

The authored case defines:

- the canonical culprit,
- the canonical causal truth,
- the essential truths required for a solve,
- multiple legitimate facts or routes that may establish the same essential truth where appropriate.

A reconstruction either satisfies the authored solve condition or it does not.

## No Numerical Case Strength for the Winner

V1 does **not** use a numerical Case Strength score to choose between competing theories.

The primary competitive distinction is:

> **Solved the murder / did not solve the murder.**

If exactly one player solves it, that player wins.

If multiple players solve it, they are tied on the murder and the already-established competitive tie-break direction applies: minigame performance before any speed-based measure.

If nobody solves it, **no player is crowned the murder winner**. The murderer/case beats the table. Nightcap may still recognize who came close in the Postmortem, but it does not manufacture a victory.

## Commitment and Reveal

Final theories lock **privately and simultaneously**.

After lock, a player cannot revise their theory because another player's accusation sounded stronger.

Once all commitments are locked, Nightcap theatrically reveals **only each player's accused culprit** before revealing the canonical murder. Players do not give speeches or argue their cases to the room.

## Interaction Constraints

- Keep the reconstruction short: normally culprit + a small number of essential causal pieces.
- Favor tapping, arranging, connecting, or selecting meaningful discovered concepts over typing.
- Free text should be optional or presentation-only unless a specific authored interaction truly benefits from it.
- Do not reveal correctness until commitment is complete.
- Do not reward brute-force guessing through incremental correctness feedback.
- Do not make interface speed a competitive skill.

## PARKED Fallback and Augmentations

### Simpler fallback — Culprit + Decisive Facts

**PARKED.** If representative testing shows Structured Reconstruction is too fiddly, too slow, or too difficult to operate on a phone, test a simpler fallback:

- choose the culprit,
- choose a very small number of decisive facts from legitimately learned information,
- commit.

This is a fallback, not the current V1 default.

### Cinematic confrontation / detective proclamation

**PARKED augmentation.** After deterministic resolution, Nightcap may dramatize the correct reconstruction as a short mystery-movie-style gathering, confrontation, or proclamation. The performance can use Arcwright to express the already-resolved result cinematically and humorously.

The confrontation does **not** decide correctness. The player already did the deduction; the game performs the payoff.

### Witness/interview contradiction mechanic

**PARKED.** Ace-Attorney-like witness confrontation or contradiction mechanics may be reconsidered only if representative feedback indicates interviews/interrogations need improvement. Do not add this mechanic merely because it is interesting in isolation.

## Handoff

**THINK / HUNT → LAST CALL → CASE FILE (STRUCTURED RECONSTRUCTION) → SIMULTANEOUS LOCK → CULPRIT REVEAL → THE TRUTH → THE VERDICT → THE POSTMORTEM**

## TESTING

- exact Last Call trigger thresholds,
- Structured Reconstruction interaction grammar,
- number of essential truths per case,
- mobile speed/friction,
- whether available theory pieces preserve autonomy without becoming confusing,
- handling of multiple equivalent valid reconstructions,
- endgame duration and pacing.

## Fairness Checks

> **Before Last Call became unavoidable, did the case give every player a legitimate opportunity to reach the correct solution, without guaranteeing that they used that opportunity well?**

> **Can multiple reasonable investigation routes reach the essential truths without one required designer-favorite clue becoming a hidden single point of failure?**

> **When a player loses, can they understand what part of their reconstruction was factually wrong without Nightcap having to defend a subjective score?**
