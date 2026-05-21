# Data architecture extends to locations, objects, decisions tables

Date: May 7, 2026
Rationale: Story is more than dialogue. World state, object interaction, branch points are first-class. Schema additions: locations (id, identity, state, contained_object_ids), objects (id, identity, state, location_id, holder_character_id), decisions (id, context, options_offered, option_chosen, decided_by). Event types extended: object.created, object.moved, object.held, location.changed, environment.changed, decision.offered, decision.made. Nightcap MVP uses subset; monster RPG and couch co-op use all of it. Additive schema, no migration needed when more is used.
Section: Cross-cutting
Status: Committed