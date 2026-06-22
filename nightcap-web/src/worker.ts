import { NightcapConnector, type CreateSessionRequest } from "./connector.js";
import { NightcapRoom } from "./room.js";

export { NightcapRoom } from "./room.js";

export interface NightcapWorkerEnv {
  ARCWRIGHT_API_BASE_URL: string;
  ARCWRIGHT_API_KEY: string;
  BOOTSTRAP_TOKEN: string;
  ROOMS: DurableObjectNamespace<NightcapRoom>;
}

function json(value: unknown, init?: ResponseInit): Response {
  return new Response(JSON.stringify(value), {
    ...init,
    headers: {
      "content-type": "application/json; charset=utf-8",
      ...(init?.headers ?? {}),
    },
  });
}

function roomPath(sessionId: string): string {
  return `/rooms/${sessionId}`;
}

function parseSegment(pathname: string, index: number): string | null {
  const segment = pathname.split("/")[index];
  return segment && segment.length > 0 ? segment : null;
}

const BOOTSTRAP_TOKEN_HEADER = "x-arcwright-bootstrap-token";

export function authorizeBootstrapSession(
  request: Request,
  env: NightcapWorkerEnv,
): Response | null {
  if (!env.BOOTSTRAP_TOKEN || env.BOOTSTRAP_TOKEN.trim().length === 0) {
    return new Response("Bootstrap token is not configured", {
      status: 503,
    });
  }

  const providedToken = request.headers.get(BOOTSTRAP_TOKEN_HEADER);
  if (providedToken !== env.BOOTSTRAP_TOKEN) {
    return new Response("Unauthorized", { status: 401 });
  }

  return null;
}

export async function bootstrapSession(
  connector: NightcapConnector,
  body: CreateSessionRequest,
): Promise<Response> {
  const session = await connector.createSession(body);
  return json({
    session,
    runtime: {
      // Reuse the session id as the room key for the DO namespace lookup.
      room_id: session.session_id,
      room_url: roomPath(session.session_id),
    },
  });
}

export async function loadSession(
  connector: NightcapConnector,
  sessionId: string,
): Promise<Response> {
  const session = await connector.getSession(sessionId);
  return json({ session });
}

export default {
  async fetch(
    request: Request,
    env: NightcapWorkerEnv,
    _ctx: ExecutionContext,
  ): Promise<Response> {
    void _ctx;
    const url = new URL(request.url);
    const connector = new NightcapConnector({
      baseUrl: env.ARCWRIGHT_API_BASE_URL,
      apiKey: env.ARCWRIGHT_API_KEY,
    });

    if (request.method === "POST" && url.pathname === "/bootstrap/session") {
      const denied = authorizeBootstrapSession(request, env);
      if (denied) {
        return denied;
      }

      const body = (await request.json()) as CreateSessionRequest;
      return bootstrapSession(connector, body);
    }

    if (request.method === "GET" && url.pathname.startsWith("/sessions/")) {
      const sessionId = parseSegment(url.pathname, 2);
      if (!sessionId) {
        return new Response("Not found", { status: 404 });
      }
      return loadSession(connector, sessionId);
    }

    if (
      url.pathname.startsWith("/rooms/") &&
      (url.pathname.endsWith("/join") ||
        url.pathname.endsWith("/leave") ||
        url.pathname.endsWith("/snapshot"))
    ) {
      const sessionId = parseSegment(url.pathname, 2);
      if (!sessionId) {
        return new Response("Not found", { status: 404 });
      }
      const room = env.ROOMS.get(env.ROOMS.idFromName(sessionId));
      return room.fetch(request);
    }

    return new Response("Not found", { status: 404 });
  },
};
