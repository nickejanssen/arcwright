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
import type { RendererRegistry } from "./registry.js";

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
const RECONNECT_MAX_RETRIES = 3;
const RECONNECT_INITIAL_DELAY_MS = 250;

function setStageState(stage: HTMLElement, state: string): void {
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
  const stream: StreamState = {
    cancelled: false,
    lastSequence: 0,
    reader: null,
  };
  const eventListeners: Array<(event: ContentEvent) => void> = [];
  let active: ActiveMount | null = null;

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

  const dispatchEvent = (event: ContentEvent): void => {
    stream.lastSequence = Math.max(stream.lastSequence, event.sequence_number);
    for (const listener of eventListeners) {
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

  const mountRenderer = async (state: MiniGameState): Promise<void> => {
    if (!opts.registry.has(state.gameId)) {
      setStageState(stage, "unknown-game");
      return;
    }
    const renderer: MiniGameRenderer = opts.registry.get(state.gameId);
    let definition: MiniGameDefinition;
    try {
      definition = await opts.loadDefinition(state.gameId, "latest");
    } catch {
      setStageState(stage, "definition-error");
      return;
    }

    const perf = perfReporterFor(state.gameId);
    const startedAt = performanceNow(view);
    const handleEvent = (event: ContentEvent): void => {
      mountedLifecycle?.handleEvent(event);
    };
    const unsubscribe = subscribe(handleEvent);

    let mountedLifecycle: SurfaceLifecycle | null = null;
    const ctx = buildContext(state, definition, perf);
    try {
      mountedLifecycle = renderer.mount(stage, ctx);
    } catch {
      unsubscribe();
      setStageState(stage, "render-error");
      return;
    }

    const mountElapsed = performanceNow(view) - startedAt;
    perf.report("mount_to_paint_ms", mountElapsed);
    setStageState(stage, `active:${state.gameId}`);

    active = {
      gameId: state.gameId,
      runId: state.runId,
      lifecycle: mountedLifecycle,
      unsubscribeEvents: unsubscribe,
    };
  };

  const refresh = async (): Promise<void> => {
    const state = await fetchActiveState();
    if (!state) {
      unmountActive();
      setStageState(stage, "idle");
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
    await mountRenderer(state);
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
        if (++retries > RECONNECT_MAX_RETRIES) return;
        await delay(RECONNECT_INITIAL_DELAY_MS * 2 ** (retries - 1), view);
        continue;
      }
      if (!res.ok || !res.body) {
        if (++retries > RECONNECT_MAX_RETRIES) return;
        await delay(RECONNECT_INITIAL_DELAY_MS * 2 ** (retries - 1), view);
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

  const maybeReactToStateTransition = (event: ContentEvent): void => {
    if (event.category !== "state_transition") return;
    if (
      event.event_type === "mini_game_started" ||
      event.event_type === "mini_game_completed" ||
      event.event_type === "mini_game_timed_out" ||
      event.event_type === "mini_game_cancelled" ||
      event.event_type === "mini_game_paused" ||
      event.event_type === "mini_game_resumed"
    ) {
      void refresh();
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
