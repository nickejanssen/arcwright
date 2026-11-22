// Fixture data and a fake engine for the round screens (AW-332). The fake
// engine answers the routes the screens call (room, menu, choices, ready,
// holdings) and does its own sums; the screens under test do none, so every
// number a screen shows can be compared with the engine's.

import type { LobbyState } from "../../src/api/lobby.js";
import type { RoundState } from "../../src/api/round.js";

// Internal names that must never be drawn on any screen.
export const INTERNAL_IDS = [
  "beat_internal_1",
  "game-uuid-1111",
  "participant-uuid-2222",
  "participant-uuid-3333",
  "participant-uuid-4444",
  "opp_internal_1",
  "opp_internal_2",
  "opp_internal_3",
  "opp_internal_4",
  "subj_internal_A",
  "subj_internal_B",
  "subj_internal_C",
  "concept_internal_1",
  "concept_internal_2",
  "concept_internal_3",
  "concept_internal_opening",
  "grant_internal_1",
  "grant_internal_2",
  "run_internal_1",
  "run_internal_2",
  "character-internal",
  "choice-id-token",
] as const;

export const ME = "participant-uuid-2222";

export function lobby(over: Partial<LobbyState> = {}): LobbyState {
  return {
    session_id: "game-uuid-1111",
    join_code: "K7QP",
    status: "active",
    current_beat_id: "beat_internal_1",
    is_terminal: false,
    min_players: 2,
    player_count: 3,
    players: [],
    ...over,
  };
}

export function round(over: Partial<RoundState> = {}): RoundState {
  return {
    sessionStatus: "active",
    beatName: "A Quiet Evening",
    phase: "scene",
    phaseEntry: 7,
    status: "running",
    secondsLeft: 102,
    readyCount: 1,
    playerCount: 3,
    players: [
      { participantId: ME, name: "Jordan", ready: false },
      { participantId: "participant-uuid-3333", name: "Avery", ready: true },
      { participantId: "participant-uuid-4444", name: null, ready: false },
    ],
    lines: [],
    ...over,
  };
}

export interface FixtureItem {
  opportunity_id: string;
  subject_id: string;
  subject_kind: string;
  subject_label: string;
  label: string;
  cost: number;
  taken: boolean;
  content: string;
  gives: string[];
}

export const ITEMS: FixtureItem[] = [
  {
    opportunity_id: "opp_internal_1",
    subject_id: "subj_internal_A",
    subject_kind: "person",
    subject_label: "The Butler",
    label: "Ask about the evening",
    cost: 1,
    taken: false,
    content: "He says he was in the pantry all night.",
    gives: ["concept_internal_1"],
  },
  {
    opportunity_id: "opp_internal_2",
    subject_id: "subj_internal_A",
    subject_kind: "person",
    subject_label: "The Butler",
    label: "Ask about the keys",
    cost: 1,
    taken: true,
    content: "He keeps the spare keys on a hook by the door.",
    gives: ["concept_internal_2"],
  },
  {
    opportunity_id: "opp_internal_3",
    subject_id: "subj_internal_B",
    subject_kind: "place",
    subject_label: "The Study",
    label: "Search the desk",
    cost: 1,
    taken: false,
    content: "A torn page is wedged behind the drawer.",
    gives: ["concept_internal_3"],
  },
  {
    opportunity_id: "opp_internal_4",
    subject_id: "subj_internal_C",
    subject_kind: "record",
    subject_label: "The Ledger",
    label: "Read the last page",
    cost: 2,
    taken: false,
    content: "The final entry is dated the day before.",
    gives: [],
  },
];

export interface FixtureHolding {
  concept_id: string;
  label: string;
  text: string;
  found_from: string | null;
  found_in_beat: string | null;
  found_in_round_title: string | null;
  found_in_round_number: number | null;
}

export const OPENING: FixtureHolding = {
  concept_id: "concept_internal_opening",
  label: "Your cover story",
  text: "You are the host's old friend, visiting for the week.",
  found_from: null,
  found_in_beat: null,
  found_in_round_title: null,
  found_in_round_number: null,
};

export interface FakeCall {
  method: string;
  path: string;
  body: Record<string, unknown> | null;
  authorization: string | null;
}

export interface FakeEngine {
  fetch: typeof fetch;
  calls: FakeCall[];
  // Choice effects recorded by choice_id; a repeated ID adds none.
  effects: string[];
  budget: number;
  open: boolean;
  items: FixtureItem[];
  holdings: FixtureHolding[];
  readyEntries: number[];
  // The next choices call is processed by the engine but its answer is lost.
  dropAnswerOnce: boolean;
  // The engine refuses the next choices call.
  refuseNextChoice: boolean;
  // A proxy answers the next choices call with a 503; the engine never sees it.
  unavailableNextChoice: boolean;
  // Each queued gate holds one menu read (the body is fixed when the read is
  // made, as a slow network would deliver it) until the gate opens.
  menuGates: Array<Promise<void>>;
  // How many of the next menu reads fail, as a dropped connection would.
  dropMenus: number;
  // The next choices call is processed but its answer waits for this promise.
  holdNextChoice: Promise<void> | null;
  // The phase entry the engine reports from ready.
  entryNow: number;
  rewards: Array<{
    grant_id: string;
    run_id: string;
    beat_id: string;
    amount: number;
    kind: string;
  }>;
}

