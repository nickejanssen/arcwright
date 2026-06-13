# Authentication: Firebase Auth (dashboard) plus API keys (developers) plus short-lived JWTs (game clients)

Date: May 7, 2026
Rationale: Three auth surfaces, three patterns. Firebase Auth handles dashboard human logins (GCP-native, free tier 50K MAU, includes password reset and MFA). API keys for developer backend code calling our API (industry standard). Short-lived JWTs for game clients authenticating to a specific session (issued at session start, scoped, expirable). Saves weeks of building auth flows from scratch.
Section: Cross-cutting
Status: Committed