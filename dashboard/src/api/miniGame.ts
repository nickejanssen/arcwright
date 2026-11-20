import type { MiniGameState } from "@arcwright/sdk";

function _parseMiniGameResponse(data: {
  run_id: string;
  game_id: string;
  mechanic_type: string | null;
  status: MiniGameState["status"];
  deadline_at: string | null;
  phase_state: MiniGameState["phaseState"];
  my_submissions: Array<{
    submission_id: string;
    is_accepted: boolean;
    rejection_reason?: string | null;
  }>;
}): MiniGameState {
  return {
    runId: data.run_id,
    gameId: data.game_id,
    mechanicType: data.mechanic_type,
    status: data.status,
    deadlineAt: data.deadline_at,
    phaseState: data.phase_state,
    mySubmissions: data.my_submissions.map((s) => ({
      submissionId: s.submission_id,
      isAccepted: s.is_accepted,
      rejectionReason: s.rejection_reason ?? undefined,
    })),
  };
}

async function _fetchDisplay(url: string): Promise<MiniGameState | null> {
  let res: Response;
  try {
    res = await fetch(url);
  } catch {
    return null;
  }
  if (res.status === 404) return null;
  if (!res.ok) return null;
  return _parseMiniGameResponse(
    (await res.json()) as Parameters<typeof _parseMiniGameResponse>[0],
  );
}

// Unauthenticated fetch for the shared display surface (no character context).
export function fetchDisplayMiniGameState(
  sessionId: string,
): Promise<MiniGameState | null> {
  return _fetchDisplay(`/v1/sessions/${sessionId}/mini-games/active/display`);
}

// Unauthenticated fetch that names a character. Since AW-331 (M4) the engine
// gives a player's own view only to a sign-in that owns the character, so with
// no sign-in this returns the shared view, the same as the display fetch above.
// Sending the seat's own sign-in is how a phone gets its personalised view.
export function fetchPlayerMiniGameState(
  sessionId: string,
  characterId: string,
): Promise<MiniGameState | null> {
  return _fetchDisplay(
    `/v1/sessions/${sessionId}/mini-games/active/display?character_id=${encodeURIComponent(characterId)}`,
  );
}
