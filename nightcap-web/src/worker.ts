import {
  NightcapConnector,
  type CreateSessionRequest,
  type EndSessionRequest,
} from "./connector.js";
import {
  buildNightcapRuntimeUrls,
  normalizePersonalizationIntake,
  type NightcapBootstrapRequest,
  type NightcapBootstrapResponse,
  type NightcapLifecycleEndRequest,
  type NightcapLifecycleResponse,
} from "./runtime.js";
import { NightcapRoom } from "./room.js";
import {
  renderHostPage,
  renderLandingPage,
  renderSharedDisplayPage,
} from "./ui.js";

export { renderHostPage, renderLandingPage, renderSharedDisplayPage };
export { NightcapRoom };

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

function html(value: string, init?: ResponseInit): Response {
  return new Response(value, {
    ...init,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store",
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

function readBearerToken(request: Request): string | null {
  const header = request.headers.get("Authorization");
  if (!header || !header.startsWith("Bearer ")) {
    return null;
  }
  const token = header.slice("Bearer ".length).trim();
  return token.length > 0 ? token : null;
}

async function readJsonBody<T>(request: Request): Promise<T | null> {
  try {
    return (await request.json()) as T;
  } catch {
    return null;
  }
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

function connectorFor(env: NightcapWorkerEnv): NightcapConnector {
  return new NightcapConnector({
    baseUrl: env.ARCWRIGHT_API_BASE_URL,
    apiKey: env.ARCWRIGHT_API_KEY,
  });
}

export async function bootstrapSession(
  connector: NightcapConnector,
  body: CreateSessionRequest,
): Promise<Response> {
  const session = await connector.createSession(body);
  return json({
    session,
    runtime: {
      room_id: session.session_id,
      room_url: roomPath(session.session_id),
    },
  });
}

export async function createHostSession(
  connector: NightcapConnector,
  body: NightcapBootstrapRequest,
): Promise<Response> {
  const { personalization_intake, ...sessionBody } = body;
  const session = await connector.createSession(sessionBody);
  const runtime = buildNightcapRuntimeUrls(session.session_id);
  return json({
    session,
    runtime: {
      room_id: session.session_id,
      ...runtime,
    },
    personalization_intake: normalizePersonalizationIntake(
      personalization_intake,
    ),
  } satisfies NightcapBootstrapResponse);
}

export async function loadSession(
  connector: NightcapConnector,
  sessionId: string,
): Promise<Response> {
  const session = await connector.getSession(sessionId);
  return json({ session });
}

export async function proxySessionLifecycle(
  connector: NightcapConnector,
  sessionId: string,
  action: "start" | "pause" | "resume" | "end",
  request: Request,
): Promise<Response> {
  const accessToken = readBearerToken(request);
  if (!accessToken) {
    return new Response("Authorization header required", { status: 401 });
  }

  try {
    if (action === "start") {
      return json({
        session: await connector.startSession(sessionId, accessToken),
      } satisfies NightcapLifecycleResponse);
    }

    if (action === "pause") {
      return json({
        session: await connector.pauseSession(sessionId, accessToken),
      } satisfies NightcapLifecycleResponse);
    }

    if (action === "resume") {
      return json({
        session: await connector.resumeSession(sessionId, accessToken),
      } satisfies NightcapLifecycleResponse);
    }

    const body =
      (await readJsonBody<NightcapLifecycleEndRequest>(request)) ?? {};
    return json({
      session: await connector.endSession(
        sessionId,
        accessToken,
        body as EndSessionRequest,
      ),
    } satisfies NightcapLifecycleResponse);
  } catch (error) {
    return new Response(
      error instanceof Error ? error.message : String(error),
      {
        status: 502,
      },
    );
  }
}

export async function proxySessionEvents(
  env: NightcapWorkerEnv,
  sessionId: string,
  request: Request,
): Promise<Response> {
  const url = new URL(
    `${env.ARCWRIGHT_API_BASE_URL}/v1/sessions/${sessionId}/events`,
  );
  const incoming = new URL(request.url);
  for (const [key, value] of incoming.searchParams.entries()) {
    url.searchParams.set(key, value);
  }

  const response = await fetch(url, {
    method: "GET",
    headers: request.headers.get("Authorization")
      ? { Authorization: request.headers.get("Authorization") as string }
      : {},
  });

  return new Response(response.body, {
    status: response.status,
    headers: {
      "content-type":
        response.headers.get("content-type") ?? "text/event-stream",
      "cache-control": "no-store",
    },
  });
}

function runtimeSessionId(url: URL): string {
  return url.searchParams.get("session_id") ?? "";
}

export default {
  async fetch(
    request: Request,
    env: NightcapWorkerEnv,
    _ctx: ExecutionContext,
  ): Promise<Response> {
    void _ctx;
    const url = new URL(request.url);
    const connector = connectorFor(env);

    if (request.method === "GET" && url.pathname === "/") {
      return html(renderLandingPage());
    }

    if (request.method === "GET" && url.pathname === "/host") {
      return html(renderHostPage(runtimeSessionId(url)));
    }

    if (request.method === "GET" && url.pathname === "/shared-display") {
      return html(renderSharedDisplayPage(runtimeSessionId(url)));
    }

    if (request.method === "POST" && url.pathname === "/bootstrap/session") {
      const denied = authorizeBootstrapSession(request, env);
      if (denied) {
        return denied;
      }

      const body = (await readJsonBody<CreateSessionRequest>(request)) ?? {};
      return bootstrapSession(connector, body);
    }

    if (
      request.method === "POST" &&
      url.pathname === "/host/api/bootstrap/session"
    ) {
      const body =
        (await readJsonBody<NightcapBootstrapRequest>(request)) ?? {};
      return createHostSession(connector, body);
    }

    if (
      request.method === "GET" &&
      url.pathname.startsWith("/host/api/sessions/") &&
      url.pathname.endsWith("/events")
    ) {
      const sessionId = parseSegment(url.pathname, 4);
      if (!sessionId) {
        return new Response("Not found", { status: 404 });
      }
      return proxySessionEvents(env, sessionId, request);
    }

    if (
      request.method === "GET" &&
      url.pathname.startsWith("/host/api/sessions/")
    ) {
      const sessionId = parseSegment(url.pathname, 4);
      if (!sessionId) {
        return new Response("Not found", { status: 404 });
      }
      return loadSession(connector, sessionId);
    }

    if (
      request.method === "POST" &&
      url.pathname.startsWith("/host/api/sessions/")
    ) {
      const sessionId = parseSegment(url.pathname, 4);
      const action = parseSegment(url.pathname, 5);
      if (
        !sessionId ||
        (action !== "start" &&
          action !== "pause" &&
          action !== "resume" &&
          action !== "end")
      ) {
        return new Response("Not found", { status: 404 });
      }
      return proxySessionLifecycle(connector, sessionId, action, request);
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
