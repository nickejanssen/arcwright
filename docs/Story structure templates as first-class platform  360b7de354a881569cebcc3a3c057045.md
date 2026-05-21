# Story structure templates as first-class platform objects: the current arc schema includes arc_structure as a metadata string field but the engine does not use it to scaffold beat definitions or pacing defaults. Should story structure templates (Dan Harmon, Hero's Journey, etc.) be first-class platform objects that pre-populate beat scaffolding for arc authors, or is this purely an authoring-layer concern deferred to the no-code arc builder in Horizon 2? Resolution must clarify whether arc_structure remains decorative metadata at MVP or whether the engine needs to understand it functionally.

Category: Product
Date Opened: May 14, 2026
Date Resolved: May 15, 2026
Priority: High
Resolution Notes: Resolved in Chat 7 Story Bible. Story Circle is now a first-class platform object. arc_structure: "story_circle" scaffolds 8 pre-populated beat containers with story_circle_step, structural_function, dramatic_purpose, emotional_target, information_goal, tension_target, and character_emphasis fields. The engine uses structural intent as a functional input for generation context, pacing calibration, and ensemble coordination. arc_structure is no longer decorative metadata. arc_structure value changed from dan_harmon to story_circle. Technical Architecture updated to v1.2 with full schema changes. Story structure templates are first-class platform objects at MVP, not deferred to Horizon 2.
Status: Resolved
Where Resolved: Chat 7 Story Bible | 07-Technical-Architecture-v1.2 | 02-Decisions-Log