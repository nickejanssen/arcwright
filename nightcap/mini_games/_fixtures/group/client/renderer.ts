// Fixture renderer: group / group-sequence.
//
// Generative: options arrive in a mini_game_started event payload. The
// renderer waits for that event before showing anything interactive. Each
// participant submits one response; engine validates submission policy.

import {
  defineRenderer,
  useCountdown,
  formatRemaining,
  createSubmissionGuard,
  createHostStatusCard,
  el,
  on,
  setText,
  setHidden,
  setDisabled,
  clearChildren,
  type MiniGameContext,
  type SurfaceLifecycle,
} from "@arcwright/mini-game-kit";

interface StartedPayload {
  options?: string[];
  prompt?: string;
}

function readStartedPayload(payload: unknown): StartedPayload {
  if (!payload || typeof payload !== "object") return {};
  const candidate = payload as Record<string, unknown>;
  const out: StartedPayload = {};
  if (typeof candidate.prompt === "string") out.prompt = candidate.prompt;
  if (Array.isArray(candidate.options)) {
    out.options = candidate.options.filter(
      (v): v is string => typeof v === "string",
    );
  }
  return out;
}

export default defineRenderer({
  gameId: "fixture-group",

  phone: {
    mount(root, ctx): SurfaceLifecycle {
      const doc = root.ownerDocument;
      clearChildren(root);

      const status = el(
        doc,
        "p",
        {
          class: "mg-status",
          "aria-live": "assertive",
          "data-role": "status",
        },
        ["Waiting for the prompt..."],
      );

      const promptNode = el(doc, "h2", {
        class: "mg-prompt",
        "data-role": "prompt",
        hidden: true,
      });

      const optionsList = el(doc, "div", {
        class: "mg-options",
        role: "group",
        "aria-label": "Options",
        hidden: true,
      });

      const timer = el(
        doc,
        "div",
        {
          class: "mg-timer",
          "aria-live": "polite",
          "data-role": "timer",
        },
        ["--:--"],
      );

      root.appendChild(status);
      root.appendChild(promptNode);
      root.appendChild(optionsList);
      root.appendChild(timer);

      const buttons: HTMLButtonElement[] = [];

      const guard = createSubmissionGuard({
        submit: async (submissionId, payload) =>
          ctx.submit(payload).catch(() => ({
            submissionId,
            isAccepted: false,
            rejectionReason: "network",
          })),
      });

      const renderOptions = (options: string[]): void => {
        clearChildren(optionsList);
        buttons.length = 0;
        options.forEach((option, index) => {
          const btn = el(
            doc,
            "button",
            {
              type: "button",
              class: "mg-option",
              "data-option-index": String(index),
            },
            [option],
          );
          on(btn, "click", async () => {
            if (guard.isPending() || guard.hasSubmitted()) return;
            for (const b of buttons) setDisabled(b, true);
            const result = await guard.submit({
              action: "group_response",
              option_index: index,
            });
            if (!result || !result.isAccepted) {
              for (const b of buttons) setDisabled(b, false);
            } else {
              setText(status, "Response submitted.");
            }
          });
          buttons.push(btn);
          optionsList.appendChild(btn);
        });
        setHidden(optionsList, false);
      };

      const view = doc.defaultView;
      const countdown = useCountdown({
        deadlineAt: ctx.state.deadlineAt,
        view,
        onTick: (remaining) => setText(timer, formatRemaining(remaining)),
      });

      const applyStatus = (state: MiniGameContext["state"]): void => {
        if (state.status === "timed_out") {
          setText(status, "Time ran out.");
          for (const b of buttons) setDisabled(b, true);
        } else if (state.status === "completed") {
          setText(status, "Round complete.");
          for (const b of buttons) setDisabled(b, true);
        }
      };

      applyStatus(ctx.state);

      return {
        update(state) {
          applyStatus(state);
        },
        handleEvent(event) {
          if (event.event_type === "mini_game_started") {
            const data = readStartedPayload(event.payload);
            if (data.prompt) {
              setText(promptNode, data.prompt);
              setHidden(promptNode, false);
            }
            if (data.options && data.options.length > 0) {
              renderOptions(data.options);
              setText(status, "Choose your response.");
            }
          }
        },
        unmount() {
          countdown.cancel();
          clearChildren(root);
        },
      };
    },
  },

  sharedDisplay: {
    mount(root, ctx): SurfaceLifecycle {
      const doc = root.ownerDocument;
      clearChildren(root);

      const title = el(doc, "h2", {}, ["Group choice"]);
      const promptNode = el(doc, "p", {
        class: "mg-shared-prompt",
        "data-role": "prompt",
        hidden: true,
      });
      const tally = el(
        doc,
        "p",
        {
          class: "mg-shared-tally",
          "aria-live": "polite",
          "data-role": "tally",
        },
        ["Waiting for responses."],
      );
      const timer = el(
        doc,
        "div",
        {
          class: "mg-timer",
          "aria-live": "polite",
          "data-role": "timer",
        },
        ["--:--"],
      );
      const status = el(doc, "p", {
        class: "mg-status",
        "aria-live": "assertive",
        "data-role": "status",
        hidden: true,
      });

      root.appendChild(title);
      root.appendChild(promptNode);
      root.appendChild(tally);
      root.appendChild(timer);
      root.appendChild(status);

      let count = 0;

      const view = doc.defaultView;
      const countdown = useCountdown({
        deadlineAt: ctx.state.deadlineAt,
        view,
        onTick: (remaining) => setText(timer, formatRemaining(remaining)),
      });

      const applyStatus = (state: MiniGameContext["state"]): void => {
        if (state.status === "timed_out") {
          setText(status, "Time ran out.");
          setHidden(status, false);
        } else if (state.status === "completed") {
          setText(status, "Round complete.");
          setHidden(status, false);
        }
      };

      applyStatus(ctx.state);

      return {
        update(state) {
          applyStatus(state);
        },
        handleEvent(event) {
          if (event.event_type === "mini_game_started") {
            const data = readStartedPayload(event.payload);
            if (data.prompt) {
              setText(promptNode, data.prompt);
              setHidden(promptNode, false);
            }
          }
          if (event.event_type === "mini_game_submission_accepted") {
            count += 1;
            setText(tally, `${count} response${count === 1 ? "" : "s"} in.`);
          }
        },
        unmount() {
          countdown.cancel();
          clearChildren(root);
        },
      };
    },
  },

  host: {
    mount(root, ctx): SurfaceLifecycle {
      return createHostStatusCard(root, {
        state: ctx.state,
        definition: ctx.definition,
        countLabel: (n) => `${n} responses received`,
        countEventType: "mini_game_submission_accepted",
      });
    },
  },
});
