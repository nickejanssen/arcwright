// Browser-side glue: fetch state, open SSE direct to Arcwright, mount the
// right renderer, handle reconnect, report perf. The Worker is not in the
// data path; the player token scopes Arcwright's stream and submission
// endpoints for this participant.

import type {
  ContentEvent,
  MiniGamePayload,
  MiniGameState,
  MiniGameSubmissionResult,
} from "../mini-game-kit/wire-types.js";
import type {
  MiniGameContext,
  MiniGameDefinition,
  MiniGameRenderer,
  Surface,
  SurfaceLifecycle,
} from "../mini-game-kit/index.js";
import { withAudienceGuard } from "../mini-game-kit/index.js";
import {
  createPerfReporter,
  type PerfTransport,
} from "../mini-game-kit/perf.js";
import {
  StageStates,
  buildActiveStageState,
  type StageState,
} from "./stage.js";
import type { RendererRegistry } from "./registry.js";

export interface RetryPolicy {
  maxRetries?: number;
  initialDelayMs?: number;
}

export interface StageBootOptions {
  registry: RendererRegistry;
  baseUrl: string;
  sessionId: string;
  /**
   * The player's sign-in. Left out on the shared display (AW-330, spec 0095
   * decision 6): the TV holds no sign-in, so it reads the public display route
   * and the public event stream and sends no Authorization header.
   */
  token?: string;
  surface: Surface;
  participantId: string;
  characterId: string;
  loadDefinition(gameId: string, version: string): Promise<MiniGameDefinition>;
  view?: Window | null;
  fetcher?: typeof fetch;
  now?: () => number;
  perfTransport?: PerfTransport;
  /**
   * Aborting stops the boot: a boot still waiting for its first reply never
   * mounts, and a running one unmounts. Added in the dashboard copy (AW-329)
   * so a React effect cleanup can cancel a pending boot.
   */
  signal?: AbortSignal;
  retry?: RetryPolicy;
}

export interface StageController {
  refresh(): Promise<void>;
  unmount(): void;
}

interface StreamState {
  cancelled: boolean;
  lastSequence: number;
  reader: ReadableStreamDefaultReader<Uint8Array> | null;
}

interface ActiveMount {
  gameId: string;
  runId: string;
  lifecycle: SurfaceLifecycle;
  unsubscribeEvents: () => void;
}

const STAGE_STATE_ATTR = "data-mini-game-state";
const DEFAULT_RECONNECT_MAX_RETRIES = 3;
const DEFAULT_RECONNECT_INITIAL_DELAY_MS = 250;

// State-transition event types that drive a stage refresh.
const STATE_TRANSITION_EVENT_TYPES = new Set([
  "mini_game_started",
  "mini_game_completed",
  "mini_game_timed_out",
  "mini_game_cancelled",
  "mini_game_paused",
  "mini_game_resumed",
  "mini_game_result_hold",
  "mini_game_result_ready_changed",
  "phase_changed",
]);

function setStageState(stage: HTMLElement, state: StageState): void {
  stage.setAttribute(STAGE_STATE_ATTR, state);
}

function performanceNow(view: Window | null): number {
  const perf = view?.performance;
  if (perf && typeof perf.now === "function") return perf.now();
  return Date.now();
}

function toSubmissionResult(
  submissionId: string,
  isAccepted: boolean,
  rejectionReason?: string | null,
): MiniGameSubmissionResult {
  if (rejectionReason !== null && rejectionReason !== undefined) {
    return { submissionId, isAccepted, rejectionReason };
  }
  return { submissionId, isAccepted };
}

function generateSubmissionId(
  state: MiniGameState,
  stream: StreamState,
  view: Window | null,
): string {
  const cryptoGlobal = (
    globalThis as { crypto?: { randomUUID?: () => string } }
  ).crypto;
  if (cryptoGlobal?.randomUUID) return cryptoGlobal.randomUUID();
  return `${state.runId}-${stream.lastSequence}-${performanceNow(view)}`;
}

