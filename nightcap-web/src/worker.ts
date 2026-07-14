import {
  NightcapConnector,
  type CreateSessionRequest,
  type EndSessionRequest,
} from "./connector.js";
import {
  buildNightcapRuntimeUrls,
  buildNightcapPlayerJoinUrl,
  normalizePersonalizationIntake,
  type NightcapBootstrapRequest,
  type NightcapBootstrapResponse,
  type NightcapLifecycleEndRequest,
  type NightcapLifecycleResponse,
  type NightcapPlayerJoinRequest,
  type NightcapPlayerJoinResponse,
  type NightcapPlayerSlotResponse,
} from "./runtime.js";
import { NightcapRoom } from "./room.js";
import {
  renderHostPage,
  renderLandingPage,
  renderPlayerJoinPage,
  renderSharedDisplayPage,
} from "./ui.js";

export {
  renderHostPage,
  renderLandingPage,
  renderPlayerJoinPage,
  renderSharedDisplayPage,
};
export { NightcapRoom };

export interface NightcapWorkerEnv {
  ARCWRIGHT_API_BASE_URL: string;
  ARCWRIGHT_API_KEY: string;
  FIREBASE_SIGN_IN_URL?: string;
  // Referrer-restricted key embedded in the host sign-in page's client-side
  // Firebase config. Public by design — Firebase web config is meant to be
  // embedded in browser clients — but restricted to this Worker's own
  // authorized domains and to the Identity Toolkit / Secure Token APIs.
  FIREBASE_WEB_API_KEY: string;
  // Public Firebase client config for the host sign-in page. Not secret —
  // Firebase web config is designed to be embedded in browser clients.
  FIREBASE_AUTH_DOMAIN: string;
  FIREBASE_PROJECT_ID: string;
  // Separate, non-referrer-restricted key used ONLY server-side for the
  // custom-token -> ID-token exchange REST call. Never sent to the browser.
  // Worker Secret only — see docs/roadmap/operations/cloud-deploy-runbook.md.
  FIREBASE_TOKEN_EXCHANGE_API_KEY: string;
  // Comma-separated Firebase test phone numbers this rehearsal's host page
  // accepts. Not secret — enforced client-side alongside (not instead of)
  // the Firebase console's SMS region policy, so a code-level guard exists
  // even if that console setting is ever loosened or misconfigured.
  ALLOWED_TEST_PHONE_NUMBERS?: string;
  BOOTSTRAP_TOKEN: string;
  ROOMS: DurableObjectNamespace<NightcapRoom>;
  // Cloudflare static assets binding. Hosts the bundled mini-game module and
  // each mini-game definition JSON. Configured via wrangler.toml [assets].
  ASSETS?: Fetcher;
}

interface PlayerTokenExchangeRequest {
  player_token: string;
}

interface PlayerTokenExchangeResponse {
  player_token: string;
  expires_at: number;
}

interface HostTokenExchangeRequest {
  host_token: string;
}

interface HostTokenExchangeResponse {
  host_token: string;
  expires_at: number;
}

const DEFAULT_FIREBASE_SIGN_IN_URL =
  "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken";

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

async function readTextBody(request: Request): Promise<string | null> {
  try {
    return await request.text();
  } catch {
    return null;
  }
}

