// The engine routes the screens use that AW-331 built: this seat's role.
// (Pause and resume with a player's sign-in, the room view, and the join
// refusal are used by the screens directly through the routes they already
// call; only the role needed a place of its own.)
//
// Still missing on purpose: "Make someone else host" needs a name picker with
// words the founder has not yet reviewed, so it stays hidden until its own
// task builds it.

export type SeatRole = "host" | "player";

// Ask the engine whether this phone's seat is the host seat. The engine decides;
// anything this screen does not recognise, and any refusal or failure, is a
// plain player, so a mistake can never show a control the seat does not hold.
export async function fetchMyRole(
  sessionId: string,
  getToken: () => Promise<string>,
  fetcher: typeof fetch = fetch,
): Promise<SeatRole> {
  const token = await getToken();
  const res = await fetcher(
    `/v1/sessions/${encodeURIComponent(sessionId)}/me/seat`,
    { headers: { Authorization: `Bearer ${token}` } },
  );
  if (!res.ok) return "player";
  const body = (await res.json()) as { role?: unknown };
  return body.role === "host" ? "host" : "player";
}

// "Make someone else host" stays hidden until its follow-up task builds it.
export function handOverAvailable(): boolean {
  return false;
}
