// Mounts one mini-game stage. The package's own renderer draws inside the
// section; the loader (client.ts) fetches state, follows events and submits.
// Several stages may be on one page, each with its own game (D-136).
// PackageMiniGameStage.tsx is this stage wired to the packages on disk.

import { useEffect, useRef } from "react";

import type { MiniGameDefinition, Surface } from "../mini-game-kit/index.js";
import { bootMiniGameStage, type StageController } from "./client.js";
import type { PerfTransport } from "../mini-game-kit/perf.js";
import { RendererRegistry } from "./registry.js";
import { StageStates } from "./stage.js";

export interface MiniGameStageProps {
  surface: Surface;
  sessionId: string;
  participantId: string;
  characterId: string;
  token: string;
  baseUrl?: string;
  registry: RendererRegistry;
  loadDefinition: (
    gameId: string,
    version: string,
  ) => Promise<MiniGameDefinition>;
  fetcher?: typeof fetch;
  perfTransport?: PerfTransport;
}

export function MiniGameStage(props: MiniGameStageProps) {
  const ref = useRef<HTMLElement | null>(null);
  const {
    surface,
    sessionId,
    participantId,
    characterId,
    token,
    baseUrl = "",
    registry,
    loadDefinition,
    fetcher,
    perfTransport,
  } = props;

  useEffect(() => {
    const stage = ref.current;
    if (!stage) return;
    let cancelled = false;
    let controller: StageController | null = null;
    void bootMiniGameStage(stage, {
      registry,
      baseUrl,
      sessionId,
      token,
      surface,
      participantId,
      characterId,
      loadDefinition,
      ...(fetcher ? { fetcher } : {}),
      ...(perfTransport ? { perfTransport } : {}),
    }).then(
      (c) => {
        if (cancelled) c.unmount();
        else controller = c;
      },
      () => stage.setAttribute("data-mini-game-state", StageStates.BootError),
    );
    return () => {
      cancelled = true;
      controller?.unmount();
    };
  }, [
    surface,
    sessionId,
    participantId,
    characterId,
    token,
    baseUrl,
    registry,
    loadDefinition,
    fetcher,
    perfTransport,
  ]);

  return (
    <section
      ref={ref}
      className="mini-game-stage"
      data-mini-game-stage=""
      data-surface={surface}
      data-mini-game-state={StageStates.Idle}
      aria-label="Mini-game stage"
    />
  );
}
