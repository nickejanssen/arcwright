// A mini-game stage wired to every package under nightcap/mini_games/: the
// package's own renderer is found by the game ID the engine reports.

import { MiniGameStage, type MiniGameStageProps } from "./MiniGameStage.js";
import {
  loadPackageDefinition,
  registerPackageRenderers,
} from "./registry-bindings.js";

export function PackageMiniGameStage(
  props: Omit<MiniGameStageProps, "registry" | "loadDefinition">,
) {
  return (
    <MiniGameStage
      {...props}
      registry={registerPackageRenderers()}
      loadDefinition={loadPackageDefinition}
    />
  );
}
