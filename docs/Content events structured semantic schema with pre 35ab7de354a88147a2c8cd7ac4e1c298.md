# Content events: structured semantic schema with presentation hints

Date: May 7, 2026
Rationale: Each content event includes: event_type, actor_id, target, payload, presentation_hints (emotion, urgency, voice style, animation hint, lighting hint), target_audience, target_surface. Semantic events not pixel commands. Engine-friendly for downstream SDK consumption: TypeScript web SDK uses subset (text rendering); future Unity SDK uses full schema mapping presentation_hints to Animator parameters, AudioMixer settings, lighting cues. Same payload, different consumers. Engine never knows about display surfaces.
Section: Cross-cutting
Status: Committed