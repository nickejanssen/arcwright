// A phone's reads and sends in a round: its menu, a choice, ready, and what it
// holds. Each is one call to an existing engine route with this seat's
// sign-in, the same pattern as controls.ts. The engine decides what is on the
// menu, what a choice costs, what is left and whether a send is allowed; this
// file only carries it. The TV never uses this file.

import { ApiError } from "./lobby";

export interface MenuItem {
  // Needed to send a choice. Never shown.
  opportunityId: string;
  subjectId: string;
  subjectKind: string;
  subjectLabel: string;
  label: string;
  cost: number;
  taken: boolean;
}

export interface Menu {
  open: boolean;
  // The route's number. The screens print it and never work it out.
  remainingBudget: number;
  // In the order the route gave.
  items: MenuItem[];
  // IDs are used only to acknowledge a reward in this browser. Never display.
  rewards: Array<{ grantId: string }>;
}

export interface Choice {
  choiceId: string;
  opportunityId: string;
  content: string;
  cost: number;
  firstTime: boolean;
  replayed: boolean;
  remainingBudget: number;
}

export interface Holding {
  label: string;
  text: string;
  // The subject it was found from; null for what the player held at the start.
  foundFrom: string | null;
  roundTitle: string | null;
  roundNumber: number | null;
}

export interface PlayerApi {
  menu(): Promise<Menu>;
  choose(choiceId: string, opportunityId: string): Promise<Choice>;
  // Marks this player ready for the visit to the phase it saw. Resolves with
  // the phase entry the engine reports, which differs when the round moved on
  // (nothing was saved then).
  ready(phaseEntry: number): Promise<{ phaseEntry: number }>;
  holdings(): Promise<Holding[]>;
}

interface MenuWire {
  open: boolean;
  remaining_budget: number;
  rewards?: Array<{ grant_id: string }>;
  items: Array<{
    opportunity_id: string;
    subject_id: string;
    subject_kind: string;
    subject_label: string;
    label: string;
    cost: number;
    taken: boolean;
  }>;
}

interface ChoiceWire {
  choice_id: string;
  opportunity_id: string;
  content: string;
  cost: number;
  first_time: boolean;
  replayed: boolean;
  remaining_budget: number;
}

interface HoldingsWire {
  concepts: Array<{
    label: string;
    text: string;
    found_from?: string | null;
    found_in_round_title?: string | null;
    found_in_round_number?: number | null;
  }>;
}

export function createPlayerApi(
  sessionId: string,
  getToken: () => Promise<string>,
  fetcher: typeof fetch = fetch,
): PlayerApi {
  const base = `/v1/sessions/${encodeURIComponent(sessionId)}/me`;

  async function call<T>(path: string, body?: unknown): Promise<T> {
    const token = await getToken();
    const res = await fetcher(`${base}${path}`, {
      method: body === undefined ? "GET" : "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        ...(body === undefined ? {} : { "Content-Type": "application/json" }),
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
    if (!res.ok) {
      throw new ApiError(`Request failed: ${res.status}`, res.status);
    }
    return (await res.json()) as T;
  }

  return {
    async menu() {
      const wire = await call<MenuWire>("/menu");
      return {
        open: wire.open,
        remainingBudget: wire.remaining_budget,
        rewards: (wire.rewards ?? []).map((reward) => ({
          grantId: reward.grant_id,
        })),
        items: wire.items.map((i) => ({
          opportunityId: i.opportunity_id,
          subjectId: i.subject_id,
          subjectKind: i.subject_kind,
          subjectLabel: i.subject_label,
          label: i.label,
          cost: i.cost,
          taken: i.taken,
        })),
      };
    },
    async choose(choiceId, opportunityId) {
      const wire = await call<ChoiceWire>("/choices", {
        choice_id: choiceId,
        opportunity_id: opportunityId,
      });
      return {
        choiceId: wire.choice_id,
        opportunityId: wire.opportunity_id,
        content: wire.content,
        cost: wire.cost,
        firstTime: wire.first_time,
        replayed: wire.replayed,
        remainingBudget: wire.remaining_budget,
      };
    },
    async ready(phaseEntry) {
      const wire = await call<{ phase_entry: number }>("/ready", {
        phase_entry: phaseEntry,
      });
      return { phaseEntry: wire.phase_entry };
    },
    async holdings() {
      const wire = await call<HoldingsWire>("/holdings");
      return wire.concepts.map((c) => ({
        label: c.label,
        text: c.text,
        foundFrom: c.found_from ?? null,
        roundTitle: c.found_in_round_title ?? null,
        roundNumber: c.found_in_round_number ?? null,
      }));
    },
  };
}

export interface ChoiceAttempt {
  choiceId: string;
  opportunityId: string;
}

// randomUUID needs a secure page; a phone on a plain http address still has
// getRandomValues, so the ID is built from that when it is missing.
export function newChoiceId(): string {
  const webCrypto = globalThis.crypto;
  if (typeof webCrypto?.randomUUID === "function") {
    return webCrypto.randomUUID();
  }
  const bytes = new Uint8Array(16);
  webCrypto.getRandomValues(bytes);
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join(
    "",
  );
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

// Gives each send of a choice its ID. The ID is made when the player taps and
// kept until the engine answers (even with a refusal), so a send that was lost
// on the way is resent with the same ID and the engine records one effect
// (spec 0093: a repeated ID has one effect). The next tap, on any item, is a
// new choice and gets a new ID.
export function createChoiceTracker(makeId: () => string = newChoiceId) {
  let pending: ChoiceAttempt | null = null;
  return {
    attempt(opportunityId: string): ChoiceAttempt {
      if (pending && pending.opportunityId === opportunityId) return pending;
      pending = { choiceId: makeId(), opportunityId };
      return pending;
    },
    // The engine answered: the next tap starts a new choice.
    answered(): void {
      pending = null;
    },
  };
}
