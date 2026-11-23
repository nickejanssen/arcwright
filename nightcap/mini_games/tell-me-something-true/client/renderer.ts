import {
  clearChildren,
  createSubmissionGuard,
  defineRenderer,
  el,
  formatRemaining,
  on,
  prefersReducedMotion,
  setDisabled,
  setHidden,
  setText,
  useCountdown,
  type MiniGameContext,
  type SurfaceLifecycle,
} from "@arcwright/mini-game-kit";

const PREVIEW_LABEL = "NON_AUTHORITATIVE_PREVIEW";
const GAME_ID = "tell-me-something-true";

type Status = MiniGameContext["state"]["status"];
type DisplayState = MiniGameContext["state"] & {
  phaseState?: Record<string, unknown>;
  playerNames?: Record<string, string>;
};

interface PromptContent {
  prompt: string;
  trueLabel: string;
  lieLabel: string;
}

interface VotePrompt {
  targetCharacterId: string;
  spotlightLabel: string;
}

function record(value: unknown): Record<string, unknown> {
  return value && typeof value === "object"
    ? (value as Record<string, unknown>)
    : {};
}

function text(value: unknown, fallback: string): string {
  return typeof value === "string" && value.trim() ? value : fallback;
}

function standingText(state: MiniGameContext["state"]): string {
  return (state.resultHold?.standing ?? [])
    .map(
      (tier, index) =>
        `${index + 1}. ${tier.map((id) => state.playerNames?.[id] ?? "Player").join(" & ")}`,
    )
    .join(" | ");
}

function presentation(ctx: MiniGameContext): Record<string, unknown> {
  return record(ctx.state.presentation);
}

function runtime(ctx: MiniGameContext): Record<string, unknown> {
  return record(ctx.state.runtimeState);
}

function phaseLabel(status: Status): string {
  switch (status) {
    case "pending":
      return "Waiting for the room.";
    case "active":
      return "Truth pressure is live.";
    case "paused":
      return "Paused.";
    case "completed":
      return "Round complete.";
    case "timed_out":
      return "Time. The room moves on.";
    case "cancelled":
      return "Round cancelled.";
  }
}

function readPromptContent(ctx: MiniGameContext): PromptContent {
  const authored = record(ctx.definition.authored_content);
  const presentationData = presentation(ctx);
  return {
    prompt: text(
      presentationData.prompt,
      text(
        authored.phone_prompt,
        "Complete your statement, then decide whether to tell the truth or sell the lie.",
      ),
    ),
    trueLabel: text(presentationData.true_label, "Tell the truth"),
    lieLabel: text(presentationData.lie_label, "Sell the lie"),
  };
}

function readVotePrompt(payload: unknown): VotePrompt | null {
  const data = record(payload);
  if (typeof data.target_character_id !== "string") return null;
  return {
    targetCharacterId: data.target_character_id,
    spotlightLabel: text(data.spotlight_label, "Current spotlight"),
  };
}

function addPreviewShell(
  root: HTMLElement,
  ctx: MiniGameContext,
  className: string,
): HTMLElement {
  const doc = root.ownerDocument;
  clearChildren(root);
  root.classList.add("tmst-root");
  root.setAttribute("data-authority", PREVIEW_LABEL);
  root.setAttribute(
    "data-reduced-motion",
    prefersReducedMotion(doc.defaultView) ? "true" : "false",
  );

  const shell = el(doc, "section", {
    class: className,
    "data-role": "tmst-shell",
  });
  const banner = el(
    doc,
    "p",
    {
      class: "tmst-preview",
      "data-role": "preview-banner",
      "aria-live": "polite",
    },
    [PREVIEW_LABEL],
  );
  shell.appendChild(banner);
  root.appendChild(shell);
  void ctx;
  return shell;
}

