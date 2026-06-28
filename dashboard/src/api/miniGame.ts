import type { MiniGameState } from "@arcwright/sdk";

// Unauthenticated mini-game state fetch for the shared display surface.
// Mirrors the response mapping in ArcwrightClient.getMiniGameState() but
// without an auth header, consistent with how the lobby endpoint is called.
export async function fetchDisplayMiniGameState(
  sessionId: string,
): Promise<MiniGameState | null> {
  let res: Response;
  try {
    res = await fetch(`/v1/sessions/${sessionId}/mini-games/active`);
  } catch {
    return null;
  }
  if (res.status === 404) return null;
  if (!res.ok) return null;
  const data = (await res.json()) as {
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
  };
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
