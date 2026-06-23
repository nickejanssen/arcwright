import { escapeHtml } from "./html.js";

export interface PersonalizationPrompt {
  readonly id: string;
  readonly label: string;
  readonly helperText: string;
  readonly placeholder: string;
  readonly required: boolean;
}

export const HOST_SEED_PROMPTS = [
  {
    id: "host_seed_1",
    label: "How familiar is this group with one another?",
    helperText: "A short phrase is enough.",
    placeholder: "New friends, mixed group, close circle",
    required: true,
  },
  {
    id: "host_seed_2",
    label: "What tone should tonight lean toward?",
    helperText: "Use the dominant mood you want the arc to carry.",
    placeholder: "Playful, tense, gothic, chaotic",
    required: true,
  },
  {
    id: "host_seed_3",
    label: "What group dynamic should we amplify?",
    helperText: "Tell us which social tension or energy to lean into.",
    placeholder: "Competitive, suspicious, cooperative",
    required: true,
  },
] as const satisfies readonly PersonalizationPrompt[];

export const PLAYER_JOIN_PROMPTS = [
  {
    id: "player_prompt_1",
    label: "What kind of role do you usually play in a group?",
    helperText: "Fast answer is fine.",
    placeholder: "Instigator, skeptic, peacekeeper",
    required: true,
  },
  {
    id: "player_prompt_2",
    label: "What kind of character energy do you want tonight?",
    helperText: "Optional, but helpful for fit.",
    placeholder: "Chaotic, charming, observant",
    required: false,
  },
] as const satisfies readonly PersonalizationPrompt[];

function renderPersonalizationPrompt(prompt: PersonalizationPrompt): string {
  const requiredSuffix = prompt.required
    ? ' <span class="pill">required</span>'
    : ' <span class="pill">optional</span>';
  return `<label class="prompt-card" for="${escapeHtml(prompt.id)}">
  <span class="prompt-title">${escapeHtml(prompt.label)}${requiredSuffix}</span>
  <input
    id="${escapeHtml(prompt.id)}"
    name="${escapeHtml(prompt.id)}"
    data-personalization-slot="${escapeHtml(prompt.id)}"
    type="text"
    placeholder="${escapeHtml(prompt.placeholder)}"
    ${prompt.required ? "required" : ""}
  />
  <span class="prompt-help">${escapeHtml(prompt.helperText)}</span>
</label>`;
}

export function renderPersonalizationPromptFields(
  prompts: readonly PersonalizationPrompt[],
): string {
  return `<div class="prompt-list">
${prompts.map(renderPersonalizationPrompt).join("\n")}
</div>`;
}
