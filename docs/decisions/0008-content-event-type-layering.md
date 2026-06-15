# Status

**Accepted** (2026-06-14)

---

# Context

`docs/architecture/08-event-system.md` S8.2 defines the `ContentEvent` schema with a single field, `event_type: ContentEventType`. The architecture text references `clue_delivery` and `clue_acknowledged` in the S8.5 Nightcap example without enumerating the full set, leaving the implementation of `ContentEventType` as an open design point.

AW-215 (`docs/specs/0038-aw-215-contentevent-model-and-in-memory-bus.md`) is the task that materializes the schema and the in-memory bus. While planning that task we surfaced a tension between two of the platform's stated principles:

- **Surface agnosticism and platform identity.** `AGENTS.md` and the Arcwright Strategy doc commit the engine to be a *platform*, not a Nightcap-specific runtime. The platform must serve Nightcap, Monster RPG, future Arcwright Studios titles, and eventual third-party developers without amendment per game.
- **Telemetry, safety, and routing need vocabulary.** A pure open-string event type forfeits the closed vocabulary that the safety pipeline, the multi-surface fanout, and the eventual telemetry roll-ups all rely on for correctness and cross-game comparability.

Alternatives considered:

- **Closed enum tied to Nightcap.** Defines a fixed list such as `clue_delivery`, `clue_acknowledged`, `beat_transition`, `narrator_line`, `reveal`, `victim_announcement`. Gives type safety today but pollutes the platform layer with one game's vocabulary. Every future game (Monster RPG, third-party studio titles) would either bend its events into Nightcap's words or force a PR against the platform repo to add its own. Rejected: incompatible with Arcwright's platform identity.
- **Pure open string `event_type: str`.** Maximum flexibility, zero ceremony. Lets every game define its own vocabulary. Rejected: the platform safety pipeline, audience-target router, and cross-game telemetry all need a closed, known vocabulary to operate against. Typos silently break clients.
- **Closed enum + open-extension hatch (single field with both behaviors).** Compromise that fuzzes intent: two ways to express the same thing in one field. Rejected: harder to reason about for engine and downstream consumers alike.

Stripe's `event.type` (closed at the top level — `payment_intent.succeeded` — opaque structure below) and Jackbox's platform protocol (closed verbs, game-defined payloads) both solve this tension by layering. The same approach fits Arcwright.

---

# Decision

We split the single `event_type` field in `ContentEvent` into two fields:

```python
class EventCategory(str, Enum):
    NARRATIVE          = "narrative"           # narrator lines, environmental description
    CHARACTER_DIALOGUE = "character_dialogue"  # in-character speech, AI or human
    PRIVATE_DELIVERY   = "private_delivery"    # clue, item, fact delivered to one player
    ACKNOWLEDGEMENT    = "acknowledgement"     # public-safe receipt of a private event
    STATE_TRANSITION   = "state_transition"    # beat changes, phase changes, reveals
    INPUT_REQUEST      = "input_request"       # prompt to player or host for input
    SYSTEM             = "system"              # session lifecycle, errors, replay markers

class ContentEvent(BaseModel):
    ...
    category:   EventCategory   # closed platform enum; owned by Arcwright
    event_type: str             # open string; owned by the game/arc
    ...
```

`EventCategory` is the closed, platform-owned vocabulary. The seven values cover Nightcap's eight beats today and generalize to the known patterns of Monster RPG and a hypothetical third-party murder mystery, escape room, or social-deduction title. Extending the enum is a deliberate platform-level decision documented as an amendment to this ADR or a successor ADR.

`event_type` is the open, game-owned vocabulary. Nightcap may emit `event_type="clue_delivery"` under `category=PRIVATE_DELIVERY`; Monster RPG may emit `event_type="monster_spawn"` under `category=STATE_TRANSITION`; a third-party studio chooses its own strings. The platform performs no validation on `event_type` beyond requiring a non-empty string.

The platform's safety pipeline, audience-target router, telemetry roll-ups, and SSE fan-out all dispatch on `category`. Game-layer clients and game-specific telemetry can dispatch on `event_type` for finer-grained behavior.

We update `docs/architecture/08-event-system.md` S8.2 to reflect the layered schema, and we implement this design in AW-215.

---

# Consequences

## Positive consequences

- **Platform identity preserved.** Arcwright remains a platform, not a Nightcap-specific runtime. Monster RPG, future Arcwright Studios titles, and third-party developers can build on the platform without amending the event vocabulary.
- **Type safety where it matters.** Safety, routing, and cross-game telemetry operate against a closed, known vocabulary. Category typos are caught at write time.
- **Telemetry stays comparable across games.** "How many private deliveries fired this session?" answers consistently across any arc; per-game metrics still available via `event_type`.
- **No platform PR required to add a game-specific event type.** Game and arc developers move at their own pace.
- **Plain-English naming for the closed vocabulary.** `PRIVATE_DELIVERY` and `ACKNOWLEDGEMENT` describe what the platform must do with the event (route privately; permit a public receipt), not what the game means by it. This is the level of abstraction the platform layer should know.

## Negative consequences

- **Two fields where the architecture doc previously implied one.** Slightly more verbose schema; consumers must read both to understand an event fully.
- **Game implementers must decide on a `category` for each game-specific `event_type`.** This is one extra step at arc-authoring time, mitigated by documenting the seven categories with examples in the architecture doc and the SDK.
- **The seven starter categories are a judgment call.** The set covers what we know about Nightcap and Monster RPG. A future arc may surface a need for an eighth category; that is a platform-level decision and an ADR amendment, not an arc-author decision.

## Trade-offs

We chose plain-English platform vocabulary and game-owned subtypes over either a Nightcap-shaped enum or a structureless string. We accepted a two-field schema instead of one, and the modest ergonomic cost of asking arc authors to classify their event types into one of seven platform categories.

---

# References

- Architecture: [`docs/architecture/08-event-system.md`](../architecture/08-event-system.md) S8.2 (updated as part of AW-215)
- Spec: [`docs/specs/0038-aw-215-contentevent-model-and-in-memory-bus.md`](../specs/0038-aw-215-contentevent-model-and-in-memory-bus.md)
- Roadmap epic: [`docs/roadmap/epics/M3-A-content-event-system.md`](../roadmap/epics/M3-A-content-event-system.md)
- GitHub issues: Epic [#40](https://github.com/nickejanssen/arcwright/issues/40), task [#68](https://github.com/nickejanssen/arcwright/issues/68)
- Product principles in `AGENTS.md`: surface agnosticism, human arc primacy, configurable composition, provider-agnostic model routing
- Product decisions log: D-32 (Jackbox-style multi-surface routing), D-45 (content events as structured semantic schema with presentation hints)
