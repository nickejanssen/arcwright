"""Narrator generation module.

Exposes ``generate_narrator_bridge`` for the session resume flow.
Architecture: docs/architecture/05-session-persistence.md §5.3-5.4.
"""

from engine.narrator.bridge import generate_narrator_bridge

__all__ = ["generate_narrator_bridge"]
