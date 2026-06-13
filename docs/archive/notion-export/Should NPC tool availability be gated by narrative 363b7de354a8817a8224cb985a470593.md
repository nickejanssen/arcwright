# Should NPC tool availability be gated by narrative state rather than relying on prompt engineering alone?

Category: Product
Date Opened: May 17, 2026
Priority: High
Status: Open

Emergence World gates tool availability by agent location; agents cannot use tools they are not physically near. The Arcwright equivalent is narrative-state-gating: an NPC who has not been confronted cannot confess; a player who has not found a clue cannot pursue that lead. Enforcing story logic through tool availability rules is more reliable and auditable than prompt engineering alone. Deciding this early has significant engine architecture implications. Needs a mapping of which NPC actions are gated by which story states before any engine code is written.