# Multi-surface routing follows the Jackbox model: platform emits tagged content events, game layer handles routing

Date: May 5, 2026
Rationale: The platform produces content events tagged with context (who the event is for, what triggered it, current session state). The game layer (Nightcap) decides what renders on which surface. The platform never knows what a TV or phone is. Keeps the engine surface-agnostic and generalizable to any delivery format.
Section: Section 2: Strategic Pillars
Status: Committed
Tags: pillars