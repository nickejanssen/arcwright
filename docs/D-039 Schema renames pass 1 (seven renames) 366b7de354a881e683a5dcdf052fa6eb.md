# D-039 Schema renames pass 1 (seven renames)

Date: May 19, 2026
Rationale: Seven renames confirmed: bonded_creatures to bonded_entities; home_base_location to player_anchor_location; career_path to player_role_arc; active_party to current_companion_entities; agency_vs_fate event tag to event_authorship with initial enum {player, world}; witnessing_creature_ids to witness_entity_ids; pact_term to current_intent, with historical wants stored separately in intent_history. Renames propagate through API surface, TypeScript SDK type definitions, dashboard UI labels, documentation, example code, Monster RPG Bible, and Nightcap Bible.
Section: Cross-cutting
Status: Committed