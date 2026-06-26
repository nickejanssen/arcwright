// Fixture renderer: individual / timed-choice.
//
// Player picks one of three authored choices before the deadline. Engine owns
// timing, validation, scoring, clue unlocking. This renderer only displays
// authored content, captures the choice, and submits the opaque payload.

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

interface AuthoredContent {
  prompt: string;
  choices: string[];
}

function readAuthoredContent(ctx: MiniGameContext): AuthoredContent {
  const content = (ctx.definition.authored_content ??
    {}) as Partial<AuthoredContent>;
  const prompt = typeof content.prompt === "string" ? content.prompt : "";
  const choices = Array.isArray(content.choices)
    ? content.choices.filter((c): c is string => typeof c === "string")
    : [];
  return { prompt, choices };
}

function statusLabel(status: MiniGameContext["state"]["status"]): string {
  switch (status) {
    case "pending":
      return "Get ready.";
    case "active":
      return "Tap your answer.";
    case "paused":
      return "Paused.";
    case "timed_out":
      return "Time is up.";
    case "completed":
      return "Round complete.";
    case "cancelled":
      return "Round cancelled.";
  }
}

export default defineRenderer({
  gameId: "fixture-individual",

  phone: {
    mount(root, ctx): SurfaceLifecycle {
      const doc = root.ownerDocument;
      clearChildren(root);
      const { prompt, choices } = readAuthoredContent(ctx);

      const status = el(
        doc,
        "p",
        {
          class: "mg-status",
          "aria-live": "assertive",
          "data-role": "status",
        },
        [statusLabel(ctx.state.status)],
      );

      const promptNode = el(
        doc,
        "h2",
        {
          class: "mg-prompt",
          "data-role": "prompt",
        },
        [prompt],
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

      const choicesList = el(doc, "div", {
        class: "mg-choices",
        role: "group",
        "aria-label": "Choices",
      });
      const choiceButtons: HTMLButtonElement[] = [];

      const guard = createSubmissionGuard({
        submit: async (submissionId, payload) =>
          ctx.submit(payload, submissionId).catch(() => ({
            submissionId,
            isAccepted: false,
            rejectionReason: "network",
          })),
      });

      const onChoice = (choice: string) => async () => {
        if (guard.isPending() || guard.hasSubmitted()) return;
        for (const btn of choiceButtons) setDisabled(btn, true);
        const result = await guard.submit({ choice });
        if (!result || !result.isAccepted) {
          for (const btn of choiceButtons) setDisabled(btn, false);
        } else {
          setText(status, "Submitted. Hold tight.");
        }
      };

      for (const choice of choices) {
        const btn = el(
          doc,
          "button",
          {
            type: "button",
            class: "mg-choice",
            "data-choice": choice,
          },
          [choice],
        );
        on(btn, "click", onChoice(choice));
        choiceButtons.push(btn);
        choicesList.appendChild(btn);
      }

      const result = el(doc, "p", {
        class: "mg-result",
        "data-role": "result",
        hidden: true,
      });

      root.appendChild(status);
      root.appendChild(promptNode);
      root.appendChild(timer);
      root.appendChild(choicesList);
      root.appendChild(result);

      const view = doc.defaultView;
      const countdown = useCountdown({
        deadlineAt: ctx.state.deadlineAt,
        view,
        onTick: (remaining) => setText(timer, formatRemaining(remaining)),
      });

      const applyStatus = (state: MiniGameContext["state"]): void => {
        setText(status, statusLabel(state.status));
        const interactive = state.status === "active" && !guard.hasSubmitted();
        for (const btn of choiceButtons) setDisabled(btn, !interactive);
        if (state.status === "timed_out" || state.status === "completed") {
          setText(
            result,
            state.status === "timed_out"
              ? "Time ran out. Watch for the clue."
              : "Round complete. Watch for the clue.",
          );
          setHidden(result, false);
        }
      };

      applyStatus(ctx.state);

      return {
        update(state) {
          applyStatus(state);
        },
        handleEvent() {
          // No per-event UI updates required; state transitions trigger update().
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

      const title = el(
        doc,
        "h2",
        {
          class: "mg-shared-title",
        },
        ["Quick choice"],
      );

      const timer = el(
        doc,
        "div",
        {
          class: "mg-shared-timer",
          "aria-live": "polite",
          "data-role": "timer",
        },
        ["--:--"],
      );

      const tally = el(
        doc,
        "p",
        {
          class: "mg-shared-tally",
          "aria-live": "polite",
          "data-role": "tally",
        },
        ["Waiting for answers."],
      );

      const status = el(doc, "p", {
        class: "mg-shared-status",
        "aria-live": "assertive",
        "data-role": "status",
        hidden: true,
      });

      root.appendChild(title);
      root.appendChild(timer);
      root.appendChild(tally);
      root.appendChild(status);

      const view = doc.defaultView;
      const countdown = useCountdown({
        deadlineAt: ctx.state.deadlineAt,
        view,
        onTick: (remaining) => setText(timer, formatRemaining(remaining)),
      });

      let answeredCount = 0;

      const applyStatus = (state: MiniGameContext["state"]): void => {
        if (state.status === "timed_out") {
          setText(status, "Time ran out.");
          setHidden(status, false);
        } else if (state.status === "completed") {
          setText(status, "Round complete.");
          setHidden(status, false);
        } else {
          setHidden(status, true);
        }
      };

      applyStatus(ctx.state);

      return {
        update(state) {
          applyStatus(state);
        },
        handleEvent(event) {
          if (event.event_type === "mini_game_submission_accepted") {
            answeredCount += 1;
            setText(tally, `${answeredCount} answered.`);
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
        countLabel: (n) => `${n} answered`,
        countEventType: "mini_game_submission_accepted",
      });
    },
  },
});
