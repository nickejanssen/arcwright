const SIGN_IN_WITH_CUSTOM_TOKEN_URL =
  "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken";
const REFRESH_TOKEN_URL = "https://securetoken.googleapis.com/v1/token";

interface FirebaseTokenExchangeResponse {
  idToken?: string;
  refreshToken?: string;
  expiresIn?: string;
  error?: { message?: string };
}

interface FirebaseRefreshResponse {
  id_token?: string;
  refresh_token?: string;
  expires_in?: string;
  error?: { message?: string };
}

export interface FirebaseAuthSession {
  idToken: string;
  refreshToken: string;
  expiresAt: number;
}

function webApiKey(): string {
  const apiKey = import.meta.env.VITE_FIREBASE_WEB_API_KEY?.trim();
  if (!apiKey) {
    throw new Error(
      "FIREBASE_WEB_API_KEY is not configured for this rehearsal.",
    );
  }
  return apiKey;
}

function authSession(
  idToken: string | undefined,
  refreshToken: string | undefined,
  expiresIn: string | undefined,
): FirebaseAuthSession {
  if (!idToken || !refreshToken || !expiresIn) {
    throw new Error("Firebase auth response is missing token lifetime data.");
  }
  return {
    idToken,
    refreshToken,
    expiresAt: Date.now() + Number(expiresIn) * 1000,
  };
}

export async function exchangeCustomToken(
  customToken: string,
): Promise<FirebaseAuthSession> {
  const response = await fetch(
    `${SIGN_IN_WITH_CUSTOM_TOKEN_URL}?key=${encodeURIComponent(webApiKey())}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: customToken, returnSecureToken: true }),
    },
  );
  const data = (await response.json()) as FirebaseTokenExchangeResponse;
  if (!response.ok) {
    throw new Error(data.error?.message ?? "Firebase sign-in failed.");
  }
  return authSession(data.idToken, data.refreshToken, data.expiresIn);
}

export const exchangePlayerToken = exchangeCustomToken;

const authKey = (kind: "player" | "host", sessionId: string) =>
  `arcwright.${kind}-auth.${sessionId}`;

function storeAuthSession(
  sessionId: string,
  kind: "player" | "host",
  auth: FirebaseAuthSession,
): void {
  sessionStorage.setItem(authKey(kind, sessionId), JSON.stringify(auth));
}

function loadAuthSession(
  sessionId: string,
  kind: "player" | "host",
): FirebaseAuthSession | null {
  const raw = sessionStorage.getItem(authKey(kind, sessionId));
  if (!raw) return null;
  try {
    return JSON.parse(raw) as FirebaseAuthSession;
  } catch {
    sessionStorage.removeItem(authKey(kind, sessionId));
    return null;
  }
}

export function storePlayerAuth(
  sessionId: string,
  auth: FirebaseAuthSession,
): void {
  storeAuthSession(sessionId, "player", auth);
}

export function loadPlayerAuth(sessionId: string): FirebaseAuthSession | null {
  return loadAuthSession(sessionId, "player");
}

export function storeHostAuth(
  sessionId: string,
  auth: FirebaseAuthSession,
): void {
  storeAuthSession(sessionId, "host", auth);
}

export function loadHostAuth(sessionId: string): FirebaseAuthSession | null {
  return loadAuthSession(sessionId, "host");
}

async function refreshAuthSession(
  sessionId: string,
  kind: "player" | "host",
  current: FirebaseAuthSession,
): Promise<FirebaseAuthSession> {
  const response = await fetch(
    `${REFRESH_TOKEN_URL}?key=${encodeURIComponent(webApiKey())}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `grant_type=refresh_token&refresh_token=${encodeURIComponent(current.refreshToken)}`,
    },
  );
  const data = (await response.json()) as FirebaseRefreshResponse;
  if (!response.ok) {
    throw new Error(data.error?.message ?? "Firebase token refresh failed.");
  }
  const refreshed = authSession(
    data.id_token,
    data.refresh_token,
    data.expires_in,
  );
  storeAuthSession(sessionId, kind, refreshed);
  return refreshed;
}

async function getValidAuthSession(
  sessionId: string,
  kind: "player" | "host",
): Promise<FirebaseAuthSession> {
  const auth = loadAuthSession(sessionId, kind);
  if (!auth) throw new Error("Authenticated session is not available.");
  if (auth.expiresAt > Date.now() + 60_000) return auth;
  return refreshAuthSession(sessionId, kind, auth);
}

export async function getValidPlayerToken(sessionId: string): Promise<string> {
  return (await getValidAuthSession(sessionId, "player")).idToken;
}

export async function getValidHostToken(sessionId: string): Promise<string> {
  return (await getValidAuthSession(sessionId, "host")).idToken;
}
