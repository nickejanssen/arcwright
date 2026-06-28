Canonical spec and runtime signal name: deflection_tendency.

Current authored declaration key: deflection-tendency.

The key stays hyphenated only because the AW-249 slug validator accepts hyphens and rejects underscores. The authored declaration remains a scalar integer sentinel for validation compatibility.

Runtime map-shaped payload support for {target_player_id: lie_vote_count} remains deferred to AW-251 or later approved schema work. This package records the alias explicitly but does not claim the structured-output question is solved at schema level.

duration_seconds is set to 240 as a playtest calibration estimate for one 45-second input window plus sequential spotlights, reveals, and scoreboard flow across the 4 to 8 player range.

clue_fallback remains present with clue_variant set to reduced because the current schema requires a delayed clue fallback record even for a no-clue social opener. The authored fallback behavior is: advance the session immediately, award no clue, withhold no clue, and use narrator and host copy that makes the social opener flavor-only on failure.