export async function bootMiniGameStage(
  stage: HTMLElement,
  opts: StageBootOptions,
): Promise<StageController> {
  const view = opts.view ?? (typeof window !== "undefined" ? window : null);
  const doFetch = opts.fetcher ?? fetch;
  const baseUrl = opts.baseUrl.replace(/\/$/, "");
  const maxRetries = opts.retry?.maxRetries ?? DEFAULT_RECONNECT_MAX_RETRIES;
  const initialDelayMs =
    opts.retry?.initialDelayMs ?? DEFAULT_RECONNECT_INITIAL_DELAY_MS;
  const stream: StreamState = {
    cancelled: false,
    lastSequence: 0,
    reader: null,
  };
  const eventListeners: Array<(event: ContentEvent) => void> = [];
  let active: ActiveMount | null = null;
  // Monotonic sequence used to invalidate stale in-flight refresh() calls.
  // Each refresh() captures its sequence at the start; after every await it
  // checks that no newer refresh has begun. This prevents double-mount on
  // concurrent state_transition events and on the boot/streamLoop overlap.
  let refreshSequence = 0;
  let playerNames: Record<string, string> = {};
  let lastState: MiniGameState | null = null;
  let namesLoading = false;
  let namesRetry: ReturnType<typeof setTimeout> | undefined;
  let namesAbort: AbortController | undefined;
  let resultPoll: ReturnType<typeof setTimeout> | undefined;
  let readFailed = false;
  const isStale = (seq: number): boolean =>
    seq !== refreshSequence || opts.signal?.aborted === true;

  const perfReporterFor = (gameId: string) =>
    createPerfReporter({
      baseUrl,
      sessionId: opts.sessionId,
      token: opts.token ?? "",
      surface: opts.surface,
      gameId,
      participantId: opts.participantId,
      view,
      ...(opts.perfTransport ? { transport: opts.perfTransport } : {}),
    });

  // Iterating over a snapshot (slice) keeps event handlers that unsubscribe
  // mid-dispatch (via refresh → unmountActive → unsubscribeEvents) from
  // skipping their siblings in the original array.
  const dispatchEvent = (event: ContentEvent): void => {
    stream.lastSequence = Math.max(stream.lastSequence, event.sequence_number);
    for (const listener of eventListeners.slice()) {
      try {
        listener(event);
      } catch {
        // Renderer errors must not break the stream loop. Silently drop.
      }
    }
  };

  const guardedListener = (
    handler: (event: ContentEvent) => void,
  ): ((event: ContentEvent) => void) =>
    withAudienceGuard(
      { surface: opts.surface, participantId: opts.participantId },
      handler,
    );

  const subscribe = (handler: (event: ContentEvent) => void): (() => void) => {
    const guarded = guardedListener(handler);
    eventListeners.push(guarded);
    return () => {
      const idx = eventListeners.indexOf(guarded);
      if (idx >= 0) eventListeners.splice(idx, 1);
    };
  };

  // No token means no header at all, and the public display route.
  const authHeaders = (): Record<string, string> =>
    opts.token ? { Authorization: `Bearer ${opts.token}` } : {};

  const loadNames = async (runId: string): Promise<void> => {
    if (namesLoading) return;
    namesLoading = true;
    let succeeded = false;
    const controller = new AbortController();
    namesAbort = controller;
    let timeout: ReturnType<typeof setTimeout> | undefined;
    try {
      const lobby = await Promise.race([
        doFetch(
          `${baseUrl}/v1/sessions/${encodeURIComponent(opts.sessionId)}/lobby`,
          { signal: controller.signal },
        ),
        new Promise<Response>((_, reject) => {
          timeout = setTimeout(() => {
            controller.abort();
            reject(new Error("name lookup timed out"));
          }, 5000);
        }),
      ]);
      if (!lobby.ok) return;
      const body = (await lobby.json()) as {
        players?: Array<{
          character_id?: unknown;
          participant_id?: unknown;
          display_name?: unknown;
        }>;
      };
      const names: Record<string, string> = {};
      for (const player of body.players ?? []) {
        if (
          typeof player.display_name !== "string" ||
          !player.display_name.trim()
        )
          continue;
        if (typeof player.character_id === "string")
          names[player.character_id] = player.display_name;
        if (typeof player.participant_id === "string")
          names[player.participant_id] = player.display_name;
      }
      if (
        stream.cancelled ||
        opts.signal?.aborted ||
        lastState?.runId !== runId
      )
        return;
      playerNames = names;
      succeeded = true;
      if (lastState && active && active.runId === lastState.runId) {
        lastState = { ...lastState, playerNames };
        active.lifecycle.update(lastState);
      }
    } catch {
      // A later refresh retries the public names lookup.
    } finally {
      if (timeout !== undefined) clearTimeout(timeout);
      namesLoading = false;
      namesAbort = undefined;
      if (lastState && lastState.runId !== runId && !stream.cancelled) {
        void loadNames(lastState.runId);
      } else if (!succeeded && !stream.cancelled && !opts.signal?.aborted) {
        namesRetry = setTimeout(() => {
          namesRetry = undefined;
          if (lastState) void loadNames(lastState.runId);
        }, 2000);
      }
    }
  };

  const fetchActiveState = async (): Promise<MiniGameState | null> => {
    readFailed = false;
    const url = `${baseUrl}/v1/sessions/${encodeURIComponent(opts.sessionId)}/mini-games/active${opts.token ? "" : "/display"}`;
    let res: Response;
    try {
      res = await doFetch(url, { headers: authHeaders() });
    } catch {
      readFailed = true;
      return null;
    }
    if (res.status === 404) {
      try {
        const result = await doFetch(
          `${baseUrl}/v1/sessions/${encodeURIComponent(opts.sessionId)}/mini-games/result/display`,
        );
        if (result.status === 404) return null;
        if (!result.ok) {
          readFailed = true;
          return null;
        }
        const data = (await result.json()) as {
          run_id: string;
          game_id: string;
          definition_version: string;
          phase_entry: number;
          deadline_at: string | null;
          standing: string[][];
        };
        let myReady = false;
        let readyCount: number | undefined;
        let playerCount: number | undefined;
        let paused = false;
        let secondsLeft: number | null = null;
        {
          const roomController = new AbortController();
          let roomTimeout: ReturnType<typeof setTimeout> | undefined;
          try {
            const room = await Promise.race([
              doFetch(
                `${baseUrl}/v1/sessions/${encodeURIComponent(opts.sessionId)}/room`,
                { signal: roomController.signal },
              ),
              new Promise<Response>((_, reject) => {
                roomTimeout = setTimeout(() => {
                  roomController.abort();
                  reject(new Error("room lookup timed out"));
                }, 1000);
              }),
            ]);
            if (room.ok) {
              const body = (await room.json()) as {
                phase_entry?: number;
                players?: Array<{ participant_id: string; ready: boolean }>;
                ready_count?: number;
                player_count?: number;
                paused?: boolean;
                seconds_left?: number | null;
              };
              if (body.phase_entry !== data.phase_entry) return null;
              myReady =
                body.phase_entry === data.phase_entry &&
                body.players?.some(
                  (p) => p.participant_id === opts.participantId && p.ready,
                ) === true;
              readyCount = body.ready_count;
              playerCount = body.player_count;
              paused = body.paused === true;
              secondsLeft = body.seconds_left ?? null;
            }
          } catch {
            // The ready action remains idempotent when the room read fails.
          } finally {
            if (roomTimeout !== undefined) clearTimeout(roomTimeout);
          }
        }
        return {
          runId: data.run_id,
          gameId: data.game_id,
          definitionVersion: data.definition_version,
          status: "completed",
          deadlineAt: data.deadline_at,
          resultHold: {
            phaseEntry: data.phase_entry,
            standing: data.standing,
            myReady,
            readyCount,
            playerCount,
            paused,
            secondsLeft,
          },
          playerNames,
          mySubmissions: [],
        };
      } catch {
        readFailed = true;
        return null;
      }
    }
    if (!res.ok) {
      readFailed = true;
      return null;
    }
    const data = (await res.json()) as {
      run_id: string;
      game_id: string;
      definition_version?: string | null;
      status: MiniGameState["status"];
      deadline_at: string | null;
      runtime_state?: Record<string, unknown> | null;
      presentation?: Record<string, unknown> | null;
      phase_state?: Record<string, unknown> | null;
      my_submissions: Array<{
        submission_id: string;
        is_accepted: boolean;
        rejection_reason?: string | null;
      }>;
    };
    return {
      runId: data.run_id,
      gameId: data.game_id,
      ...(data.definition_version
        ? { definitionVersion: data.definition_version }
        : {}),
      status: data.status,
      deadlineAt: data.deadline_at,
      ...(data.runtime_state ? { runtimeState: data.runtime_state } : {}),
      ...(data.presentation ? { presentation: data.presentation } : {}),
      ...(data.phase_state ? { phaseState: data.phase_state } : {}),
      ...(opts.surface === "shared_display" ? { playerNames } : {}),
      mySubmissions: data.my_submissions.map((s) =>
        toSubmissionResult(s.submission_id, s.is_accepted, s.rejection_reason),
      ),
    };
  };

  const submitAction = async (
    runId: string,
    submissionId: string,
    payload: MiniGamePayload,
  ): Promise<MiniGameSubmissionResult> => {
    if (!opts.token) throw new Error("submission needs a sign-in");
    const url = `${baseUrl}/v1/sessions/${encodeURIComponent(opts.sessionId)}/mini-games/${encodeURIComponent(runId)}/submissions`;
    const res = await doFetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${opts.token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ submission_id: submissionId, payload }),
    });
    if (!res.ok) {
      throw new Error(`submission failed: ${res.status} ${res.statusText}`);
    }
    const data = (await res.json()) as {
      submission_id: string;
      is_accepted: boolean;
      rejection_reason?: string | null;
    };
    return toSubmissionResult(
      data.submission_id,
      data.is_accepted,
      data.rejection_reason,
    );
  };

  const buildContext = (
    state: MiniGameState,
    definition: MiniGameDefinition,
    perf: ReturnType<typeof createPerfReporter>,
  ): MiniGameContext => ({
    surface: opts.surface,
    sessionId: opts.sessionId,
    participantId: opts.participantId,
    characterId: opts.characterId,
    state,
    definition,
    ...(opts.token
      ? {
          markReady: async (phaseEntry: number) => {
            const res = await doFetch(
              `${baseUrl}/v1/sessions/${encodeURIComponent(opts.sessionId)}/me/ready`,
              {
                method: "POST",
                headers: {
                  ...authHeaders(),
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({ phase_entry: phaseEntry }),
              },
            );
            if (!res.ok) throw new Error(`ready failed: ${res.status}`);
          },
        }
      : {}),
    submit: async (payload, submissionId) => {
      const id = submissionId ?? generateSubmissionId(state, stream, view);
      return submitAction(state.runId, id, payload);
    },
    onEvent: subscribe,
    reportPerf: (name, value) => perf.report(name, value),
  });

  const unmountActive = (): void => {
    if (!active) return;
    try {
      active.lifecycle.unmount();
    } catch {
      // ignore
    }
    active.unsubscribeEvents();
    active = null;
  };

  // mountRenderer is sequence-aware: if a newer refresh begins while we are
  // awaiting loadDefinition, this mount aborts before subscribing or setting
  // active. Otherwise two concurrent state_transition events could both pass
  // their refresh()-level sequence check (since active is still null) and
  // both subscribe, leaking the first listener when the second overwrites
  // `active`.
  const mountRenderer = async (
    state: MiniGameState,
    mySeq: number,
  ): Promise<void> => {
    if (!opts.registry.has(state.gameId)) {
      setStageState(stage, StageStates.UnknownGame);
      return;
    }
    if (!state.definitionVersion) {
      setStageState(stage, StageStates.DefinitionError);
      return;
    }
    const renderer: MiniGameRenderer = opts.registry.get(state.gameId);
    let definition: MiniGameDefinition;
    try {
      definition = await opts.loadDefinition(
        state.gameId,
        state.definitionVersion,
      );
    } catch {
      if (isStale(mySeq)) return;
      setStageState(stage, StageStates.DefinitionError);
      return;
    }
    if (isStale(mySeq)) return;

    const perf = perfReporterFor(state.gameId);
    const startedAt = performanceNow(view);
    const handleEvent = (event: ContentEvent): void => {
      mountedLifecycle?.handleEvent(event);
    };
    const unsubscribe = subscribe(handleEvent);

    let mountedLifecycle: SurfaceLifecycle | null = null;
    const ctx = buildContext(state, definition, perf);
    // Flip the stage to its active state *before* renderer.mount so the
    // CSS idle placeholder cannot paint adjacent to the renderer's DOM
    // during a frame boundary between mount and the post-mount attribute
    // write.
    setStageState(stage, buildActiveStageState(state.gameId));
    try {
      mountedLifecycle = renderer.mount(stage, ctx);
    } catch {
      unsubscribe();
      // Wipe any partial DOM the renderer left behind before signaling
      // error so the error label is not interleaved with broken markup.
      stage.replaceChildren();
      setStageState(stage, StageStates.RenderError);
      return;
    }

    const mountElapsed = performanceNow(view) - startedAt;
    perf.report("mount_to_paint_ms", mountElapsed);

    active = {
      gameId: state.gameId,
      runId: state.runId,
      lifecycle: mountedLifecycle,
      unsubscribeEvents: unsubscribe,
    };
    if (lastState?.runId === state.runId) {
      lastState = { ...lastState, playerNames };
      active.lifecycle.update(lastState);
    }
  };

  const refresh = async (): Promise<void> => {
    const mySeq = ++refreshSequence;
    const previousState = lastState;
    const state = await fetchActiveState();
    if (isStale(mySeq)) return;
    if (lastState?.runId !== state?.runId) {
      playerNames = {};
      namesAbort?.abort();
    }
    lastState = state;
    if (resultPoll !== undefined) clearTimeout(resultPoll);
    resultPoll = state?.resultHold
      ? setTimeout(() => {
          void refresh();
        }, 2000)
      : undefined;
    if (state) {
      state.playerNames = playerNames;
      void loadNames(state.runId);
    }
    if (!state) {
      if (readFailed && previousState?.resultHold) {
        lastState = previousState;
        resultPoll = setTimeout(() => {
          void refresh();
        }, 1000);
        return;
      }
      unmountActive();
      setStageState(stage, StageStates.Idle);
      return;
    }
    if (
      active &&
      active.runId === state.runId &&
      active.gameId === state.gameId
    ) {
      active.lifecycle.update(state);
      return;
    }
    unmountActive();
    if (isStale(mySeq)) return;
    await mountRenderer(state, mySeq);
  };

  const maybeReactToStateTransition = (event: ContentEvent): void => {
    if (event.category !== "state_transition") return;
    if (STATE_TRANSITION_EVENT_TYPES.has(event.event_type)) {
      void refresh();
    }
  };

  const streamLoop = async (): Promise<void> => {
    let retries = 0;
    while (!stream.cancelled) {
      const url = `${baseUrl}/v1/sessions/${encodeURIComponent(opts.sessionId)}/events?since=${stream.lastSequence}`;
      let res: Response;
      try {
        res = await doFetch(url, { headers: authHeaders() });
      } catch {
        if (++retries > maxRetries) return;
        await delay(initialDelayMs * 2 ** (retries - 1), view);
        continue;
      }
      if (!res.ok || !res.body) {
        if (++retries > maxRetries) return;
        await delay(initialDelayMs * 2 ** (retries - 1), view);
        continue;
      }
      retries = 0;
      await refresh();
      stream.reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      try {
        while (!stream.cancelled) {
          const { done, value } = await stream.reader.read();
          if (done) break;
          buf += decoder.decode(value, { stream: true });
          buf = buf.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
          const blocks = buf.split("\n\n");
          buf = blocks.pop() ?? "";
          for (const block of blocks) {
            for (const line of block.split("\n")) {
              if (!line.startsWith("data:")) continue;
              const json = line.slice(5).trim();
              if (!json) continue;
              try {
                const event = JSON.parse(json) as ContentEvent;
                dispatchEvent(event);
                maybeReactToStateTransition(event);
              } catch {
                // malformed event; skip
              }
            }
          }
        }
      } finally {
        stream.reader = null;
      }
      if (stream.cancelled) return;
      // Stream ended unexpectedly; re-fetch state then reconnect.
      await refresh();
    }
  };

  const controller: StageController = {
    refresh,
    unmount: () => {
      stream.cancelled = true;
      if (namesRetry !== undefined) clearTimeout(namesRetry);
      if (resultPoll !== undefined) clearTimeout(resultPoll);
      namesAbort?.abort();
      refreshSequence++;
      lastState = null;
      if (stream.reader) {
        void stream.reader.cancel();
        stream.reader = null;
      }
      unmountActive();
      // Leave the stage in idle state so the CSS placeholder reappears and
      // the data attribute does not advertise a stale active run.
      setStageState(stage, StageStates.Idle);
    },
  };

  if (opts.signal?.aborted) return controller;
  opts.signal?.addEventListener("abort", () => controller.unmount(), {
    once: true,
  });
  await refresh();
  if (opts.signal?.aborted) return controller;
  void streamLoop();
  return controller;
}

function delay(ms: number, view: Window | null): Promise<void> {
  return new Promise((resolve) => {
    if (view && typeof view.setTimeout === "function") {
      view.setTimeout(resolve, ms);
    } else {
      setTimeout(resolve, ms);
    }
  });
}
