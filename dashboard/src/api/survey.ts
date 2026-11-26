// This seat's survey answers (GET and PUT /me/survey, AW-331). Private to the
// player; the TV never uses this file.

export type SurveyAnswers = Record<string, number | string>;

export interface SurveyReply {
  answered: boolean;
  answers: SurveyAnswers;
  comment: string | null;
}

export function surveyApi(sessionId: string, getToken: () => Promise<string>) {
  const url = `/v1/sessions/${encodeURIComponent(sessionId)}/me/survey`;
  async function request(method: string, body?: unknown): Promise<SurveyReply> {
    const token = await getToken();
    const response = await fetch(url, {
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(body === undefined ? {} : { "Content-Type": "application/json" }),
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
    if (!response.ok) throw new Error("Request failed");
    return response.json() as Promise<SurveyReply>;
  }
  return {
    read: () => request("GET"),
    save: (answers: SurveyAnswers, comment: string | null) =>
      request("PUT", { answers, comment }),
  };
}
