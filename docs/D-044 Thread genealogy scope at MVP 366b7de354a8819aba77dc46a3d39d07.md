# D-044 Thread genealogy scope at MVP

Date: May 19, 2026
Rationale: The parent_thread_id field exists on the thread schema from day one, nullable, defaulting to null. Genealogy traversal logic using parent_thread_id for narrative coherence over long saves ships at Monster RPG H2. Nightcap is single-session and does not exercise thread ancestry.
Section: Cross-cutting
Status: Committed