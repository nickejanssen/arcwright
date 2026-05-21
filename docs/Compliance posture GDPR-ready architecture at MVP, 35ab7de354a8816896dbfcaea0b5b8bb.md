# Compliance posture: GDPR-ready architecture at MVP, formal certifications deferred to enterprise ask

Date: May 7, 2026
Rationale: GDPR is law in EU regardless of certification: any EU user playing Nightcap triggers compliance. Architecture choices that make GDPR possible are essentially free in chosen stack: encryption at rest (Cloud SQL default), encryption in transit (HTTPS), data minimization (discipline), right to deletion (foreign keys), consent tracking (consent_records table). Formal SOC 2 / ISO 27001 deferred until first enterprise customer specifically asks. HIPAA never (PRD declines clinical healthcare).
Section: Cross-cutting
Status: Committed