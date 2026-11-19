const SIGN_IN_WITH_CUSTOM_TOKEN_URL =
  "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken";
const REFRESH_TOKEN_URL = "https://securetoken.googleapis.com/v1/token";

import { seatStore } from "./seatStore";

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

async function refreshAuthSession(
  gameId: string,
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
    // The sign-in was refused, so the stored seat cannot work again.
    if (response.status >= 400 && response.status < 500) {
      seatStore.clear(gameId);
    }
    throw new Error(data.error?.message ?? "Firebase token refresh failed.");
  }
  const refreshed = authSession(
    data.id_token,
    data.refresh_token,
    data.expires_in,
  );
  seatStore.updateAuth(gameId, refreshed);
  return refreshed;
}

// The phone's sign-in for one game, read from the stored seat.
export async function getValidPlayerToken(gameId: string): Promise<string> {
  const seat = seatStore.get(gameId);
  if (!seat) throw new Error("Authenticated session is not available.");
  if (seat.auth.expiresAt > Date.now() + 60_000) return seat.auth.idToken;
  return (await refreshAuthSession(gameId, seat.auth)).idToken;
}
