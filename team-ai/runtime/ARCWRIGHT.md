# Arcwright knowledge CLI runtime

This is an Arcwright-maintained compatibility snapshot of `nickejanssen/team-ai`
version 0.6.6, commit `dde94c5b9aafa3e85fdcd7990b096497e57a235d`. It is
included so normal operation and CI do not require a second checkout. The
upstream Apache-2.0 license and notice are in `LICENSE` and `NOTICE`.

The complete tracked upstream tree was retained initially to preserve the
existing command interface and tests. Its nested `.github/` and governance
files are historical snapshot material; Arcwright's root configuration governs
this repository. The upstream `prepare` package script and `lefthook` development dependency
were removed because they install Git hooks into the enclosing Arcwright
repository. No automatic
sync from upstream is configured. Future changes are reviewed and maintained
here, and unnecessary parts can be retired after their interfaces are audited.

Build with Node 22 or later using `npm ci` and `npm run build`. The generated
`dist/` and `node_modules/` are local build products and are not committed.
The local index is derived data, rebuilt separately in each checkout.