async function readJsonResponse<T>(response: Response): Promise<T | null> {
  try {
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

async function verifyHostSession(
  env: NightcapWorkerEnv,
  sessionId: string,
  accessToken: string,
): Promise<Response | null> {
  const response = await fetch(
    `${env.ARCWRIGHT_API_BASE_URL}/v1/sessions/${sessionId}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    },
  );

  if (response.ok) {
    return null;
  }

  const detail = (await response.text()).trim();
  return new Response(detail || "Host token rejected", {
    status: response.status,
  });
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

export async function createAuthenticatedHostSession(
  connector: NightcapConnector,
  body: NightcapBootstrapRequest,
  hostIdToken: string,
): Promise<Response> {
  const { personalization_intake, ...sessionBody } = body;
  const session = await connector.createHostSessionAuthenticated(
    sessionBody,
    hostIdToken,
  );
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

export async function createPlayerJoinLink(
  connector: NightcapConnector,
  env: NightcapWorkerEnv,
  sessionId: string,
  request: Request,
): Promise<Response> {
  const accessToken = readBearerToken(request);
  if (!accessToken) {
    return new Response("Authorization header required", { status: 401 });
  }

  try {
    const denied = await verifyHostSession(env, sessionId, accessToken);
    if (denied) {
      return denied;
    }

    const player = await connector.createPlayerSlot(sessionId);
    const runtime = buildNightcapRuntimeUrls(sessionId);
    return json({
      session_id: sessionId,
      player,
      runtime: {
        room_id: sessionId,
        ...runtime,
        player_url: buildNightcapPlayerJoinUrl(sessionId, player.join_token),
      },
    } satisfies NightcapPlayerSlotResponse);
  } catch (error) {
    console.error("Nightcap player join link creation failed", {
      sessionId,
      error: error instanceof Error ? error.message : String(error),
    });
    return new Response("Player join link creation failed", { status: 502 });
  }
}

async function registerJoinedPlayer(
  env: NightcapWorkerEnv,
  sessionId: string,
  player: NightcapPlayerJoinResponse["player"],
): Promise<void> {
  try {
    const room = env.ROOMS.get(env.ROOMS.idFromName(sessionId));
    await room.fetch(
      new Request(`https://nightcap-web.invalid/rooms/${sessionId}/join`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          client_id: player.player_id,
          participant_id: player.player_id,
          character_id: player.character_id,
          role: "player",
        }),
      }),
    );
  } catch (error) {
    console.warn("Nightcap room registration failed after join", {
      sessionId,
      error: error instanceof Error ? error.message : String(error),
    });
  }
}

export async function joinPlayerSession(
  connector: NightcapConnector,
  env: NightcapWorkerEnv,
  body: NightcapPlayerJoinRequest,
): Promise<Response> {
  const sessionId = body.session_id?.trim() ?? "";
  const joinToken = body.join_token?.trim() ?? "";
  if (!sessionId || !joinToken) {
    return new Response("Invalid join payload", { status: 400 });
  }

  try {
    const personalizationIntake = normalizePersonalizationIntake(
      body.personalization_intake,
    );
    const player = await connector.joinSession(
      sessionId,
      joinToken,
      personalizationIntake,
    );
    await registerJoinedPlayer(env, sessionId, player);

    return json({
      session_id: sessionId,
      player,
      runtime: {
        room_id: sessionId,
        ...buildNightcapRuntimeUrls(sessionId),
        player_url: buildNightcapPlayerJoinUrl(sessionId, joinToken),
      },
      personalization_intake: personalizationIntake,
    } satisfies NightcapPlayerJoinResponse);
  } catch (error) {
    console.error("Nightcap player join failed", {
      sessionId,
      error: error instanceof Error ? error.message : String(error),
    });
    return new Response("Player join failed", { status: 502 });
  }
}

interface CustomTokenExchangeResult {
  idToken: string;
  expiresAt: number;
}

/** Exchange a Firebase custom token (minted by the Arcwright API) for a
 * usable ID token via the Identity Toolkit REST API. Shared by both the
 * player join flow and the authenticated host flow — the Arcwright API
 * mints session-scoped custom tokens carrying an ``arcwright_role``
 * claim for both surfaces (see api/routers/sessions.py). */
async function exchangeCustomToken(
  env: NightcapWorkerEnv,
  customToken: string,
  logContext: Record<string, unknown>,
): Promise<CustomTokenExchangeResult | null> {
  const apiKey = env.FIREBASE_TOKEN_EXCHANGE_API_KEY.trim();
  if (!apiKey) {
    console.warn(
      "Nightcap token exchange failed: Firebase token-exchange API key is not configured",
      logContext,
    );
    return null;
  }

  const signInUrl =
    env.FIREBASE_SIGN_IN_URL?.trim() || DEFAULT_FIREBASE_SIGN_IN_URL;

  const response = await fetch(
    `${signInUrl}?key=${encodeURIComponent(apiKey)}`,
    {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({
        token: customToken,
        returnSecureToken: true,
      }),
    },
  );
  const data = await readJsonResponse<{
    idToken?: string;
    expiresIn?: string;
    error?: { message?: string };
  }>(response);

  if (!response.ok || !data?.idToken) {
    console.warn("Nightcap token exchange failed", {
      ...logContext,
      status: response.status,
      error: data?.error?.message ?? "missing idToken",
    });
    return null;
  }

  const expiresInSeconds = Number.parseInt(data.expiresIn ?? "0", 10);
  const expiresAt =
    Number.isFinite(expiresInSeconds) && expiresInSeconds > 0
      ? Date.now() + expiresInSeconds * 1000
      : Date.now() + 60 * 60 * 1000;

  return { idToken: data.idToken, expiresAt };
}

