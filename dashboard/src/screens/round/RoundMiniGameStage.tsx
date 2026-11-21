// Loads the package registry lazily so the screen tests can supply a fixture
// renderer without relying on Vite's import.meta.glob transform.

import { useEffect, useRef, useState } from "react";

import { MiniGameStage } from "../../mini-games/MiniGameStage";
import type { MiniGameDefinition, Surface } from "../../mini-game-kit/index";
import type { PerfTransport } from "../../mini-game-kit/perf";
import type { RendererRegistry } from "../../mini-games/registry";
import { copy } from "../../shell/copy";

export interface StageServices {
  registry: RendererRegistry;
  loadDefinition: (
    gameId: string,
    version: string,
  ) => Promise<MiniGameDefinition>;
  fetcher?: typeof fetch;
  perfTransport?: PerfTransport;
}

interface Props {
  surface: Surface;
  sessionId: string;
  participantId: string;
  characterId: string;
  token?: string;
  onStageState: (state: string) => void;
  services?: StageServices;
}

export default function RoundMiniGameStage(props: Props) {
  const container = useRef<HTMLDivElement | null>(null);
  const [services, setServices] = useState<StageServices | null>(
    props.services ?? null,
  );
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    if (!services) return;
    const stage = container.current?.querySelector<HTMLElement>(
      "[data-mini-game-stage]",
    );
    if (!stage) return;
    const observer = new MutationObserver(() => {
      props.onStageState(stage.dataset.miniGameState ?? "idle");
    });
    observer.observe(stage, {
      attributes: true,
      attributeFilter: ["data-mini-game-state"],
    });
    return () => observer.disconnect();
  }, [services, props.onStageState]);

  useEffect(() => {
    if (props.services) {
      setServices(props.services);
      return;
    }
    let cancelled = false;
    void import("../../mini-games/registry-bindings.js")
      .then((bindings) => {
        if (cancelled) return;
        setServices({
          registry: bindings.registerPackageRenderers(),
          loadDefinition: bindings.loadPackageDefinition,
        });
      })
      .catch(() => {
        if (!cancelled) {
          setFailed(true);
          props.onStageState("boot-error");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [props.services, props.onStageState]);

  if (failed) {
    return (
      <p className="sh-error" role="alert">
        {copy.round.failed}
      </p>
    );
  }
  if (!services) return null;
  return (
    <div ref={container}>
      <MiniGameStage
        surface={props.surface}
        sessionId={props.sessionId}
        participantId={props.participantId}
        characterId={props.characterId}
        token={props.token}
        registry={services.registry}
        loadDefinition={services.loadDefinition}
        fetcher={services.fetcher}
        perfTransport={services.perfTransport}
      />
    </div>
  );
}