function addTimer(
  parent: HTMLElement,
  ctx: MiniGameContext,
): {
  node: HTMLElement;
  cancel: () => void;
  update: (deadline: string | null) => void;
} {
  const doc = parent.ownerDocument;
  const node = el(
    doc,
    "div",
    { class: "tmst-timer", "data-role": "timer", "aria-live": "polite" },
    ["--:--"],
  );
  parent.appendChild(node);
  let deadline = ctx.state.deadlineAt;
  const start = (at: string | null) =>
    useCountdown({
      deadlineAt: at,
      view: doc.defaultView,
      onTick: (remaining) => setText(node, formatRemaining(remaining)),
    });
  let countdown = start(deadline);
  return {
    node,
    cancel: () => countdown.cancel(),
    update: (next) => {
      if (next === deadline) return;
      deadline = next;
      countdown.cancel();
      countdown = start(next);
    },
  };
}

export default defineRenderer({
  gameId: GAME_ID,

  phone: {
    mount(root, ctx): SurfaceLifecycle {
      const doc = root.ownerDocument;
      const shell = addPreviewShell(root, ctx, "tmst-phone");
      const status = el(
        doc,
        "p",
        {
          class: "tmst-status",
          "data-role": "status",
          "aria-live": "assertive",
        },
        [phaseLabel(ctx.state.status)],
      );
      const prompt = el(
        doc,
        "h2",
        { class: "tmst-prompt", "data-role": "private-prompt", hidden: true },
        [""],
      );
      const statementInput = el(doc, "textarea", {
        class: "tmst-input",
        "data-role": "statement-input",
        rows: "3",
        maxlength: "280",
        hidden: true,
      });
      const actionRow = el(doc, "div", {
        class: "tmst-actions",
        role: "group",
        "aria-label": "Statement actions",
        hidden: true,
      });
      const truthButton = el(
        doc,
        "button",
        { type: "button", class: "tmst-button", "data-role": "truth-action" },
        ["Tell the truth"],
      );
      const lieButton = el(
        doc,
        "button",
        { type: "button", class: "tmst-button", "data-role": "lie-action" },
        ["Sell the lie"],
      );
      actionRow.appendChild(truthButton);
      actionRow.appendChild(lieButton);

      const voteRow = el(doc, "div", {
        class: "tmst-actions",
        role: "group",
        "aria-label": "Vote actions",
        hidden: true,
      });
      const votePrompt = el(doc, "p", {
        class: "tmst-vote-prompt",
        "data-role": "vote-prompt",
      });
      const voteTruth = el(
        doc,
        "button",
        { type: "button", class: "tmst-button", "data-role": "vote-truth" },
        ["Truth"],
      );
      const voteLie = el(
        doc,
        "button",
        { type: "button", class: "tmst-button", "data-role": "vote-lie" },
        ["Lie"],
      );
      voteRow.appendChild(votePrompt);
      voteRow.appendChild(voteTruth);
      voteRow.appendChild(voteLie);

      const result = el(doc, "p", {
        class: "tmst-result",
        "data-role": "result",
        "aria-live": "polite",
        hidden: true,
      });
      const readyButton = el(
        doc,
        "button",
        {
          type: "button",
          class: "tmst-button",
          "data-role": "result-ready",
          hidden: true,
        },
        ["Ready to continue"],
      );
      shell.appendChild(status);
      shell.appendChild(prompt);
      shell.appendChild(statementInput);
      shell.appendChild(actionRow);
      shell.appendChild(voteRow);
      shell.appendChild(result);
      shell.appendChild(readyButton);
      const timer = addTimer(shell, ctx);

      let promptReady = false;
      let currentVote: VotePrompt | null = null;
      let currentState = ctx.state;
      const statementGuard = createSubmissionGuard({
        submit: async (submissionId, payload) =>
          ctx.submit(payload, submissionId).catch(() => ({
            submissionId,
            isAccepted: false,
            rejectionReason: "network",
          })),
      });
      const voteGuard = createSubmissionGuard({
        submit: async (submissionId, payload) =>
          ctx.submit(payload, submissionId).catch(() => ({
            submissionId,
            isAccepted: false,
            rejectionReason: "network",
          })),
      });

      const applyStatus = (state: MiniGameContext["state"]): void => {
        // Name-only updates retain the snapshot object; a refresh replaces it.
        currentState = state;
        timer.update(state.deadlineAt);
        if (state.resultHold?.paused && state.resultHold.secondsLeft != null)
          setText(
            timer.node,
            formatRemaining(state.resultHold.secondsLeft * 1000),
          );
        setHidden(readyButton, !state.resultHold || !ctx.markReady);
        setDisabled(readyButton, state.resultHold?.myReady === true);
        if (state.resultHold) {
          setHidden(prompt, true);
          setHidden(statementInput, true);
          setHidden(actionRow, true);
          setHidden(voteRow, true);
          setText(result, standingText(state));
          setHidden(result, false);
          setText(
            status,
            state.resultHold.myReady
              ? "Ready. Waiting for the room."
              : "Round complete.",
          );
          return;
        }
        setText(status, phaseLabel(state.status));
        const active = state.status === "active";
        setDisabled(
          truthButton,
          !active || !promptReady || statementGuard.hasSubmitted(),
        );
        setDisabled(
          lieButton,
          !active || !promptReady || statementGuard.hasSubmitted(),
        );
        setDisabled(
          voteTruth,
          !active || !currentVote || voteGuard.hasSubmitted(),
        );
        setDisabled(
          voteLie,
          !active || !currentVote || voteGuard.hasSubmitted(),
        );
        if (state.status === "completed" || state.status === "timed_out") {
          setText(
            result,
            state.status === "completed"
              ? "Scores are being staged for the reveal."
              : "Fallback is active. No clue, score, or story state changes here.",
          );
          setHidden(result, false);
        }
      };

      const submitStatement =
        (declaredTruth: boolean) => async (): Promise<void> => {
          if (!promptReady || statementGuard.hasSubmitted()) return;
          const statementText = statementInput.value.trim();
          if (!statementText) {
            setText(status, "Write the statement before submitting.");
            return;
          }
          setDisabled(truthButton, true);
          setDisabled(lieButton, true);
          const submitted = await statementGuard.submit({
            action: "input",
            statement_text: statementText,
            declared_truth: declaredTruth,
          });
          if (submitted?.isAccepted) {
            setText(status, "Locked in. Watch the table work.");
          } else {
            setDisabled(truthButton, false);
            setDisabled(lieButton, false);
          }
        };

      const submitVote = (vote: "truth" | "lie") => async (): Promise<void> => {
        if (!currentVote || voteGuard.hasSubmitted()) return;
        setDisabled(voteTruth, true);
        setDisabled(voteLie, true);
        const submitted = await voteGuard.submit({
          action: "vote",
          target_character_id: currentVote.targetCharacterId,
          vote,
        });
        if (submitted?.isAccepted) {
          setText(status, "Vote locked.");
        } else {
          setDisabled(voteTruth, false);
          setDisabled(voteLie, false);
        }
      };

      on(truthButton, "click", submitStatement(true));
      on(lieButton, "click", submitStatement(false));
      on(voteTruth, "click", submitVote("truth"));
      on(voteLie, "click", submitVote("lie"));
      on(readyButton, "click", async () => {
        if (!currentState.resultHold || !ctx.markReady) return;
        setDisabled(readyButton, true);
        try {
          await ctx.markReady(currentState.resultHold.phaseEntry);
          setText(status, "Ready. Waiting for the room.");
        } catch {
          setDisabled(readyButton, false);
          setText(result, "Could not mark ready. Please try again.");
        }
      });
      applyStatus(ctx.state);

      return {
        update(state) {
          applyStatus(state);
        },
        handleEvent(event) {
          if (event.event_type === "tmst_private_prompt_ready") {
            const promptContent = readPromptContent(ctx);
            promptReady = true;
            setText(prompt, promptContent.prompt);
            setText(truthButton, promptContent.trueLabel);
            setText(lieButton, promptContent.lieLabel);
            setHidden(prompt, false);
            setHidden(statementInput, false);
            setHidden(actionRow, false);
            applyStatus(ctx.state);
            return;
          }
          if (event.event_type === "tmst_spotlight_started") {
            currentVote = readVotePrompt(event.payload);
            if (!currentVote) return;
            setText(votePrompt, `${currentVote.spotlightLabel}: truth or lie?`);
            setHidden(voteRow, false);
            applyStatus(ctx.state);
            return;
          }
          if (event.event_type === "tmst_reveal_resolved") {
            const data = record(event.payload);
            setText(result, text(data.statement_text, "Statement resolved."));
            setHidden(result, false);
          }
        },
        unmount() {
          timer.cancel();
          clearChildren(root);
        },
      };
    },
  },

  sharedDisplay: {
    mount(root, ctx): SurfaceLifecycle {
      const doc = root.ownerDocument;
      const shell = addPreviewShell(root, ctx, "tmst-shared");
      const publicPresentation = presentation(ctx);
      const title = el(
        doc,
        "h2",
        { class: "tmst-title", "data-role": "title" },
        [text(publicPresentation.title, "Tell Me Something True")],
      );
      const phase = el(
        doc,
        "p",
        {
          class: "tmst-status",
          "data-role": "status",
          "aria-live": "assertive",
        },
        [phaseLabel(ctx.state.status)],
      );
      const spotlight = el(
        doc,
        "p",
        { class: "tmst-spotlight", "data-role": "spotlight" },
        [text(runtime(ctx).spotlight_label, "The room is warming up.")],
      );
      const tally = el(
        doc,
        "p",
        { class: "tmst-tally", "data-role": "tally", "aria-live": "polite" },
        ["0 responses in."],
      );
      const reveal = el(doc, "p", {
        class: "tmst-result",
        "data-role": "public-result",
        "aria-live": "polite",
        hidden: true,
      });
      shell.appendChild(title);
      shell.appendChild(phase);
      shell.appendChild(spotlight);
      shell.appendChild(tally);
      shell.appendChild(reveal);
      const timer = addTimer(shell, ctx);
      let count = 0;
      let currentState: DisplayState = ctx.state;
      let eventSpotlight: { target: unknown; label: unknown } | null = null;

      const showSpotlight = (target: unknown, legacyLabel?: unknown): void => {
        const name =
          typeof target === "string"
            ? currentState.playerNames?.[target]
            : undefined;
        setText(
          spotlight,
          name
            ? `${name} is in the spotlight.`
            : text(legacyLabel, "A player is in the spotlight."),
        );
      };

      const applyStatus = (state: MiniGameContext["state"]): void => {
        if (
          state.resultHold ||
          state.status !== "active" ||
          state.runtimeState?.phase === "scoreboard" ||
          (state.runtimeState !== currentState.runtimeState &&
            state.runtimeState?.phase === "spotlight")
        )
          eventSpotlight = null;
        currentState = state;
        timer.update(state.deadlineAt);
        if (state.resultHold?.paused && state.resultHold.secondsLeft != null)
          setText(
            timer.node,
            formatRemaining(state.resultHold.secondsLeft * 1000),
          );
        if (state.resultHold) {
          setText(phase, "Results");
          setText(spotlight, "The room's standings");
          setText(
            tally,
            state.resultHold.readyCount != null &&
              state.resultHold.playerCount != null
              ? `${state.resultHold.readyCount} of ${state.resultHold.playerCount} ready.`
              : "",
          );
          setText(reveal, standingText(state));
          setHidden(reveal, false);
          return;
        }
        if (eventSpotlight) {
          setText(phase, "Spotlight: truth or lie?");
          showSpotlight(eventSpotlight.target, eventSpotlight.label);
          return;
        }
        const step = state.runtimeState?.phase;
        const labels: Record<string, string> = {
          input: "Write your statement.",
          spotlight: "Spotlight: truth or lie?",
          scoreboard: "Scoreboard.",
        };
        setText(
          phase,
          state.status === "active" && typeof step === "string"
            ? (labels[step] ?? phaseLabel(state.status))
            : phaseLabel(state.status),
        );
        if (state.status === "active" && step === "spotlight") {
          showSpotlight(currentState.phaseState?.target_character_id);
        } else if (typeof step !== "string" && state.status === "active") {
          setText(
            spotlight,
            text(
              state.runtimeState?.spotlight_label,
              "The room is warming up.",
            ),
          );
        } else {
          setText(spotlight, "The room is warming up.");
        }
        if (state.status === "timed_out") {
          setText(
            reveal,
            "Fallback active. The story continues without consequences.",
          );
          setHidden(reveal, false);
        } else if (state.status === "completed") {
          setText(reveal, "Reveal staged. Final scoring remains engine-owned.");
          setHidden(reveal, false);
        }
      };

      applyStatus(ctx.state);

      return {
        update(state) {
          applyStatus(state);
        },
        handleEvent(event) {
          if (event.event_type === "tmst_private_prompt_ready") return;
          if (event.event_type === "mini_game_submission_accepted") {
            count += 1;
            setText(tally, `${count} response${count === 1 ? "" : "s"} in.`);
            return;
          }
          if (event.event_type === "tmst_spotlight_started") {
            const data = record(event.payload);
            eventSpotlight = {
              target: data.target_character_id,
              label: data.spotlight_label,
            };
            setText(phase, "Spotlight: truth or lie?");
            showSpotlight(data.target_character_id, data.spotlight_label);
            return;
          }
          if (event.event_type === "tmst_reveal_resolved") {
            const data = record(event.payload);
            setText(reveal, text(data.statement_text, "Statement resolved."));
            setHidden(reveal, false);
            return;
          }
          if (event.event_type === "tmst_scoreboard_ready") {
            eventSpotlight = null;
            setText(phase, "Scoreboard.");
            setText(spotlight, "The room is warming up.");
            setText(
              reveal,
              "Scoreboard ready. Final scoring remains engine-owned.",
            );
            setHidden(reveal, false);
          }
        },
        unmount() {
          timer.cancel();
          clearChildren(root);
        },
      };
    },
  },

  host: {
    mount(root, ctx): SurfaceLifecycle {
      const doc = root.ownerDocument;
      const shell = addPreviewShell(root, ctx, "tmst-host");
      const title = el(doc, "h2", { class: "tmst-title" }, [
        "Tell Me Something True status",
      ]);
      const status = el(
        doc,
        "p",
        {
          class: "tmst-status",
          "data-role": "status",
          "aria-live": "assertive",
        },
        [phaseLabel(ctx.state.status)],
      );
      const progress = el(
        doc,
        "p",
        { class: "tmst-tally", "data-role": "host-progress" },
        ["0 accepted submissions."],
      );
      const fallback = el(doc, "p", { class: "tmst-result" }, [
        "Fallback available. Preview evidence cannot promote production authority.",
      ]);
      shell.appendChild(title);
      shell.appendChild(status);
      shell.appendChild(progress);
      shell.appendChild(fallback);
      const timer = addTimer(shell, ctx);
      let accepted = 0;

      return {
        update(state) {
          setText(status, phaseLabel(state.status));
        },
        handleEvent(event) {
          if (event.event_type === "mini_game_submission_accepted") {
            accepted += 1;
            setText(
              progress,
              `${accepted} accepted submission${accepted === 1 ? "" : "s"}.`,
            );
          }
        },
        unmount() {
          timer.cancel();
          clearChildren(root);
        },
      };
    },
  },
});
