import renderer from "../../nightcap/mini_games/battle-of-wits/client/renderer";
import type {
  MiniGameDefinition,
  SurfaceLifecycle,
} from "./mini-game-kit/index";
import type {
  MiniGameState,
  MiniGameSubmissionResult,
} from "./mini-game-kit/wire-types";

interface Seat {
  token: string;
  character_id: string;
  participant_id: string;
}

interface Room {
  players: string[];
  game: MiniGameState | null;
  definition: MiniGameDefinition | null;
}

const seatKey = "battle-of-wits-seat";

class RoomError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

export function mountRoom(root: HTMLElement, fetcher = fetch): () => void {
  const doc = root.ownerDocument;
  const view = doc.defaultView!;
  const form = root.querySelector<HTMLFormElement>("form")!;
  const input = root.querySelector<HTMLInputElement>("#name")!;
  const lobby = root.querySelector<HTMLElement>("#lobby")!;
  const players = root.querySelector<HTMLUListElement>("#players")!;
  const stage = root.querySelector<HTMLElement>("#game")!;
  const start = root.querySelector<HTMLButtonElement>("#start")!;
  const message = root.querySelector<HTMLElement>("#message")!;
  const stored = view.sessionStorage.getItem(seatKey);
  let seat: Seat | null = stored ? JSON.parse(stored) : null;
  let active: MiniGameState | null = null;
  let lifecycle: SurfaceLifecycle | null = null;
  let lastGame = "";
  let lastPlayers = "";
  let stopped = false;
  let pending = false;
  let poll: number | undefined;

  async function request<T>(path: string, body?: object): Promise<T> {
    const headers = new Headers();
    if (seat) headers.set("Authorization", `Bearer ${seat.token}`);
    if (body) headers.set("Content-Type", "application/json");
    const response = await fetcher(path, {
      method: body ? "POST" : "GET",
      headers,
      body: body ? JSON.stringify(body) : undefined,
      cache: "no-store",
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new RoomError(
        response.status,
        typeof error.detail === "string" ? error.detail : "Try again.",
      );
    }
    return response.json();
  }

  function render(room: Room): void {
    form.hidden = true;
    lobby.hidden = room.game !== null;
    stage.hidden = room.game === null;
    start.hidden = room.game !== null && !room.game.resultHold;
    start.textContent = room.game ? "Play again" : "Start";
    const names = JSON.stringify(room.players);
    if (names !== lastPlayers) {
      players.replaceChildren(
        ...room.players.map((name) => {
          const item = doc.createElement("li");
          item.textContent = name;
          return item;
        }),
      );
      lastPlayers = names;
    }
    const game = room.game;
    if (!game || !seat || !room.definition) return;
    const signature = JSON.stringify(game);
    if (!lifecycle || active?.runId !== game.runId) {
      lifecycle?.unmount();
      lifecycle = renderer.mount(stage, {
        surface: "phone",
        sessionId: "standalone",
        participantId: seat.participant_id,
        characterId: seat.character_id,
        definition: room.definition,
        state: game,
        submit: (payload, submissionId) =>
          request<MiniGameSubmissionResult>("/api/answer", {
            run_id: game.runId,
            submission_id: submissionId,
            payload,
          }),
        onEvent: () => () => {},
        reportPerf: () => {},
      });
    } else if (signature !== lastGame) {
      lifecycle.update(game);
    }
    active = game;
    lastGame = signature;
  }

  async function refresh(job: () => Promise<Room>): Promise<void> {
    if (stopped || pending) return;
    pending = true;
    try {
      const room = await job();
      if (stopped) return;
      render(room);
      message.textContent = "";
    } catch (error) {
      if (stopped) return;
      if (error instanceof RoomError && error.status === 401) {
        seat = null;
        view.sessionStorage.removeItem(seatKey);
        lifecycle?.unmount();
        lifecycle = null;
        active = null;
        form.hidden = false;
        lobby.hidden = stage.hidden = start.hidden = true;
      }
      message.textContent =
        error instanceof RoomError
          ? error.message
          : "Waiting for the room to reconnect.";
    } finally {
      pending = false;
    }
  }

  const read = () => request<Room>("/api/room");

  function join(event: Event) {
    event.preventDefault();
    void refresh(async () => {
      seat = await request<Seat>("/api/join", { name: input.value });
      view.sessionStorage.setItem(seatKey, JSON.stringify(seat));
      form.hidden = true;
      return read();
    });
  }

  function begin() {
    void refresh(() =>
      request<Room>("/api/start", { previous_run: active?.runId ?? null }),
    );
  }

  async function pollRoom() {
    if (seat) await refresh(read);
    if (!stopped) poll = view.setTimeout(() => void pollRoom(), 450);
  }

  form.hidden = seat !== null;
  form.addEventListener("submit", join);
  start.addEventListener("click", begin);
  void pollRoom();
  return () => {
    stopped = true;
    view.clearTimeout(poll);
    form.removeEventListener("submit", join);
    start.removeEventListener("click", begin);
    lifecycle?.unmount();
  };
}
