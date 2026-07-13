import { SHARED_DISPLAY_VISIBLE_AUDIENCES } from "./filters.js";
import {
  HOST_SEED_PROMPTS,
  PLAYER_JOIN_PROMPTS,
  renderPersonalizationPromptFields,
} from "./personalization.js";
import { escapeHtml } from "./html.js";
import {
  buildNightcapPlayerSessionStorageKey,
  buildNightcapRuntimeUrls,
  isNightcapPlayerSessionExpired,
  normalizeNightcapPlayerSessionState,
} from "./runtime.js";
import {
  renderMiniGameScriptTag,
  renderMiniGameStage,
  renderMiniGameStageStyles,
} from "./mini-games/stage.js";
import type { ContentEvent, PresentationHints } from "./types.js";
import { renderDesignTokenCss, surfaceBodyClass } from "./design/index.js";
import type { SurfaceMode } from "./design/index.js";

function pageShell(title: string, body: string, surface?: SurfaceMode): string {
  const bodyClass = surfaceBodyClass(surface);
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${title}</title>
  <style>
    ${renderDesignTokenCss()}
    :root {
      font-family: var(--font-ui);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at 50% -10%, color-mix(in srgb, var(--theme-glow) 12%, transparent), transparent 42%),
        var(--stage-0);
      color: var(--ink-primary);
    }
    main {
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }
    .shell {
      display: grid;
      gap: var(--space-4);
    }
    .card {
      background: var(--stage-1-glass);
      border: 1px solid var(--line);
      border-radius: var(--radius-card);
      padding: var(--space-4);
      box-shadow: var(--shadow-stage);
      backdrop-filter: blur(16px);
    }
    .card-strong {
      margin: 0;
      background: var(--stage-2);
    }
    .card-inset {
      margin: 0 0 var(--space-3);
      background: var(--veil);
    }
    h1, h2, h3, p { margin-top: 0; }
    h1 {
      font-family: var(--font-display);
      font-weight: 600;
      letter-spacing: 0.01em;
      font-size: var(--type-title);
      margin-bottom: var(--space-2);
    }
    h2 { font-size: var(--type-heading); margin-bottom: 10px; }
    p, label, button, input, textarea, select, summary {
      font: inherit;
    }
    p { font-size: var(--type-body); }
    label { display: grid; gap: var(--space-2); margin-bottom: var(--space-3); color: var(--ink-muted); }
    input, textarea, select, button {
      border-radius: var(--radius-control);
      border: 1px solid var(--line);
      background: var(--veil);
      color: var(--ink-primary);
      padding: 12px 14px;
    }
    textarea { min-height: 120px; resize: vertical; }
    button {
      cursor: pointer;
      font-weight: 650;
      background: linear-gradient(135deg, color-mix(in srgb, var(--theme-glow) 16%, transparent), color-mix(in srgb, var(--theme-glow) 6%, transparent));
      transition: border-color var(--t-quick), background-color var(--t-quick);
    }
    button:hover { border-color: color-mix(in srgb, var(--theme-glow) 45%, transparent); }
    .grid {
      display: grid;
      gap: 16px;
    }
    .grid.two {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    .muted { color: var(--ink-muted); }
    .status {
      padding: 10px 12px;
      border-radius: var(--radius-control);
      background: color-mix(in srgb, var(--theme-glow) 7%, transparent);
      border: 1px solid color-mix(in srgb, var(--theme-glow) 22%, transparent);
      color: var(--theme-glow);
      white-space: pre-wrap;
    }
    .status.error {
      background: color-mix(in srgb, var(--accuse) 10%, transparent);
      border-color: color-mix(in srgb, var(--accuse) 30%, transparent);
      color: var(--accuse);
    }
    .event-feed {
      display: grid;
      gap: 12px;
    }
    .event {
      border: 1px solid var(--line);
      background: var(--veil);
      border-radius: 14px;
      padding: 14px;
    }
    .event-header {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      justify-content: space-between;
    }
    .event strong {
      color: var(--theme-glow);
      text-transform: capitalize;
    }
    .event-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
      color: var(--ink-muted);
      font-size: var(--type-detail);
    }
    .event-body {
      margin: 10px 0 0;
      white-space: pre-wrap;
      word-break: break-word;
      color: var(--ink-primary);
      font-size: var(--type-body);
    }
    .hint-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
    }
    .hint-pill {
      display: inline-flex;
      align-items: center;
      border-radius: var(--radius-pill);
      border: 1px solid color-mix(in srgb, var(--theme-glow) 24%, transparent);
      padding: 4px 10px;
      color: var(--theme-glow);
      background: var(--veil);
      font-size: 0.82rem;
    }
    .pill {
      display: inline-block;
      margin-left: 8px;
      padding: 2px 8px;
      border-radius: var(--radius-pill);
      border: 1px solid var(--line);
      color: var(--ink-muted);
      font-size: 0.8rem;
      vertical-align: middle;
    }
    .prompt-list {
      display: grid;
      gap: 12px;
    }
    .prompt-card {
      display: grid;
      gap: 8px;
      margin: 0;
      padding: 14px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: var(--veil);
    }
    .prompt-title {
      color: var(--ink-primary);
      font-weight: 650;
    }
    .prompt-help {
      color: var(--ink-muted);
      font-size: 0.92rem;
      line-height: 1.35;
    }
    .surface-stack {
      display: grid;
      gap: 12px;
    }
    .surface-panel {
      border: 1px solid var(--line);
      border-radius: 14px;
      background: var(--veil);
      padding: 14px;
    }
    .surface-title {
      margin-bottom: 4px;
      font-size: var(--type-body);
      color: var(--ink-primary);
    }
    .surface-detail {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      color: var(--ink-muted);
    }
    .surface-feed {
      display: grid;
      gap: 12px;
    }
    .surface-input {
      display: grid;
      gap: 12px;
    }
    .surface-input .actions {
      justify-content: flex-start;
    }
    .hide { display: none; }
    @media (max-width: 900px) {
      .grid.two { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body${bodyClass ? ` class="${bodyClass}"` : ""}>
  <main>${body}</main>
</body>
</html>`;
}

const SHARED_DISPLAY_UNKNOWN_PLACEHOLDER = "A private event was shared.";

export function getSharedDisplayEventBody(
  event: Pick<ContentEvent, "payload" | "event_type">,
): string {
  const payload = event.payload;
  if (typeof payload === "string") {
    return payload;
  }

  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return SHARED_DISPLAY_UNKNOWN_PLACEHOLDER;
  }

  const fields = ["text", "message", "summary", "description"] as const;
  for (const field of fields) {
    const value = payload[field];
    if (typeof value === "string" && value.trim().length > 0) {
      return value;
    }
  }

  return SHARED_DISPLAY_UNKNOWN_PLACEHOLDER;
}

export function getPlayerEventBody(
  event: Pick<ContentEvent, "payload" | "event_type">,
): string {
  const payload = event.payload;
  if (typeof payload === "string") {
    return payload;
  }

  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return JSON.stringify(payload, null, 2);
  }

  const fields = ["text", "message", "summary", "description"] as const;
  for (const field of fields) {
    const value = payload[field];
    if (typeof value === "string" && value.trim().length > 0) {
      return value;
    }
  }

  // Player-private surfaces render the full structured payload intentionally.
  return JSON.stringify(payload, null, 2);
}

export function getPlayerEventLabel(
  event: Pick<ContentEvent, "category" | "event_type">,
): string {
  const label = event.event_type.replaceAll("_", " ").trim();
  return label.length > 0 ? label : event.category.replaceAll("_", " ");
}

export function getSharedDisplayEventLabel(
  event: Pick<ContentEvent, "category" | "event_type">,
): string {
  const label = event.event_type.replaceAll("_", " ").trim();
  return label.length > 0 ? label : event.category.replaceAll("_", " ");
}

export function getSharedDisplayPresentationHintTokens(
  hints: PresentationHints,
): string[] {
  const tokens: string[] = [];

  if (hints.emotion) {
    tokens.push(`emotion: ${hints.emotion}`);
  }
  if (hints.urgency) {
    tokens.push(`urgency: ${hints.urgency}`);
  }
  if (hints.voice_hint) {
    tokens.push(`voice: ${hints.voice_hint}`);
  }
  if (hints.animation_hint) {
    tokens.push(`animation: ${hints.animation_hint}`);
  }
  if (hints.lighting_hint) {
    tokens.push(`lighting: ${hints.lighting_hint}`);
  }
  if (hints.pause_before_ms > 0) {
    tokens.push(`pause: ${hints.pause_before_ms}ms`);
  }

  return tokens;
}

export function renderLandingPage(): string {
  return pageShell(
    "Nightcap Runtime",
    `<section class="shell">
      <div class="card">
        <h1>Nightcap web runtime</h1>
        <p class="muted">Host controls and shared-display playback over Arcwright lifecycle APIs.</p>
        <div class="actions">
          <a href="/host">Host controls</a>
          <a href="/shared-display">Shared display</a>
          <a href="/join">Player join</a>
        </div>
      </div>
    </section>`,
  );
}

export function renderHostPage(sessionId = ""): string {
  const urls = buildNightcapRuntimeUrls(sessionId || "session");
  return pageShell(
    "Nightcap Host Controls",
    `<section class="shell">
      <div class="card">
        <h1>Host controls</h1>
        <p class="muted">Creates sessions and forwards lifecycle actions to Arcwright. The browser does not own session state.</p>
        <div class="grid two">
          <form id="bootstrap-form" class="card card-strong">
            <h2>Create session</h2>
            <label>
              Arc ID
              <input id="arc-id" name="arc_id" value="nightcap-v1" />
            </label>
            <label>
              Quality tier
              <select id="quality-tier" name="quality_tier">
                <option value="standard" selected>standard</option>
                <option value="premium">premium</option>
              </select>
            </label>
            <div class="card card-inset">
              <h3>Group personalization</h3>
              <p class="muted">Three short answers seed character fit and narrator callbacks.</p>
              ${renderPersonalizationPromptFields(HOST_SEED_PROMPTS)}
            </div>
            <button type="submit">Create session</button>
          </form>

          <div class="card card-strong">
            <h2>Session state</h2>
            <div id="host-status" class="status">No session created yet.</div>
            <label>
              Session ID
              <input id="session-id" placeholder="session UUID" value="${escapeHtml(
                sessionId,
              )}" />
            </label>
            <label>
              Host bearer token
              <input id="host-token" placeholder="Bearer token from Arcwright" />
            </label>
            <label>
              End completion type
              <select id="completion-type">
                <option value="full_arc" selected>full_arc</option>
                <option value="interrupted">interrupted</option>
                <option value="abandoned">abandoned</option>
              </select>
            </label>
            <label>
              Killer identified
              <select id="killer-identified">
                <option value="false" selected>false</option>
                <option value="true">true</option>
              </select>
            </label>
            <div class="actions">
              <button data-action="start" type="button">Start</button>
              <button data-action="pause" type="button">Pause</button>
              <button data-action="resume" type="button">Resume</button>
              <button data-action="end" type="button">End</button>
              <button id="create-player-link" type="button">Create player join link</button>
              <button id="refresh-session" type="button">Refresh</button>
            </div>
          </div>
        </div>
      </div>
      <div class="card">
        <h2>Bootstrap response</h2>
        <pre id="bootstrap-output" class="status">Waiting for session bootstrap.</pre>
      </div>
      <div class="card">
        <h2>Runtime URLs</h2>
        <pre id="runtime-output" class="status">${JSON.stringify(urls, null, 2)}</pre>
      </div>
      <div class="card">
        <h2>Player join link</h2>
        <pre id="player-link-output" class="status">No player join link created yet.</pre>
      </div>
      ${renderMiniGameStage("host")}
    </section>
    ${renderMiniGameStageStyles()}
    ${renderMiniGameScriptTag()}
    <script>
      (function() {
        const bootstrapForm = document.getElementById('bootstrap-form');
        const bootstrapOutput = document.getElementById('bootstrap-output');
        const runtimeOutput = document.getElementById('runtime-output');
        const playerLinkOutput = document.getElementById('player-link-output');
        const hostStatus = document.getElementById('host-status');
        const sessionIdInput = document.getElementById('session-id');
        const hostTokenInput = document.getElementById('host-token');
        const arcIdInput = document.getElementById('arc-id');
        const qualityTierInput = document.getElementById('quality-tier');
        const completionTypeInput = document.getElementById('completion-type');
        const killerIdentifiedInput = document.getElementById('killer-identified');
        const createPlayerLinkButton = document.getElementById('create-player-link');
        const refreshSessionButton = document.getElementById('refresh-session');

        function setStatus(message, isError) {
          hostStatus.textContent = message;
          hostStatus.className = isError ? 'status error' : 'status';
        }

        function readPersonalizationIntake(form) {
          const payload = {};
          form.querySelectorAll('[data-personalization-slot]').forEach(function(field) {
            const key = field.getAttribute('data-personalization-slot');
            const value = field.value.trim();
            if (key && value) {
              payload[key] = value;
            }
          });
          return payload;
        }

        async function readJson(response) {
          const text = await response.text();
          return text ? JSON.parse(text) : null;
        }

        bootstrapForm.addEventListener('submit', async function(event) {
          event.preventDefault();
          try {
            setStatus('Creating session...', false);
            const payload = {
              arc_id: arcIdInput.value.trim(),
              quality_tier: qualityTierInput.value,
              personalization_intake: readPersonalizationIntake(bootstrapForm),
            };
            const response = await fetch('/host/api/bootstrap/session', {
              method: 'POST',
              headers: { 'content-type': 'application/json' },
              body: JSON.stringify(payload),
            });
            const data = await readJson(response);
            if (!response.ok) {
              throw new Error((data && data.detail) || 'Session bootstrap failed.');
            }
            sessionIdInput.value = data.session.session_id;
            hostTokenInput.value = data.session.host_token;
            bootstrapOutput.textContent = JSON.stringify(data, null, 2);
            runtimeOutput.textContent = JSON.stringify(data.runtime, null, 2);
            setStatus('Session created.', false);
          } catch (error) {
            setStatus(error.message || String(error), true);
          }
        });

        async function sendControl(action) {
          const sessionId = sessionIdInput.value.trim();
          const hostToken = hostTokenInput.value.trim();
          if (!sessionId) {
            throw new Error('Create or paste a session id first.');
          }
          if (!hostToken) {
            throw new Error('Paste a host bearer token first.');
          }

          const init = {
            method: 'POST',
            headers: {
              'authorization': 'Bearer ' + hostToken,
              'content-type': 'application/json',
            },
            body: action === 'end' ? JSON.stringify({
              completion_type: completionTypeInput.value,
              killer_identified: killerIdentifiedInput.value === 'true',
            }) : '{}',
          };

          const response = await fetch('/host/api/sessions/' + encodeURIComponent(sessionId) + '/' + action, init);
          const data = await readJson(response);
          if (!response.ok) {
            throw new Error((data && data.detail) || action + ' failed.');
          }
          bootstrapOutput.textContent = JSON.stringify(data, null, 2);
          setStatus(action + ' completed.', false);
        }

        async function createPlayerJoinLink() {
          const sessionId = sessionIdInput.value.trim();
          const hostToken = hostTokenInput.value.trim();
          if (!sessionId) {
            throw new Error('Create or paste a session id first.');
          }
          if (!hostToken) {
            throw new Error('Paste a host bearer token first.');
          }

          const response = await fetch('/host/api/sessions/' + encodeURIComponent(sessionId) + '/players', {
            method: 'POST',
            headers: {
              'authorization': 'Bearer ' + hostToken,
              'content-type': 'application/json',
            },
          });
          const data = await readJson(response);
          if (!response.ok) {
            throw new Error((data && data.detail) || 'Player join link creation failed.');
          }

          playerLinkOutput.textContent = JSON.stringify(data, null, 2);
          setStatus('Player join link created.', false);
        }

        document.querySelectorAll('button[data-action]').forEach(function(button) {
          button.addEventListener('click', async function() {
            try {
              await sendControl(button.getAttribute('data-action'));
            } catch (error) {
              setStatus(error.message || String(error), true);
            }
          });
        });

        createPlayerLinkButton.addEventListener('click', async function() {
          try {
            await createPlayerJoinLink();
          } catch (error) {
            setStatus(error.message || String(error), true);
          }
        });

        refreshSessionButton.addEventListener('click', async function() {
          try {
            const sessionId = sessionIdInput.value.trim();
            if (!sessionId) {
              throw new Error('Create or paste a session id first.');
            }
            const response = await fetch('/host/api/sessions/' + encodeURIComponent(sessionId));
            const data = await readJson(response);
            if (!response.ok) {
              throw new Error((data && data.detail) || 'Session load failed.');
            }
            bootstrapOutput.textContent = JSON.stringify(data, null, 2);
            setStatus('Session refreshed.', false);
          } catch (error) {
            setStatus(error.message || String(error), true);
          }
        });
      })();
    </script>`,
  );
}

export function renderSharedDisplayPage(sessionId = ""): string {
  const urls = buildNightcapRuntimeUrls(sessionId || "session");
  return pageShell(
    "Nightcap Shared Display",
    `<section class="shell">
      <div class="card">
        <h1>Shared display</h1>
        <p class="muted">Only public or shared-display events are rendered here.</p>
        <div class="grid two">
          <div class="card card-strong">
            <h2>Connection</h2>
            <label>
              Session ID
              <input id="display-session-id" value="${escapeHtml(
                sessionId,
              )}" placeholder="session UUID" />
            </label>
            <label>
              Bearer token
              <input id="display-token" placeholder="display or host token" />
            </label>
            <div class="actions">
              <button id="connect-button" type="button">Connect</button>
              <button id="disconnect-button" type="button">Disconnect</button>
            </div>
            <div id="display-status" class="status">Disconnected.</div>
          </div>
          <div class="card card-strong">
            <h2>Runtime URLs</h2>
            <pre class="status">${JSON.stringify(urls, null, 2)}</pre>
          </div>
        </div>
      </div>
      <div class="card">
        <h2>Visible events</h2>
        <div id="event-feed" class="event-feed"></div>
      </div>
      ${renderMiniGameStage("shared_display")}
    </section>
    ${renderMiniGameStageStyles()}
    ${renderMiniGameScriptTag()}
    <script>
      (function() {
        const sharedDisplayVisibleAudiences = ${JSON.stringify(
          SHARED_DISPLAY_VISIBLE_AUDIENCES,
        )};
        const getSharedDisplayEventBody = ${getSharedDisplayEventBody.toString()};
        const getSharedDisplayEventLabel = ${getSharedDisplayEventLabel.toString()};
        const getSharedDisplayPresentationHintTokens = ${getSharedDisplayPresentationHintTokens.toString()};
        const sessionIdInput = document.getElementById('display-session-id');
        const tokenInput = document.getElementById('display-token');
        const connectButton = document.getElementById('connect-button');
        const disconnectButton = document.getElementById('disconnect-button');
        const status = document.getElementById('display-status');
        const eventFeed = document.getElementById('event-feed');
        const state = { reader: null, active: false, since: 0 };

        function setStatus(message, isError) {
          status.textContent = message;
          status.className = isError ? 'status error' : 'status';
        }

        function shouldRender(event) {
          return sharedDisplayVisibleAudiences.includes(event.target_audience);
        }

        function renderHintTokens(hints) {
          const tokens = getSharedDisplayPresentationHintTokens(hints);
          if (!tokens.length) {
            return null;
          }

          const hintRow = document.createElement('div');
          hintRow.className = 'hint-row';
          tokens.forEach(function(token) {
            const pill = document.createElement('span');
            pill.className = 'hint-pill';
            pill.textContent = token;
            hintRow.appendChild(pill);
          });
          return hintRow;
        }

        function renderEvent(event) {
          const card = document.createElement('article');
          card.className = 'event';

          const header = document.createElement('div');
          header.className = 'event-header';

          const title = document.createElement('strong');
          title.textContent = getSharedDisplayEventLabel(event);

          const sequence = document.createElement('span');
          sequence.className = 'pill';
          sequence.textContent = '#' + String(event.sequence_number);

          header.appendChild(title);
          header.appendChild(sequence);

          const meta = document.createElement('div');
          meta.className = 'event-meta';

          const category = document.createElement('span');
          category.textContent = String(event.category).replace(/_/g, ' ');
          meta.appendChild(category);

          const timestamp = document.createElement('span');
          timestamp.textContent = new Date(event.timestamp).toLocaleString();
          meta.appendChild(timestamp);

          const body = document.createElement('div');
          body.className = 'event-body';
          body.textContent = getSharedDisplayEventBody(event);

          const hintRow = renderHintTokens(event.presentation_hints);

          card.appendChild(header);
          card.appendChild(meta);
          card.appendChild(body);
          if (hintRow) {
            card.appendChild(hintRow);
          }

          eventFeed.prepend(card);
        }

        function parseBlock(block) {
          const dataLines = [];
          block.split('\\n').forEach(function(line) {
            if (line.startsWith('data:')) {
              dataLines.push(line.slice(5).replace(/^\\s/, ''));
            }
          });
          if (!dataLines.length) {
            return;
          }
          try {
            const event = JSON.parse(dataLines.join('\\n'));
            state.since = Math.max(state.since, event.sequence_number || 0);
            if (shouldRender(event)) {
              renderEvent(event);
            }
          } catch (error) {
            setStatus('Malformed event payload received.', true);
          }
        }

        async function disconnect() {
          state.active = false;
          if (state.reader) {
            try {
              await state.reader.cancel();
            } catch (error) {
              void error;
            }
            state.reader = null;
          }
          setStatus('Disconnected.', false);
        }

        async function connect() {
          const sessionId = sessionIdInput.value.trim();
          const token = tokenInput.value.trim();
          if (!sessionId) {
            throw new Error('Session id is required.');
          }
          if (!token) {
            throw new Error('Bearer token is required.');
          }
          await disconnect();
          state.active = true;
          setStatus('Connecting...', false);
          const response = await fetch('/host/api/sessions/' + encodeURIComponent(sessionId) + '/events?since=' + state.since, {
            headers: {
              'authorization': 'Bearer ' + token,
            },
          });
          if (!response.ok || !response.body) {
            throw new Error('Event stream failed with ' + response.status + '.');
          }
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let buffer = '';
          state.reader = reader;
          setStatus('Connected.', false);
          while (state.active) {
            const chunk = await reader.read();
            if (chunk.done) {
              break;
            }
            buffer += decoder.decode(chunk.value, { stream: true });
            buffer = buffer.replace(/\\r\\n/g, '\\n').replace(/\\r/g, '\\n');
            const blocks = buffer.split('\\n\\n');
            buffer = blocks.pop() || '';
            blocks.forEach(parseBlock);
          }
          await disconnect();
        }

        connectButton.addEventListener('click', function() {
          connect().catch(function(error) {
            setStatus(error.message || String(error), true);
          });
        });

        disconnectButton.addEventListener('click', function() {
          disconnect().catch(function(error) {
            setStatus(error.message || String(error), true);
          });
        });
      })();
    </script>`,
    "display",
  );
}

export function renderPlayerJoinPage(sessionId = "", joinToken = ""): string {
  return pageShell(
    "Nightcap Player Join",
    `<section class="shell">
      <div class="card">
        <h1>Join Nightcap</h1>
        <p class="muted">Join with the QR link or the join code from the host. No account or app install required. Private events stay on your device. Input stays on your device too.</p>
        <div class="grid two">
          <div class="card card-strong">
            <h2>Join code</h2>
            <form id="player-join-form">
              <label>
                Session ID
                <input id="join-session-id" placeholder="session UUID" value="${escapeHtml(
                  sessionId,
                )}" />
              </label>
              <label>
                Join token
                <input id="join-token" placeholder="join code or QR token" value="${escapeHtml(
                  joinToken,
                )}" />
              </label>
              <div class="card card-inset">
                <h2>Quick personalization</h2>
                <p class="muted">Answer one required question and one optional follow-up so Arcwright can fit your character.</p>
                ${renderPersonalizationPromptFields(PLAYER_JOIN_PROMPTS)}
              </div>
              <div class="actions">
                <button id="join-button" type="submit">Join</button>
              </div>
            </form>
            <div id="player-status" class="status">Waiting for a join code.</div>
          </div>
          <div class="card card-strong">
            <h2>Your surface</h2>
            <div id="player-surface" class="surface-stack">
              <section class="surface-panel">
                <h3 class="surface-title" id="player-character-title">No character assigned yet.</h3>
                <pre id="player-character-detail" class="surface-detail">Join to load your private character context.</pre>
              </section>
              <form id="player-input-form" class="surface-panel surface-input">
                <h3 class="surface-title">Send input</h3>
                <label>
                  Input type
                  <select id="player-input-kind">
                    <option value="action" selected>action</option>
                    <option value="dialogue">dialogue</option>
                  </select>
                </label>
                <label>
                  Message
                  <textarea id="player-input-content" placeholder="What do you do or say next?" disabled></textarea>
                </label>
                <div class="actions">
                  <button id="player-input-submit" type="submit" disabled>Send</button>
                  <button id="player-feed-retry" type="button" disabled>Retry feed</button>
                </div>
              </form>
              <section class="surface-panel">
                <h3 class="surface-title">Private feed</h3>
                <div id="player-event-feed" class="surface-feed"></div>
              </section>
            </div>
          </div>
        </div>
      </div>
      ${renderMiniGameStage("phone")}
    </section>
    ${renderMiniGameStageStyles()}
    ${renderMiniGameScriptTag()}
    <script>
      (function() {
        const buildPlayerSessionStorageKey = ${buildNightcapPlayerSessionStorageKey.toString()};
        const normalizePlayerSessionState = ${normalizeNightcapPlayerSessionState.toString()};
        const isNightcapPlayerSessionExpired = ${isNightcapPlayerSessionExpired.toString()};
        const getPlayerEventBody = ${getPlayerEventBody.toString()};
        const getPlayerEventLabel = ${getPlayerEventLabel.toString()};
        const joinForm = document.getElementById('player-join-form');
        const sessionIdInput = document.getElementById('join-session-id');
        const joinTokenInput = document.getElementById('join-token');
        const status = document.getElementById('player-status');
        const playerCharacterTitle = document.getElementById('player-character-title');
        const playerCharacterDetail = document.getElementById('player-character-detail');
        const playerInputForm = document.getElementById('player-input-form');
        const playerInputKind = document.getElementById('player-input-kind');
        const playerInputContent = document.getElementById('player-input-content');
        const playerInputSubmit = document.getElementById('player-input-submit');
        const playerFeedRetry = document.getElementById('player-feed-retry');
        const playerEventFeed = document.getElementById('player-event-feed');
        const activeSessionStorageKey = 'nightcap.player.active_session_id';
        const state = {
          active: false,
          reader: null,
          reconnectAttempts: 0,
          session: null,
          since: 0,
        };

        function setStatus(message, isError) {
          status.textContent = message;
          status.className = isError ? 'status error' : 'status';
        }

        function readStoredSession(sessionId) {
          const raw = sessionStorage.getItem(buildPlayerSessionStorageKey(sessionId));
          if (!raw) {
            return null;
          }

          try {
            return normalizePlayerSessionState(JSON.parse(raw));
          } catch {
            return null;
          }
        }

        function readActiveSession() {
          const sessionId = sessionStorage.getItem(activeSessionStorageKey);
          if (!sessionId) {
            return null;
          }

          return readStoredSession(sessionId);
        }

        function persistSession(session) {
          sessionStorage.setItem(activeSessionStorageKey, session.session_id);
          sessionStorage.setItem(
            buildPlayerSessionStorageKey(session.session_id),
            JSON.stringify(session),
          );
        }

        function rememberSequenceNumber(sequenceNumber) {
          if (!state.session) {
            return;
          }

          state.since = Math.max(state.since, sequenceNumber || 0);
          persistSession({
            session_id: state.session.session_id,
            player_id: state.session.player_id,
            character_id: state.session.character_id,
            player_token: state.session.player_token,
            expires_at: state.session.expires_at,
            last_sequence_number: state.since,
          });
        }

        function readPersonalizationIntake(form) {
          const payload = {};
          form.querySelectorAll('[data-personalization-slot]').forEach(function(field) {
            const key = field.getAttribute('data-personalization-slot');
            const value = field.value.trim();
            if (key && value) {
              payload[key] = value;
            }
          });
          return payload;
        }

        async function readJson(response) {
          const text = await response.text();
          return text ? JSON.parse(text) : null;
        }

        async function exchangeJoinTokenForBearerToken(sessionId, playerToken) {
          const response = await fetch(
            '/player/api/sessions/' +
              encodeURIComponent(sessionId) +
              '/auth/exchange',
            {
              method: 'POST',
              headers: {
                'content-type': 'application/json',
              },
              body: JSON.stringify({
                player_token: playerToken,
              }),
            },
          );
          const data = await readJson(response);
          if (!response.ok) {
            throw new Error((data && data.detail) || 'Player sign-in failed.');
          }

          if (
            !data ||
            typeof data.player_token !== 'string' ||
            typeof data.expires_at !== 'number'
          ) {
            throw new Error('Player sign-in failed.');
          }

          return {
            player_token: data.player_token,
            expires_at: data.expires_at,
          };
        }

        function sessionHeaders(includeContentType) {
          if (!state.session) {
            return {};
          }

          return {
            authorization: 'Bearer ' + state.session.player_token,
            ...(includeContentType ? { 'content-type': 'application/json' } : {}),
          };
        }

        function clearFeed() {
          playerEventFeed.textContent = '';
        }

        function renderPlayerCharacter(character) {
          playerCharacterTitle.textContent = 'Character ' + character.character_id;
          playerCharacterDetail.textContent = [
            'Private character loaded.',
            'Surface: ' + character.surface_type,
            'Your private feed and input stay on this device.',
          ].join('\\n');
        }

        function renderPlayerEvent(event) {
          const card = document.createElement('article');
          card.className = 'event';

          const header = document.createElement('div');
          header.className = 'event-header';

          const title = document.createElement('strong');
          title.textContent = getPlayerEventLabel(event);

          const sequence = document.createElement('span');
          sequence.className = 'pill';
          sequence.textContent = '#' + String(event.sequence_number);

          header.appendChild(title);
          header.appendChild(sequence);

          const meta = document.createElement('div');
          meta.className = 'event-meta';

          const category = document.createElement('span');
          category.textContent = String(event.category).replace(/_/g, ' ');
          meta.appendChild(category);

          const timestamp = document.createElement('span');
          timestamp.textContent = new Date(event.timestamp).toLocaleString();
          meta.appendChild(timestamp);

          const body = document.createElement('div');
          body.className = 'event-body';
          body.textContent = getPlayerEventBody(event);

          card.appendChild(header);
          card.appendChild(meta);
          card.appendChild(body);
          playerEventFeed.prepend(card);
        }

        function parseSseBlock(block) {
          const dataLines = [];
          block.split('\\n').forEach(function(line) {
            if (line.startsWith('data:')) {
              dataLines.push(line.slice(5).replace(/^\\s/, ''));
            }
          });

          if (!dataLines.length) {
            return;
          }

          try {
            const event = JSON.parse(dataLines.join('\\n'));
            rememberSequenceNumber(event.sequence_number);
            renderPlayerEvent(event);
          } catch {
            setStatus('Malformed private event received.', true);
          }
        }

        async function disconnectPlayerStream() {
          state.active = false;
          if (state.reader) {
            try {
              await state.reader.cancel();
            } catch (error) {
              void error;
            }
            state.reader = null;
          }
        }

        async function sleep(ms) {
          return await new Promise(function(resolve) {
            setTimeout(resolve, ms);
          });
        }

        function retryDelayFor(attempt) {
          return attempt < 8 ? 250 * Math.pow(2, attempt) : null;
        }

        async function retryPlayerFeed() {
          if (!state.session) {
            throw new Error('Join the session first.');
          }

          setStatus('Retrying private feed...', false);
          await disconnectPlayerStream();
          state.reconnectAttempts = 0;
          void connectPlayerStream();
        }

        async function connectPlayerStream() {
          if (!state.session) {
            return;
          }

          state.active = true;
          while (state.active) {
            const url = '/player/api/sessions/' + encodeURIComponent(state.session.session_id) + '/events?since=' + state.since;
            let response;
            try {
              response = await fetch(url, {
                headers: {
                  authorization: 'Bearer ' + state.session.player_token,
                },
              });
            } catch {
              const retryDelayMs = retryDelayFor(state.reconnectAttempts);
              if (!retryDelayMs) {
                setStatus('Private feed disconnected. Tap Retry feed or reload.', true);
                break;
              }
              state.reconnectAttempts += 1;
              setStatus('Private feed reconnecting in ' + retryDelayMs + 'ms.', false);
              await sleep(retryDelayMs);
              continue;
            }

            if (!response.ok || !response.body) {
              const retryDelayMs = retryDelayFor(state.reconnectAttempts);
              if (!retryDelayMs) {
                setStatus('Private feed failed with ' + response.status + '. Tap Retry feed or reload.', true);
                break;
              }
              state.reconnectAttempts += 1;
              setStatus('Private feed reconnecting in ' + retryDelayMs + 'ms.', false);
              await sleep(retryDelayMs);
              continue;
            }

            state.reader = response.body.getReader();
            state.reconnectAttempts = 0;
            setStatus('Private feed connected.', false);
            const decoder = new TextDecoder();
            let buffer = '';

            try {
              while (state.active) {
                const chunk = await state.reader.read();
                if (chunk.done) {
                  break;
                }

                buffer += decoder.decode(chunk.value, { stream: true });
                buffer = buffer.replace(/\\r\\n/g, '\\n').replace(/\\r/g, '\\n');
                const blocks = buffer.split('\\n\\n');
                buffer = blocks.pop() || '';
                blocks.forEach(parseSseBlock);
              }
            } finally {
              if (buffer.length) {
                parseSseBlock(buffer);
              }
              state.reader = null;
            }

            if (!state.active) {
              break;
            }

            const retryDelayMs = retryDelayFor(state.reconnectAttempts);
            if (!retryDelayMs) {
              setStatus('Private feed disconnected. Tap Retry feed or reload.', true);
              break;
            }
            state.reconnectAttempts += 1;
            setStatus('Private feed reconnecting in ' + retryDelayMs + 'ms.', false);
            await sleep(retryDelayMs);
          }
        }

        async function loadCharacterSurface() {
          if (!state.session) {
            return;
          }

          const response = await fetch(
            '/player/api/sessions/' +
              encodeURIComponent(state.session.session_id) +
              '/characters/' +
              encodeURIComponent(state.session.character_id),
            {
              headers: sessionHeaders(false),
            },
          );
          const data = await readJson(response);
          if (!response.ok) {
            throw new Error((data && data.detail) || 'Character load failed.');
          }

          renderPlayerCharacter(data);
        }

        function renderConnectedSession(session) {
          state.session = session;
          state.since = session.last_sequence_number || 0;
          state.reconnectAttempts = 0;
          persistSession(session);
          clearFeed();
          playerInputContent.value = '';
          playerInputContent.disabled = false;
          playerInputSubmit.disabled = false;
          playerFeedRetry.disabled = false;
          setStatus('Joined. Private events stay on this device.', false);
          const url = new URL(window.location.href);
          url.searchParams.set('session_id', session.session_id);
          url.searchParams.delete('token');
          window.history.replaceState({}, '', url.pathname + url.search);
          sessionIdInput.value = session.session_id;
          joinTokenInput.value = '';
        }

        async function activateSession(session) {
          await disconnectPlayerStream();
          renderConnectedSession(session);
          try {
            await loadCharacterSurface();
          } catch (error) {
            setStatus(
              error instanceof Error ? error.message : String(error),
              true,
            );
          }
          void connectPlayerStream();
        }

        async function joinPlayer() {
          const sessionId = sessionIdInput.value.trim();
          const joinToken = joinTokenInput.value.trim();
          if (!sessionId) {
            throw new Error('Session id is required.');
          }
          if (!joinToken) {
            throw new Error('Join token is required.');
          }

          setStatus('Joining session...', false);
          const response = await fetch('/join/api', {
            method: 'POST',
            headers: {
              'content-type': 'application/json',
            },
            body: JSON.stringify({
              session_id: sessionId,
              join_token: joinToken,
              personalization_intake: readPersonalizationIntake(joinForm),
            }),
          });
          const data = await readJson(response);
          if (!response.ok) {
            throw new Error((data && data.detail) || 'Join failed.');
          }

          setStatus('Signing you in...', false);
          const playerToken = await exchangeJoinTokenForBearerToken(
            sessionId,
            data.player.player_token,
          );

          await activateSession({
            session_id: data.session_id,
            player_id: data.player.player_id,
            character_id: data.player.character_id,
            player_token: playerToken.player_token,
            expires_at: playerToken.expires_at,
            last_sequence_number: 0,
          });
        }

        async function submitPlayerInput(event) {
          event.preventDefault();
          if (!state.session) {
            throw new Error('Join the session first.');
          }

          const content = playerInputContent.value.trim();
          if (!content) {
            throw new Error('Enter a message first.');
          }

          const response = await fetch(
            '/player/api/sessions/' +
              encodeURIComponent(state.session.session_id) +
              '/characters/' +
              encodeURIComponent(state.session.character_id) +
              '/input',
            {
              method: 'POST',
              headers: sessionHeaders(true),
              body: JSON.stringify({
                kind: playerInputKind.value,
                content: content,
              }),
            },
          );

          if (!response.ok) {
            const data = await readJson(response);
            throw new Error((data && data.detail) || 'Input submission failed.');
          }

          playerInputContent.value = '';
          setStatus('Input sent.', false);
        }

        async function resumeStoredSession() {
          const sessionId = sessionIdInput.value.trim();
          if (joinTokenInput.value.trim()) {
            return;
          }

          const stored = readActiveSession();
          if (!stored) {
            return;
          }

          if (sessionId && stored.session_id !== sessionId) {
            return;
          }

          if (isNightcapPlayerSessionExpired(stored)) {
            sessionStorage.removeItem(activeSessionStorageKey);
            sessionStorage.removeItem(
              buildPlayerSessionStorageKey(stored.session_id),
            );
            setStatus('Your private session expired. Rejoin to continue.', true);
            return;
          }

          if (!sessionId) {
            sessionIdInput.value = stored.session_id;
          }

          setStatus('Restoring your private surface...', false);
          await activateSession(stored);
        }

        joinForm.addEventListener('submit', function(event) {
          event.preventDefault();
          joinPlayer().catch(function(error) {
            setStatus(error.message || String(error), true);
          });
        });

        playerInputForm.addEventListener('submit', function(event) {
          submitPlayerInput(event).catch(function(error) {
            setStatus(error.message || String(error), true);
          });
        });

        if (playerFeedRetry instanceof HTMLButtonElement) {
          playerFeedRetry.addEventListener('click', function() {
            retryPlayerFeed().catch(function(error) {
              setStatus(error.message || String(error), true);
            });
          });
        }

        if (sessionIdInput.value.trim() && joinTokenInput.value.trim()) {
          setStatus('Answer the prompts, then tap Join.', false);
          const firstPrompt = joinForm.querySelector('[data-personalization-slot]');
          if (firstPrompt instanceof HTMLElement) {
            firstPrompt.focus();
          }
        }

        resumeStoredSession().catch(function(error) {
          setStatus(error.message || String(error), true);
        });
      })();
    </script>`,
    "phone",
  );
}
