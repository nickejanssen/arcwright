# D-036 TypeScript clarification (reaffirmation and extension of D-057)

Date: May 19, 2026
Rationale: TypeScript is correct for the web SDK and dashboard frontend. Engine SDKs (Unity in C#, Unreal in C++ with Blueprints integration, Godot in GDScript or C#, native mobile in Swift and Kotlin if pursued) require their native languages and are separate engineering efforts wrapping the same REST API. Backend Python remains correct for the AI-heavy engine. The phrase 'the SDK' is plural; each engine SDK is its own real piece of work.
Section: Section 8: Tool Stack
Status: Committed