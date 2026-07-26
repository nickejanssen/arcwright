const SIGN_IN_WITH_CUSTOM_TOKEN_URL =
  "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken";

interface FirebaseTokenExchangeResponse {
  idToken?: string;
  error?: { message?: string };
}

export async function exchangePlayerToken(
  customToken: string,
): Promise<string> {
  const apiKey = import.meta.env.VITE_FIREBASE_WEB_API_KEY?.trim();
  if (!apiKey) {
    throw new Error(
      "FIREBASE_WEB_API_KEY is not configured for this rehearsal.",
    );
  }

  const response = await fetch(
    `${SIGN_IN_WITH_CUSTOM_TOKEN_URL}?key=${encodeURIComponent(apiKey)}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: customToken, returnSecureToken: true }),
    },
  );
  const data = (await response.json()) as FirebaseTokenExchangeResponse;
  if (!response.ok || !data.idToken) {
    throw new Error(data.error?.message ?? "Player sign-in failed.");
  }

  return data.idToken;
}

const playerTokenKey = (sessionId: string) =>
  `arcwright.player-token.${sessionId}`;

export function storePlayerToken(sessionId: string, token: string): void {
  sessionStorage.setItem(playerTokenKey(sessionId), token);
}

export function loadPlayerToken(sessionId: string): string | null {
  return sessionStorage.getItem(playerTokenKey(sessionId));
}
