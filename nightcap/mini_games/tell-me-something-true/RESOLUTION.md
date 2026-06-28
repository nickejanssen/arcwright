deflection_tendency is declared as scalar integer in the authoring schema for AW-249 validation compatibility.

Runtime emits a map-shaped {target_player_id: lie_vote_count} payload in event data per AW-251.

Resolved under AW-262. Closes the open question in docs/specs/0061-aw-258-tell-me-something-true.md.

duration_seconds is set to 180 as the schema-valid estimate for one 45-second input window plus sequential spotlights, reveals, and scoreboard flow.

clue_fallback remains present with clue_variant set to reduced because the current schema requires a delayed clue fallback record even for a no-clue social opener.
