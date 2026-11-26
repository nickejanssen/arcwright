export interface TheoryOption {
  value: string;
  label: string;
  text: string | null;
}
export interface TheoryForm {
  open: boolean;
  slots: Array<{ slot_id: string; label: string; options: TheoryOption[] }>;
  account: Array<{ text: string; slot_id: string | null }>;
  proof_options: TheoryOption[];
  theory: {
    state: "none" | "drafting" | "locked" | "no_theory";
    answers: Record<string, string>;
    proof: string | null;
    revision: number;
  };
}

// This player's own part of the result (GET /me/result). Refused until the
// engine has worked the result out.
export interface PrivateResult {
  state: "locked" | "no_theory";
  slots: Array<{ slot_id: string; label: string; right: boolean }>;
}

export function theoryApi(sessionId: string, getToken: () => Promise<string>) {
  const me = `/v1/sessions/${encodeURIComponent(sessionId)}/me`;
  async function request<T>(
    path: string,
    method: string,
    body?: unknown,
  ): Promise<T> {
    const token = await getToken();
    const response = await fetch(`${me}${path}`, {
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(body === undefined ? {} : { "Content-Type": "application/json" }),
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
    if (!response.ok) throw new Error("Request failed");
    return response.json() as Promise<T>;
  }
  return {
    read: () => request<TheoryForm>("/theory", "GET"),
    save: (answers: Record<string, string>, proof: string | null) =>
      request<TheoryForm["theory"]>("/theory", "PUT", { answers, proof }),
    lock: () => request<TheoryForm["theory"]>("/theory/lock", "POST"),
    result: () => request<PrivateResult>("/result", "GET"),
  };
}