export function fakeEngine(
  options: {
    budget?: number;
    items?: FixtureItem[];
    holdings?: FixtureHolding[];
  } = {},
): FakeEngine {
  const engine: FakeEngine = {
    calls: [],
    effects: [],
    budget: options.budget ?? 4,
    open: true,
    items: (options.items ?? ITEMS).map((i) => ({ ...i })),
    holdings: [...(options.holdings ?? [OPENING])],
    readyEntries: [],
    dropAnswerOnce: false,
    refuseNextChoice: false,
    unavailableNextChoice: false,
    dropMenus: 0,
    menuGates: [],
    holdNextChoice: null,
    entryNow: 7,
    rewards: [],
    fetch: undefined as unknown as typeof fetch,
  };
  const answers = new Map<string, Record<string, unknown>>();

  const json = (body: unknown, status = 200) =>
    new Response(JSON.stringify(body), { status });

  engine.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(String(input), "https://app.test");
    const path = url.pathname;
    const headers = (init?.headers ?? {}) as Record<string, string>;
    const body = init?.body
      ? (JSON.parse(String(init.body)) as Record<string, unknown>)
      : null;
    engine.calls.push({
      method: init?.method ?? "GET",
      path,
      body,
      authorization: headers.Authorization ?? null,
    });

    if (path.endsWith("/me/menu")) {
      if (engine.dropMenus > 0) {
        engine.dropMenus -= 1;
        throw new TypeError("Failed to fetch");
      }
      const gate = engine.menuGates.shift();
      const reply = json({
        open: engine.open,
        remaining_budget: engine.budget,
        items: engine.items.map((i) => ({
          opportunity_id: i.opportunity_id,
          subject_id: i.subject_id,
          subject_kind: i.subject_kind,
          subject_label: i.subject_label,
          label: i.label,
          cost: i.cost,
          taken: i.taken,
        })),
        rewards: engine.rewards,
      });
      if (gate) await gate;
      return reply;
    }
    if (path.endsWith("/me/choices")) {
      const choiceId = String(body?.choice_id);
      const opportunityId = String(body?.opportunity_id);
      if (engine.unavailableNextChoice) {
        engine.unavailableNextChoice = false;
        return json({ detail: "bad gateway" }, 503);
      }
      if (engine.refuseNextChoice) {
        engine.refuseNextChoice = false;
        if (engine.holdNextChoice) {
          const gate = engine.holdNextChoice;
          engine.holdNextChoice = null;
          await gate;
        }
        return json({ detail: { code: "not_on_menu" } }, 409);
      }
      const seen = answers.get(choiceId);
      let answer: Record<string, unknown>;
      if (seen) {
        answer = { ...seen, replayed: true };
      } else {
        const item = engine.items.find(
          (i) => i.opportunity_id === opportunityId,
        );
        if (!item) return json({ detail: { code: "not_on_menu" } }, 409);
        const firstTime = !item.taken;
        const cost = firstTime ? item.cost : 0;
        if (cost > engine.budget) {
          return json({ detail: { code: "budget_exhausted" } }, 409);
        }
        engine.budget -= cost;
        item.taken = true;
        engine.effects.push(choiceId);
        if (firstTime) {
          for (const concept of item.gives) {
            engine.holdings.push({
              concept_id: concept,
              label: item.label,
              text: item.content,
              found_from: item.subject_label,
              found_in_beat: "beat_internal_1",
              found_in_round_title: "A Quiet Evening",
              found_in_round_number: 1,
            });
          }
        }
        answer = {
          choice_id: choiceId,
          opportunity_id: opportunityId,
          content: item.content,
          gave: firstTime ? item.gives : [],
          cost,
          first_time: firstTime,
          replayed: false,
          remaining_budget: engine.budget,
        };
        answers.set(choiceId, answer);
      }
      if (engine.dropAnswerOnce) {
        engine.dropAnswerOnce = false;
        throw new TypeError("Failed to fetch");
      }
      if (engine.holdNextChoice) {
        const gate = engine.holdNextChoice;
        engine.holdNextChoice = null;
        await gate;
      }
      return json(answer);
    }
    if (path.endsWith("/me/ready")) {
      const entry = Number(body?.phase_entry);
      if (entry === engine.entryNow) engine.readyEntries.push(entry);
      return json({
        beat_id: "beat_internal_1",
        phase_entry: engine.entryNow,
        phase: "choices",
        status: "running",
        deadline_at: null,
      });
    }
    if (path.endsWith("/me/holdings")) {
      return json({ concepts: engine.holdings });
    }
    return json({ detail: "unexpected route" }, 404);
  }) as typeof fetch;

  return engine;
}

// Runs `body` with the engine installed as the page's fetch.
export async function withFetch<T>(
  engine: FakeEngine,
  body: () => Promise<T>,
): Promise<T> {
  const globals = globalThis as Record<string, unknown>;
  const real = globals.fetch;
  globals.fetch = engine.fetch;
  try {
    return await body();
  } finally {
    globals.fetch = real;
  }
}
