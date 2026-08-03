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

interface PrivatePrompt {
  statementId: string;
  prompt: string;
  trueLabel: string;
  lieLabel: string;
}

interface VotePrompt {
  statementId: string;
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

function isPrivatePrompt(payload: unknown): payload is PrivatePrompt {
  const data = record(payload);
  return (
    typeof data.statement_id === "string" && typeof data.prompt === "string"
  );
}

function readPrivatePrompt(payload: unknown): PrivatePrompt | null {
  if (!isPrivatePrompt(payload)) return null;
  const data = record(payload);
  return {
    statementId: String(data.statement_id),
    prompt: String(data.prompt),
    trueLabel: text(data.true_label, "Tell the truth"),
    lieLabel: text(data.lie_label, "Sell the lie"),
  };
}

function readVotePrompt(payload: unknown): VotePrompt | null {
  const data = record(payload);
  if (typeof data.statement_id !== "string") return null;
  return {
    statementId: data.statement_id,
    spotlightLabel: text(data.spotlight_label, "Someone at the table"),
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
): { node: HTMLElement; cancel: () => void } {
  const doc = parent.ownerDocument;
  const node = el(
    doc,
    "div",
    { class: "tmst-timer", "data-role": "timer", "aria-live": "polite" },
    ["--:--"],
  );
  parent.appendChild(node);
  const countdown = useCountdown({
    deadlineAt: ctx.state.deadlineAt,
    view: doc.defaultView,
    onTick: (remaining) => setText(node, formatRemaining(remaining)),
  });
  return { node, cancel: countdown.cancel };
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
      shell.appendChild(status);
      shell.appendChild(prompt);
      shell.appendChild(actionRow);
      shell.appendChild(voteRow);
      shell.appendChild(result);
      const timer = addTimer(shell, ctx);

      let privatePrompt: PrivatePrompt | null = null;
      let currentVote: VotePrompt | null = null;
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
        setText(status, phaseLabel(state.status));
        const active = state.status === "active";
        setDisabled(truthButton, !active || statementGuard.hasSubmitted());
        setDisabled(lieButton, !active || statementGuard.hasSubmitted());
        setDisabled(voteTruth, !active || voteGuard.hasSubmitted());
        setDisabled(voteLie, !active || voteGuard.hasSubmitted());
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
          if (!privatePrompt || statementGuard.hasSubmitted()) return;
          setDisabled(truthButton, true);
          setDisabled(lieButton, true);
          const submitted = await statementGuard.submit({
            action: "submit_statement",
            statement_id: privatePrompt.statementId,
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
          action: "vote_statement",
          statement_id: currentVote.statementId,
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
      applyStatus(ctx.state);

      return {
        update(state) {
          applyStatus(state);
        },
        handleEvent(event) {
          if (event.event_type === "mini_game_private_prompt") {
            privatePrompt = readPrivatePrompt(event.payload);
            if (!privatePrompt) return;
            setText(prompt, privatePrompt.prompt);
            setText(truthButton, privatePrompt.trueLabel);
            setText(lieButton, privatePrompt.lieLabel);
            setHidden(prompt, false);
            setHidden(actionRow, false);
            applyStatus(ctx.state);
            return;
          }
          if (event.event_type === "mini_game_vote_opened") {
            currentVote = readVotePrompt(event.payload);
            if (!currentVote) return;
            setText(votePrompt, `${currentVote.spotlightLabel}: truth or lie?`);
            setHidden(voteRow, false);
            applyStatus(ctx.state);
            return;
          }
          if (event.event_type === "mini_game_personal_result") {
            const data = record(event.payload);
            setText(result, text(data.summary, "Personal result received."));
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

      const applyStatus = (state: MiniGameContext["state"]): void => {
        setText(phase, phaseLabel(state.status));
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
          if (event.event_type === "mini_game_private_prompt") return;
          if (event.event_type === "mini_game_submission_accepted") {
            count += 1;
            setText(tally, `${count} response${count === 1 ? "" : "s"} in.`);
            return;
          }
          if (event.event_type === "mini_game_spotlight") {
            const data = record(event.payload);
            setText(spotlight, text(data.spotlight_label, "Spotlight is up."));
            return;
          }
          if (event.event_type === "mini_game_public_result") {
            const data = record(event.payload);
            setText(reveal, text(data.summary, "Public result received."));
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
