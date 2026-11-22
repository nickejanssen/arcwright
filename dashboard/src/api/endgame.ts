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

export function theoryApi(sessionId: string, getToken: () => Promise<string>) {
  const base = `/v1/sessions/${encodeURIComponent(sessionId)}/me/theory`;
  async function request<T>(
    path: string,
    method: string,
    body?: unknown,
  ): Promise<T> {
    const token = await getToken();
    const response = await fetch(`${base}${path}`, {
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
    read: () => request<TheoryForm>("", "GET"),
    save: (answers: Record<string, string>, proof: string | null) =>
      request<TheoryForm["theory"]>("", "PUT", { answers, proof }),
    lock: () => request<TheoryForm["theory"]>("/lock", "POST"),
  };
}
