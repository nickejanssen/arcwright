// The one place that stands in for engine routes AW-331 has not built yet.
// When AW-331 lands, this file is the only one that changes.
//
// Missing today (checked in api/routers on main): a route that says whether
// this seat is the host; a player's sign-in on pause and resume; handing the
// host role on; the room view (who is ready, who paused); and refusing a join
// after the game has started with a named reason.

export type SeatRole = "host" | "player";

// Until the engine can say, every seat is a player. Tests pass the role in.
// AW-331 gives this the game to ask about.
export async function fetchMyRole(): Promise<SeatRole> {
  return "player";
}

// "Make someone else host" stays hidden until the engine has the route.
export function handOverAvailable(): boolean {
  return false;
}