export async function exchangePlayerToken(
  env: NightcapWorkerEnv,
  sessionId: string,
  request: Request,
): Promise<Response> {
  const body = await readJsonBody<PlayerTokenExchangeRequest>(request);
  const playerToken = body?.player_token?.trim() ?? "";
  if (!playerToken) {
    return new Response("Invalid player token exchange payload", {
      status: 400,
    });
  }

  const result = await exchangeCustomToken(env, playerToken, { sessionId });
  if (!result) {
    return new Response("Player token exchange failed", { status: 502 });
  }

  return json({
    player_token: result.idToken,
    expires_at: result.expiresAt,
  } satisfies PlayerTokenExchangeResponse);
}

export async function exchangeHostToken(
  env: NightcapWorkerEnv,
  sessionId: string,
  request: Request,
): Promise<Response> {
  const body = await readJsonBody<HostTokenExchangeRequest>(request);
  const hostToken = body?.host_token?.trim() ?? "";
  if (!hostToken) {
    return new Response("Invalid host token exchange payload", {
      status: 400,
    });
  }

  const result = await exchangeCustomToken(env, hostToken, { sessionId });
  if (!result) {
    return new Response("Host token exchange failed", { status: 502 });
  }

  return json({
    host_token: result.idToken,
    expires_at: result.expiresAt,
  } satisfies HostTokenExchangeResponse);
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
    console.error("Arcwright lifecycle request failed", {
      action,
      sessionId,
      error: error instanceof Error ? error.message : String(error),
    });
    return new Response("Arcwright lifecycle request failed", {
      status: 502,
    });
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

export async function proxyPlayerCharacter(
  env: NightcapWorkerEnv,
  sessionId: string,
  characterId: string,
  request: Request,
): Promise<Response> {
  const accessToken = readBearerToken(request);
  if (!accessToken) {
    return new Response("Authorization header required", { status: 401 });
  }

  const url = new URL(
    `${env.ARCWRIGHT_API_BASE_URL}/v1/sessions/${sessionId}/characters/${characterId}`,
  );
  const response = await fetch(url, {
    method: request.method,
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return new Response(response.body, {
    status: response.status,
    headers: {
      "content-type":
        response.headers.get("content-type") ??
        "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

export async function proxyPlayerInput(
  env: NightcapWorkerEnv,
  sessionId: string,
  characterId: string,
  request: Request,
): Promise<Response> {
  const accessToken = readBearerToken(request);
  if (!accessToken) {
    return new Response("Authorization header required", { status: 401 });
  }

  const url = new URL(
    `${env.ARCWRIGHT_API_BASE_URL}/v1/sessions/${sessionId}/characters/${characterId}/input`,
  );
  const body = request.method === "POST" ? await readTextBody(request) : null;
  const response = await fetch(url, {
    method: request.method,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      ...(request.headers.get("content-type")
        ? { "content-type": request.headers.get("content-type") as string }
        : {}),
    },
    body,
  });

  return new Response(response.body, {
    status: response.status,
    headers: {
      "content-type":
        response.headers.get("content-type") ??
        "application/json; charset=utf-8",
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

    if (
      request.method === "GET" &&
      (url.pathname === "/mini-games.js" ||
        url.pathname.startsWith("/mini-games/definitions/"))
    ) {
      if (env.ASSETS) {
        return env.ASSETS.fetch(request);
      }
      // Cloudflare's [assets] binding intercepts these paths before the
      // worker fetch handler runs, so this 404 only fires in mis-configured
      // or local setups where the binding is absent.
      return new Response("Static assets are not configured", { status: 404 });
    }

    if (request.method === "GET" && url.pathname === "/") {
      return html(renderLandingPage());
    }

    if (request.method === "GET" && url.pathname === "/host") {
      return html(
        renderHostPage(runtimeSessionId(url), {
          apiKey: env.FIREBASE_WEB_API_KEY,
          authDomain: env.FIREBASE_AUTH_DOMAIN,
          projectId: env.FIREBASE_PROJECT_ID,
          allowedTestPhoneNumbers: (env.ALLOWED_TEST_PHONE_NUMBERS ?? "")
            .split(",")
            .map((number) => number.trim())
            .filter(Boolean),
        }),
      );
    }

    if (request.method === "GET" && url.pathname === "/shared-display") {
      return html(renderSharedDisplayPage(runtimeSessionId(url)));
    }

    if (request.method === "GET" && url.pathname === "/join") {
      return html(
        renderPlayerJoinPage(
          runtimeSessionId(url),
          url.searchParams.get("token") ?? "",
        ),
      );
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
      const denied = authorizeBootstrapSession(request, env);
      if (denied) {
        return denied;
      }

      const body =
        (await readJsonBody<NightcapBootstrapRequest>(request)) ?? {};
      return createHostSession(connector, body);
    }

    if (request.method === "POST" && url.pathname === "/host/api/session") {
      const hostIdToken = readBearerToken(request);
      if (!hostIdToken) {
        return new Response("Authorization header required", {
          status: 401,
        });
      }

      const body =
        (await readJsonBody<NightcapBootstrapRequest>(request)) ?? {};
      return createAuthenticatedHostSession(connector, body, hostIdToken);
    }

    if (
      request.method === "POST" &&
      url.pathname.startsWith("/host/api/sessions/") &&
      url.pathname.endsWith("/auth/exchange")
    ) {
      const sessionId = parseSegment(url.pathname, 4);
      if (!sessionId) {
        return new Response("Not found", { status: 404 });
      }
      return exchangeHostToken(env, sessionId, request);
    }

    if (
      request.method === "POST" &&
      url.pathname.startsWith("/host/api/sessions/") &&
      url.pathname.endsWith("/players")
    ) {
      const sessionId = parseSegment(url.pathname, 4);
      if (!sessionId) {
        return new Response("Not found", { status: 404 });
      }
      return createPlayerJoinLink(connector, env, sessionId, request);
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
      url.pathname.startsWith("/player/api/sessions/") &&
      url.pathname.endsWith("/events")
    ) {
      const sessionId = parseSegment(url.pathname, 4);
      if (!sessionId) {
        return new Response("Not found", { status: 404 });
      }
      return proxySessionEvents(env, sessionId, request);
    }

    if (
      request.method === "POST" &&
      url.pathname.startsWith("/player/api/sessions/") &&
      url.pathname.endsWith("/auth/exchange")
    ) {
      const sessionId = parseSegment(url.pathname, 4);
      if (!sessionId) {
        return new Response("Not found", { status: 404 });
      }
      return exchangePlayerToken(env, sessionId, request);
    }

    if (
      request.method === "GET" &&
      url.pathname.startsWith("/player/api/sessions/") &&
      /\/characters\/[^/]+$/.test(url.pathname)
    ) {
      const sessionId = parseSegment(url.pathname, 4);
      const characterId = parseSegment(url.pathname, 6);
      if (!sessionId || !characterId) {
        return new Response("Not found", { status: 404 });
      }
      return proxyPlayerCharacter(env, sessionId, characterId, request);
    }

    if (
      request.method === "POST" &&
      url.pathname.startsWith("/player/api/sessions/") &&
      /\/characters\/[^/]+\/input$/.test(url.pathname)
    ) {
      const sessionId = parseSegment(url.pathname, 4);
      const characterId = parseSegment(url.pathname, 6);
      if (!sessionId || !characterId) {
        return new Response("Not found", { status: 404 });
      }
      return proxyPlayerInput(env, sessionId, characterId, request);
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

    if (request.method === "POST" && url.pathname === "/join/api") {
      const body = (await readJsonBody<NightcapPlayerJoinRequest>(request)) ?? {
        session_id: "",
        join_token: "",
      };
      return joinPlayerSession(connector, env, body);
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
