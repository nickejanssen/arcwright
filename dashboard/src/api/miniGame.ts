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

// Unauthenticated fetch for a player device, personalised by characterId.
// M4 pre-auth path — replaces ArcwrightClient.getMiniGameState() when no
// valid Firebase ID token is available. Production auth via JWT at M5 (AW-269).
export function fetchPlayerMiniGameState(
  sessionId: string,
  characterId: string,
): Promise<MiniGameState | null> {
  return _fetchDisplay(
    `/v1/sessions/${sessionId}/mini-games/active/display?character_id=${encodeURIComponent(characterId)}`,
  );
}
