# python-statemachine v3.0 StateChart confirmed as arc execution library; StateChart base class (not StateMachine) is correct

Date: May 11, 2026
Rationale: Verified May 11 2026 that v3.0 supports all required arc graph patterns: parallel regions (State.Parallel), compound states (State.Compound), history states, delayed events, conditional transitions via cond=, and invoked sub-machines. The StateChart base class is the SCXML-compliant class introduced in v3.0; StateMachine is the legacy v2.x-compatible class and must not be used. NightcapArcChart implements investigation beat as State.Parallel so private clue distribution and group interrogation run simultaneously.
Section: Cross-cutting
Status: Committed
Tags: roadmap