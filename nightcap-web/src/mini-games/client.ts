// Browser-side glue: fetch state, open SSE direct to Arcwright, mount the
// right renderer, handle reconnect, report perf. The Worker is not in the
// data path; the player token scopes Arcwright's stream and submission
// endpoints for this participant.

import type {
  ContentEvent,
  MiniGamePayload,
  MiniGameState,
  MiniGameSubmissionResult,
} from "../types.js";
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
  token: string;
  surface: Surface;
  participantId: string;
  characterId: string;
  loadDefinition(gameId: string, version: string): Promise<MiniGameDefinition>;
  view?: Window | null;
  fetcher?: typeof fetch;
  now?: () => number;
  perfTransport?: PerfTransport;
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

  const perfReporterFor = (gameId: string) =>
    createPerfReporter({
      baseUrl,
      sessionId: opts.sessionId,
      token: opts.token,
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

  const fetchActiveState = async (): Promise<MiniGameState | null> => {
    const url = `${baseUrl}/v1/sessions/${encodeURIComponent(opts.sessionId)}/mini-games/active`;
    let res: Response;
    try {
      res = await doFetch(url, {
        headers: { Authorization: `Bearer ${opts.token}` },
      });
    } catch {
      return null;
    }
    if (res.status === 404) return null;
    if (!res.ok) return null;
    const data = (await res.json()) as {
      run_id: string;
      game_id: string;
      status: MiniGameState["status"];
      deadline_at: string | null;
      my_submissions: Array<{
        submission_id: string;
        is_accepted: boolean;
        rejection_reason?: string | null;
      }>;
    };
    return {
      runId: data.run_id,
      gameId: data.game_id,
      status: data.status,
      deadlineAt: data.deadline_at,
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
    submit: async (payload) => {
      const submissionId =
        (
          globalThis as { crypto?: { randomUUID?: () => string } }
        ).crypto?.randomUUID?.() ??
        `${state.runId}-${stream.lastSequence}-${performanceNow(view)}`;
      return submitAction(state.runId, submissionId, payload);
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
    const renderer: MiniGameRenderer = opts.registry.get(state.gameId);
    let definition: MiniGameDefinition;
    try {
      definition = await opts.loadDefinition(state.gameId, "latest");
    } catch {
      if (mySeq !== refreshSequence) return;
      setStageState(stage, StageStates.DefinitionError);
      return;
    }
    if (mySeq !== refreshSequence) return;

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
  };

  const refresh = async (): Promise<void> => {
    const mySeq = ++refreshSequence;
    const state = await fetchActiveState();
    if (mySeq !== refreshSequence) return;
    if (!state) {
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
    if (mySeq !== refreshSequence) return;
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
        res = await doFetch(url, {
          headers: { Authorization: `Bearer ${opts.token}` },
        });
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

  await refresh();
  void streamLoop();

  return {
    refresh,
    unmount: () => {
      stream.cancelled = true;
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
