# Account model: hybrid (mandatory host accounts plus anonymous player join plus optional post-session account creation plus decoupled consent)

Date: May 7, 2026
Rationale: Players join anonymously via QR code (preserves PRD frictionless onboarding requirement, under 30 seconds to seated). Hosts have mandatory accounts (managing settings, eventual billing). Optional post-session account creation for players who want history saved. Consent decoupled: session-level consent at join (lightweight, ToS plus AI processing notice) for anonymous players, full consent at account creation. Three tables: session_participants, accounts, consent_records. Architecture supports monster RPG persistent player identity without rebuild.
Section: Cross-cutting
Status: Committed