import {
  createSubmissionGuard,
  defineRenderer,
  formatRemaining,
  prefersReducedMotion,
  useCountdown,
  type MiniGameContext,
  type SubmissionGuard,
  type SurfaceLifecycle,
} from "@arcwright/mini-game-kit";

type Option = { id: string; label: string };
type Stage = {
  phase: "question" | "reveal";
  index: number;
  total: number;
  kind: "choice" | "sort";
  prompt: string;
  options: Option[];
  answer?: string[];
  correct?: string[];
  scores?: Record<string, number>;
  standing?: string[][];
};
type PlayerView = {
  locked: boolean;
  disabled?: string[];
  pinned?: { id: string; position: number };
};

const GAME_ID = "battle-of-wits";
const TIER_DELAY_MS = 450;

function stageNumber(stage: Stage): number {
  return stage.index * 2 + Number(stage.phase === "reveal");
}

function mount(root: HTMLElement, ctx: MiniGameContext): SurfaceLifecycle {
  const doc = root.ownerDocument;
  const view = doc.defaultView;
  const phone = ctx.surface === "phone";
  let state = ctx.state;
  let stage: Stage | undefined;
  let player: PlayerView | undefined;
  let order: string[] = [];
  let retryAnswer: (() => Promise<void>) | undefined;
  let pending = false;
  let feedback = "";
  let live = true;
  let dragId: string | undefined;
  let resultStart: { phaseEntry: number; time: number } | undefined;
  const revealTimers: ReturnType<typeof setTimeout>[] = [];
  let readyRequested = false;
  let countdown: ReturnType<typeof useCountdown> | undefined;

  function append<K extends keyof HTMLElementTagNameMap>(
    parent: HTMLElement,
    tag: K,
    text = "",
  ): HTMLElementTagNameMap[K] {
    const element = doc.createElement(tag);
    element.textContent = text;
    parent.append(element);
    return element;
  }

  function button(
    parent: HTMLElement,
    label: string,
    handle: () => void,
  ): HTMLButtonElement {
    const element = append(parent, "button", label);
    element.type = "button";
    element.style.minHeight = "44px";
    element.style.paddingInline = "0.75em";
    element.addEventListener("click", handle);
    return element;
  }

  function names(ids: string[]): string {
    return ids.map((id) => state.playerNames?.[id] ?? "Player").join(", ");
  }

  function receiveStage(next: Stage): void {
    if (stage && stageNumber(next) <= stageNumber(stage)) return;
    stage = next;
    order = next.options.map((option) => option.id);
    player = undefined;
    retryAnswer = undefined;
    pending = false;
    dragId = undefined;
    feedback = "";
  }

  function receivePlayer(next: PlayerView): void {
    player = { ...next, locked: next.locked || player?.locked === true };
    const pin = next.pinned;
    if (pin && order[pin.position] !== pin.id) {
      order = order.filter((id) => id !== pin.id);
      order.splice(pin.position, 0, pin.id);
    }
  }

  function lockAnswer(
    answer: { option_id: string } | { order: string[] },
  ): void {
    if (!stage || !player || player.locked || retryAnswer) return;
    const index = stage.index;
    const payload = { action: stage.kind, question_index: index, ...answer };
    let submissionId: string | undefined;
    const guard = createSubmissionGuard({
      submit: (generatedId, input) =>
        ctx.submit(input, (submissionId ??= generatedId)),
    });
    retryAnswer = () => sendAnswer(index, () => guard.submit(payload));
    void retryAnswer();
  }

  async function sendAnswer(
    index: number,
    send: () => ReturnType<SubmissionGuard["submit"]>,
  ): Promise<void> {
    if (pending || state.status !== "active") return;
    pending = true;
    feedback = "";
    render();
    try {
      const result = await send();
      if (!live || stage?.index !== index || stage.phase !== "question") return;
      if (!result) return;
      retryAnswer = undefined;
      if (result.isAccepted) {
        receivePlayer({ ...player, locked: true });
      } else {
        feedback = "Answer was declined. Check your choice and try again.";
      }
    } catch {
      if (live && stage?.index === index && stage.phase === "question") {
        feedback = "Answer could not be confirmed. Try again.";
      }
    } finally {
      if (live && stage?.index === index && stage.phase === "question") {
        pending = false;
        render();
      }
    }
  }

  function move(from: number, to: number): boolean {
    if (from < 0 || to < 0 || to >= order.length || from === to) return false;
    const pin = player?.pinned?.position;
    if (
      pin !== undefined &&
      pin >= Math.min(from, to) &&
      pin <= Math.max(from, to)
    ) {
      return false;
    }
    const [id] = order.splice(from, 1);
    if (id === undefined) return false;
    order.splice(to, 0, id);
    render();
    return true;
  }

  function finishDrag(target: EventTarget | null): void {
    const source = dragId;
    dragId = undefined;
    if (!source || !(target instanceof (view?.Element ?? Element))) return;
    const row = target.closest<HTMLElement>("[data-sort-id]");
    if (row && root.contains(row))
      move(order.indexOf(source), order.indexOf(row.dataset.sortId ?? ""));
  }

  function renderSort(parent: HTMLElement, current: Stage): void {
    const list = append(parent, "ol");
    for (const [index, id] of order.entries()) {
      const label =
        current.options.find((option) => option.id === id)?.label ?? id;
      const row = append(list, "li");
      row.dataset.sortId = id;
      const pinned = player?.pinned?.position === index;
      const disabled = pending || state.status !== "active";
      append(row, "span", pinned ? `${label} (pre-placed)` : label);
      row.draggable = !disabled && !pinned;
      row.addEventListener("dragstart", (event) => {
        dragId = id;
        event.dataTransfer?.setData("text/plain", id);
      });
      row.addEventListener("dragover", (event) => event.preventDefault());
      row.addEventListener("drop", (event) => {
        event.preventDefault();
        finishDrag(row);
      });
      row.addEventListener("dragend", () => {
        dragId = undefined;
      });
      if (!pinned && !disabled) {
        const handle = append(row, "span", "↕");
        handle.setAttribute("aria-hidden", "true");
        handle.style.display = "inline-grid";
        handle.style.placeItems = "center";
        handle.style.minWidth = "44px";
        handle.style.minHeight = "44px";
        handle.style.touchAction = "none";
        handle.addEventListener("pointerdown", (event) => {
          if (event.pointerType === "mouse") return;
          dragId = id;
          handle.setPointerCapture(event.pointerId);
        });
        handle.addEventListener("pointerup", (event) => {
          finishDrag(doc.elementFromPoint(event.clientX, event.clientY));
        });
        handle.addEventListener("pointercancel", () => {
          dragId = undefined;
        });
      }
      for (const [word, offset] of [
        ["up", -1],
        ["down", 1],
      ] as const) {
        const dest = index + offset;
        const labelText = `Move ${label} ${word}`;
        const control = button(row, word === "up" ? "Up" : "Down", () => {
          if (!move(index, dest)) return;
          const controls = [
            ...root.querySelectorAll<HTMLButtonElement>("button"),
          ];
          const next =
            controls.find(
              (item) =>
                item.getAttribute("aria-label") === labelText && !item.disabled,
            ) ??
            controls.find(
              (item) =>
                item.closest("li")?.dataset.sortId === id && !item.disabled,
            );
          next?.focus();
        });
        control.setAttribute("aria-label", labelText);
        control.disabled =
          disabled ||
          pinned ||
          dest < 0 ||
          dest >= order.length ||
          dest === player?.pinned?.position;
      }
    }
    const lock = button(parent, "Lock order", () => {
      lockAnswer({ order: [...order] });
    });
    lock.disabled = pending || state.status !== "active";
  }

  function renderQuestion(parent: HTMLElement, current: Stage): void {
    if (!phone) {
      for (const option of current.options) append(parent, "p", option.label);
      return;
    }
    if (player?.locked) {
      append(parent, "p", "Answer locked");
      return;
    }
    if (!player) {
      append(parent, "p", "Waiting for your question");
      return;
    }
    if (retryAnswer) {
      if (pending) append(parent, "p", "Sending answer");
      else {
        const retry = button(parent, "Retry answer", () => {
          void retryAnswer?.();
        });
        retry.disabled = state.status !== "active";
      }
      return;
    }
    if (current.kind === "sort") {
      renderSort(parent, current);
      return;
    }
    for (const option of current.options) {
      const choice = button(parent, option.label, () => {
        lockAnswer({ option_id: option.id });
      });
      const struck = player.disabled?.includes(option.id) === true;
      if (struck) choice.style.textDecoration = "line-through";
      choice.disabled = struck || pending || state.status !== "active";
    }
  }

  function renderReveal(parent: HTMLElement, current: Stage): void {
    const labels = current.answer?.map(
      (id) => current.options.find((item) => item.id === id)?.label ?? id,
    );
    append(parent, "p", `Correct answer: ${labels?.join(" → ") ?? ""}`);
    if (phone) {
      append(
        parent,
        "p",
        `Your score: ${current.scores?.[ctx.characterId] ?? 0} / ${current.total * 4}`,
      );
      return;
    }
    append(
      parent,
      "p",
      current.correct?.length
        ? `Got it right: ${names(current.correct)}`
        : "No fully correct answers",
    );
    append(parent, "h3", "Running ranking");
    const ranking = append(parent, "ul");
    current.standing?.forEach((tier, index) => {
      append(
        ranking,
        "li",
        `${index + 1}. ${names(tier)} · ${current.scores?.[tier[0] ?? ""] ?? 0} pts`,
      );
    });
  }

  function renderResult(
    parent: HTMLElement,
    hold: NonNullable<MiniGameContext["state"]["resultHold"]>,
  ): void {
    append(parent, "h3", "Final standing");
    if (!phone) {
      if (resultStart?.phaseEntry !== hold.phaseEntry) {
        resultStart = { phaseEntry: hold.phaseEntry, time: Date.now() };
      }
      const elapsed = Date.now() - resultStart.time;
      function revealAfter(element: HTMLElement, step: number): void {
        const wait = step * TIER_DELAY_MS - elapsed;
        if (wait <= 0 || prefersReducedMotion(view)) return;
        element.hidden = true;
        revealTimers.push(
          setTimeout(() => {
            element.hidden = false;
          }, wait),
        );
      }
      const ranking = append(parent, "ul");
      const firstTier = hold.standing[0] ?? [];
      [...hold.standing].reverse().forEach((tier, index) => {
        const row = append(
          ranking,
          "li",
          `${hold.standing.length - index}. ${names(tier)}`,
        );
        revealAfter(row, index);
      });
      if (firstTier.length) {
        const winner = append(
          parent,
          "p",
          `${firstTier.length === 1 ? "Winner" : "Winners"}: ${names(firstTier)}`,
        );
        revealAfter(winner, hold.standing.length);
      }
    }
    append(parent, "p", "Back to the story shortly.");
    const markReady = ctx.markReady;
    if (phone && markReady) {
      const ready = button(parent, "Ready", () => {
        readyRequested = true;
        render();
        void markReady(hold.phaseEntry).catch(() => {
          readyRequested = false;
          feedback = "Ready could not be saved. Try again.";
          render();
        });
      });
      ready.disabled =
        readyRequested || hold.myReady === true || hold.paused === true;
    }
  }

  function render(): void {
    if (!live) return;
    revealTimers.splice(0).forEach(clearTimeout);
    countdown?.cancel();
    root.replaceChildren();
    const panel = append(root, "section");
    if (!phone) panel.style.fontSize = "clamp(1.25rem, 3vw, 2.5rem)";
    const title = append(panel, "h2", "Battle of Wits");
    title.style.marginBlock = "0.25em";
    if (state.status === "paused" || state.resultHold?.paused) {
      append(panel, "p", "Paused");
    } else if (state.deadlineAt) {
      const timer = append(panel, "p");
      timer.setAttribute("aria-label", "Time remaining");
      countdown = useCountdown({
        deadlineAt: state.deadlineAt,
        view,
        onTick: (remaining) => {
          timer.textContent = formatRemaining(remaining);
        },
      });
    }
    if (state.resultHold) {
      renderResult(panel, state.resultHold);
    } else if (stage) {
      append(panel, "p", `Question ${stage.index + 1} of ${stage.total}`);
      append(panel, "h3", stage.prompt);
      if (stage.phase === "reveal") renderReveal(panel, stage);
      else renderQuestion(panel, stage);
    } else {
      append(panel, "p", "Waiting for Battle of Wits");
    }
    if (feedback) append(panel, "p", feedback).setAttribute("role", "status");
  }

  function update(next: MiniGameContext["state"]): void {
    const incoming = next.runtimeState?.stage as Stage | undefined;
    const stale =
      incoming && stage && stageNumber(incoming) < stageNumber(stage);
    state = stale ? { ...next, deadlineAt: state.deadlineAt } : next;
    if (incoming && !stale) {
      receiveStage(incoming);
      if (phone) {
        const own = (
          next.runtimeState?.player as Record<string, PlayerView> | undefined
        )?.[ctx.characterId];
        if (own) receivePlayer(own);
      }
    }
    render();
  }

  update(state);
  return {
    update,
    handleEvent(event) {
      if (event.payload.run_id !== state.runId || state.resultHold) return;
      if (event.event_type === "battle_of_wits_stage") {
        const next = event.payload.stage as Stage | undefined;
        if (!next || (stage && stageNumber(next) <= stageNumber(stage))) return;
        receiveStage(next);
        const deadline = event.payload.deadline_at;
        if (typeof deadline === "string")
          state = { ...state, deadlineAt: deadline };
        render();
      }
      if (
        event.event_type === "battle_of_wits_player" &&
        phone &&
        event.target_player_id === ctx.participantId &&
        stage?.phase === "question" &&
        event.payload.index === stage.index
      ) {
        const own = event.payload.player as PlayerView | undefined;
        if (own) {
          receivePlayer(own);
          render();
        }
      }
    },
    unmount() {
      live = false;
      revealTimers.splice(0).forEach(clearTimeout);
      countdown?.cancel();
      root.replaceChildren();
    },
  };
}

export default defineRenderer({
  gameId: GAME_ID,
  phone: { mount },
  sharedDisplay: { mount },
  host: { mount },
});
