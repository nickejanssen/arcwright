// Listens to the session's event stream, and nothing more: it reads only the
// event number, so a screen knows when to ask the round and lobby routes again.
// What the screens show always comes from those routes, never from an event.

export type EventSignal = "event" | "reconnect" | "restart";

export interface EventSubscription {
  sessionId: string;
  onSignal: (signal: EventSignal) => void;
  fetcher?: typeof fetch;
  retryMs?: number;
}

// Returns a function that stops listening. Event numbers going backwards mean
// the engine restarted and numbers began again; that is a "restart" signal.
export function subscribeEvents(options: EventSubscription): () => void {
  const fetcher = options.fetcher ?? fetch;
  const retryMs = options.retryMs ?? 3000;
  let active = true;
  let last = 0;
  let retryTimer: ReturnType<typeof setTimeout> | null = null;

  function handleBlock(block: string): void {
    for (const line of block.split("\n")) {
      if (!line.startsWith("data:")) continue;
      const json = line.slice(5).trim();
      if (!json) continue;
      let number: unknown;
      try {
        number = (JSON.parse(json) as { sequence_number?: unknown })
          .sequence_number;
      } catch {
        continue;
      }
      if (typeof number !== "number") continue;
      const restarted = number < last;
      last = number;
      options.onSignal(restarted ? "restart" : "event");
    }
  }

  async function run(): Promise<void> {
    let res: Response | null;
    try {
      res = await fetcher(
        `/v1/sessions/${encodeURIComponent(options.sessionId)}/events?since=${last}`,
      );
    } catch {
      res = null;
    }
    if (active && res?.ok && res.body) {
      // The stream is open again: anything that happened while it was down is
      // picked up by asking the routes.
      options.onSignal("reconnect");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      try {
        while (active) {
          const { done, value } = await reader.read();
          if (done) break;
          buf += decoder.decode(value, { stream: true });
          buf = buf.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
          const blocks = buf.split("\n\n");
          buf = blocks.pop() ?? "";
          for (const block of blocks) handleBlock(block);
        }
      } catch {
        // A broken stream is retried below.
      } finally {
        reader.cancel().catch(() => undefined);
      }
    }
    if (active) retryTimer = setTimeout(() => void run(), retryMs);
  }

  void run();
  return () => {
    active = false;
    if (retryTimer) clearTimeout(retryTimer);
  };
}
