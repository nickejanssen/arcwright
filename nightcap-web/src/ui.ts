import { SHARED_DISPLAY_VISIBLE_AUDIENCES } from "./filters.js";
import {
  HOST_SEED_PROMPTS,
  PLAYER_JOIN_PROMPTS,
  renderPersonalizationPromptFields,
} from "./personalization.js";
import { escapeHtml } from "./html.js";
import { buildNightcapRuntimeUrls } from "./runtime.js";
import type { ContentEvent, PresentationHints } from "./types.js";

function pageShell(title: string, body: string): string {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${title}</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0b1020;
      --panel: rgba(16, 22, 43, 0.88);
      --panel-strong: #121a33;
      --line: rgba(163, 183, 255, 0.18);
      --text: #eef2ff;
      --muted: #98a3c7;
      --accent: #7dd3fc;
      --accent-strong: #38bdf8;
      --danger: #fb7185;
      --success: #34d399;
      font-family: Inter, "Segoe UI", system-ui, sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top, rgba(56, 189, 248, 0.18), transparent 36%),
        linear-gradient(160deg, #050814 0%, #0b1020 55%, #10162d 100%);
      color: var(--text);
    }
    main {
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }
    .shell {
      display: grid;
      gap: 18px;
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
      backdrop-filter: blur(16px);
    }
    h1, h2, h3, p { margin-top: 0; }
    h1 { font-size: clamp(2rem, 4vw, 3.5rem); margin-bottom: 8px; }
    h2 { font-size: 1.2rem; margin-bottom: 10px; }
    p, label, button, input, textarea, select, summary {
      font: inherit;
    }
    label { display: grid; gap: 8px; margin-bottom: 12px; color: var(--muted); }
    input, textarea, select, button {
      border-radius: 12px;
      border: 1px solid var(--line);
      background: rgba(6, 10, 24, 0.75);
      color: var(--text);
      padding: 12px 14px;
    }
    textarea { min-height: 120px; resize: vertical; }
    button {
      cursor: pointer;
      font-weight: 650;
      background: linear-gradient(135deg, rgba(56, 189, 248, 0.18), rgba(125, 211, 252, 0.08));
    }
    button:hover { border-color: rgba(125, 211, 252, 0.45); }
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
    .muted { color: var(--muted); }
    .status {
      padding: 10px 12px;
      border-radius: 12px;
      background: rgba(59, 130, 246, 0.08);
      border: 1px solid rgba(59, 130, 246, 0.2);
      color: var(--accent);
      white-space: pre-wrap;
    }
    .status.error {
      background: rgba(244, 63, 94, 0.08);
      border-color: rgba(244, 63, 94, 0.2);
      color: var(--danger);
    }
    .event-feed {
      display: grid;
      gap: 12px;
    }
    .event {
      border: 1px solid var(--line);
      background: rgba(7, 11, 24, 0.78);
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
      color: var(--accent);
      text-transform: capitalize;
    }
    .event-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
      color: var(--muted);
      font-size: 0.88rem;
    }
    .event-body {
      margin: 10px 0 0;
      white-space: pre-wrap;
      word-break: break-word;
      color: var(--text);
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
      border-radius: 999px;
      border: 1px solid rgba(125, 211, 252, 0.22);
      padding: 4px 10px;
      color: var(--accent);
      background: rgba(8, 15, 30, 0.7);
      font-size: 0.82rem;
    }
    .pill {
      display: inline-block;
      margin-left: 8px;
      padding: 2px 8px;
      border-radius: 999px;
      border: 1px solid var(--line);
      color: var(--muted);
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
      background: rgba(8, 15, 30, 0.55);
    }
    .prompt-title {
      color: var(--text);
      font-weight: 650;
    }
    .prompt-help {
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.35;
    }
    .hide { display: none; }
    @media (max-width: 900px) {
      .grid.two { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
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
    return JSON.stringify(payload, null, 2);
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
          <form id="bootstrap-form" class="card" style="margin: 0; background: var(--panel-strong);">
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
            <div class="card" style="margin: 0 0 12px; background: rgba(8, 15, 30, 0.55);">
              <h3>Group personalization</h3>
              <p class="muted">Three short answers seed character fit and narrator callbacks.</p>
              ${renderPersonalizationPromptFields(HOST_SEED_PROMPTS)}
            </div>
            <button type="submit">Create session</button>
          </form>

          <div class="card" style="margin: 0; background: var(--panel-strong);">
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
    </section>
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
          <div class="card" style="margin: 0; background: var(--panel-strong);">
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
          <div class="card" style="margin: 0; background: var(--panel-strong);">
            <h2>Runtime URLs</h2>
            <pre class="status">${JSON.stringify(urls, null, 2)}</pre>
          </div>
        </div>
      </div>
      <div class="card">
        <h2>Visible events</h2>
        <div id="event-feed" class="event-feed"></div>
      </div>
    </section>
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
  );
}

export function renderPlayerJoinPage(sessionId = "", joinToken = ""): string {
  return pageShell(
    "Nightcap Player Join",
    `<section class="shell">
      <div class="card">
        <h1>Join Nightcap</h1>
        <p class="muted">Join with the QR link or the join code from the host. No account or app install required.</p>
        <div class="grid two">
          <div class="card" style="margin: 0; background: var(--panel-strong);">
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
              <div class="card" style="margin: 0 0 12px; background: rgba(8, 15, 30, 0.55);">
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
          <div class="card" style="margin: 0; background: var(--panel-strong);">
            <h2>Your surface</h2>
            <div id="player-surface" class="status">No character assigned yet.</div>
          </div>
        </div>
      </div>
    </section>
    <script>
      (function() {
        const joinForm = document.getElementById('player-join-form');
        const sessionIdInput = document.getElementById('join-session-id');
        const joinTokenInput = document.getElementById('join-token');
        const status = document.getElementById('player-status');
        const playerSurface = document.getElementById('player-surface');

        function setStatus(message, isError) {
          status.textContent = message;
          status.className = isError ? 'status error' : 'status';
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

        function renderPlayerSurface(data) {
          playerSurface.textContent = JSON.stringify({
            character_id: data.player.character_id,
          }, null, 2);
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

          renderPlayerSurface(data);
          setStatus('Joined. You are on your private player surface.', false);

          const url = new URL(window.location.href);
          url.searchParams.set('session_id', sessionId);
          url.searchParams.delete('token');
          window.history.replaceState({}, '', url.pathname + url.search);
        }

        joinForm.addEventListener('submit', function(event) {
          event.preventDefault();
          joinPlayer().catch(function(error) {
            setStatus(error.message || String(error), true);
          });
        });

        if (sessionIdInput.value.trim() && joinTokenInput.value.trim()) {
          setStatus('Answer the prompts, then tap Join.', false);
          const firstPrompt = joinForm.querySelector('[data-personalization-slot]');
          if (firstPrompt instanceof HTMLElement) {
            firstPrompt.focus();
          }
        }
      })();
    </script>`,
  );
}
