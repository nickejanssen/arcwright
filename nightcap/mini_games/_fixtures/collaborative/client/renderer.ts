// Fixture renderer: collaborative / piece-assembly.
//
// Each player holds a private piece delivered as a specific_player event.
// Players choose when to share their piece. Engine tracks pieces shared and
// owns the all-pieces-required completion logic. This renderer never renders
// another player's piece content.

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

interface PieceDelivery {
  piece_id: string;
  text?: string;
}

function isPieceDeliveryPayload(payload: unknown): payload is PieceDelivery {
  if (!payload || typeof payload !== "object") return false;
  const candidate = payload as Record<string, unknown>;
  return typeof candidate.piece_id === "string";
}

export default defineRenderer({
  gameId: "fixture-collaborative",

  phone: {
    mount(root, ctx): SurfaceLifecycle {
      const doc = root.ownerDocument;
      clearChildren(root);

      const instructions = el(
        doc,
        "p",
        {
          class: "mg-instructions",
        },
        [
          (ctx.definition.authored_content as { instructions?: string } | null)
            ?.instructions ?? "",
        ],
      );

      const pieceCard = el(doc, "section", {
        class: "mg-piece-card",
        "aria-label": "Your private piece",
        "data-role": "piece",
        hidden: true,
      });
      const pieceLabel = el(doc, "h3", { class: "mg-piece-label" }, [
        "Your piece",
      ]);
      const pieceBody = el(doc, "p", {
        class: "mg-piece-body",
        "data-role": "piece-body",
      });
      pieceCard.appendChild(pieceLabel);
      pieceCard.appendChild(pieceBody);

      const shareBtn = el(
        doc,
        "button",
        {
          type: "button",
          class: "mg-share",
          "data-role": "share",
        },
        ["Share piece"],
      );
      setDisabled(shareBtn, true);

      const sharedCount = el(
        doc,
        "p",
        {
          class: "mg-shared-count",
          "aria-live": "polite",
          "data-role": "shared-count",
        },
        ["0 pieces shared so far"],
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

      root.appendChild(instructions);
      root.appendChild(pieceCard);
      root.appendChild(shareBtn);
      root.appendChild(sharedCount);
      root.appendChild(timer);
      root.appendChild(status);

      let myPiece: PieceDelivery | null = null;
      let sharedTotal = 0;

      const guard = createSubmissionGuard({
        submit: async (submissionId, payload) =>
          ctx.submit(payload, submissionId).catch(() => ({
            submissionId,
            isAccepted: false,
            rejectionReason: "network",
          })),
      });

      on(shareBtn, "click", async () => {
        if (!myPiece || guard.isPending() || guard.hasSubmitted()) return;
        setDisabled(shareBtn, true);
        const result = await guard.submit({
          action: "share_piece",
          piece_id: myPiece.piece_id,
        });
        if (!result || !result.isAccepted) {
          setDisabled(shareBtn, false);
        } else {
          setText(shareBtn, "Shared");
        }
      });

      const view = doc.defaultView;
      const countdown = useCountdown({
        deadlineAt: ctx.state.deadlineAt,
        view,
        onTick: (remaining) => setText(timer, formatRemaining(remaining)),
      });

      const applyStatus = (state: MiniGameContext["state"]): void => {
        const interactive =
          state.status === "active" && !!myPiece && !guard.hasSubmitted();
        setDisabled(shareBtn, !interactive);
        if (state.status === "timed_out") {
          setText(status, "Time ran out. Watch for the clue.");
          setHidden(status, false);
        } else if (state.status === "completed") {
          setText(status, "All pieces in. Watch for the clue.");
          setHidden(status, false);
        }
      };

      applyStatus(ctx.state);

      return {
        update(state) {
          applyStatus(state);
        },
        handleEvent(event) {
          if (
            event.event_type === "mini_game_piece_delivery" &&
            isPieceDeliveryPayload(event.payload)
          ) {
            myPiece = event.payload;
            setText(pieceBody, myPiece.text ?? `Piece ${myPiece.piece_id}`);
            setHidden(pieceCard, false);
            setDisabled(shareBtn, false);
            return;
          }
          if (event.event_type === "mini_game_piece_shared") {
            sharedTotal += 1;
            setText(sharedCount, `${sharedTotal} pieces shared so far`);
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

      const title = el(doc, "h2", {}, ["Assembling the pieces"]);
      const rules = ctx.definition.rules as
        | { piece_count?: number }
        | undefined;
      const total =
        typeof rules?.piece_count === "number" ? rules.piece_count : 0;

      const progress = el(doc, "div", {
        class: "mg-progress",
        role: "progressbar",
        "aria-valuemin": "0",
        "aria-valuemax": String(total),
        "aria-valuenow": "0",
        "data-role": "progress",
      });
      const progressFill = el(doc, "div", {
        class: "mg-progress-fill",
        "data-role": "progress-fill",
      });
      progress.appendChild(progressFill);

      const counter = el(
        doc,
        "p",
        {
          class: "mg-counter",
          "aria-live": "polite",
          "data-role": "counter",
        },
        [`0 of ${total} pieces submitted`],
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
      root.appendChild(progress);
      root.appendChild(counter);
      root.appendChild(timer);
      root.appendChild(status);

      let shared = 0;
      const view = doc.defaultView;
      const countdown = useCountdown({
        deadlineAt: ctx.state.deadlineAt,
        view,
        onTick: (remaining) => setText(timer, formatRemaining(remaining)),
      });

      const updateProgress = (): void => {
        progress.setAttribute("aria-valuenow", String(shared));
        const percent = total > 0 ? Math.min(100, (shared / total) * 100) : 0;
        progressFill.setAttribute("style", `width: ${percent}%`);
        setText(counter, `${shared} of ${total} pieces submitted`);
      };

      const applyStatus = (state: MiniGameContext["state"]): void => {
        if (state.status === "timed_out") {
          setText(status, "Pieces did not assemble in time.");
          setHidden(status, false);
        } else if (state.status === "completed") {
          setText(status, "All pieces in.");
          setHidden(status, false);
        }
      };

      applyStatus(ctx.state);

      return {
        update(state) {
          applyStatus(state);
        },
        handleEvent(event) {
          if (event.event_type === "mini_game_piece_shared") {
            shared += 1;
            updateProgress();
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
        countLabel: (n) => `${n} pieces shared`,
        countEventType: "mini_game_piece_shared",
      });
    },
  },
});
