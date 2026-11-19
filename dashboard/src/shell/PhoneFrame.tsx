import { useState } from "react";
import type { ReactNode } from "react";
import { copy } from "./copy";
import SettingsPanel from "./SettingsPanel";
import type { Settings } from "./settings";
import StartMenu from "./StartMenu";
import type { StartMenuInfo } from "./StartMenu";

interface PhoneFrameProps {
  children: ReactNode;
  // Null where there is no seat yet, so no Menu button is drawn.
  menu: StartMenuInfo | null;
  settings: Settings;
  onSettingsChange: (next: Settings) => void;
  roomCode: string | null;
  joinUrl: string | null;
}

type Open = "none" | "menu" | "settings";

// Every phone screen sits in this frame: the screen, and the Menu button that
// opens the Start menu (spec 0095 Q1, D-133).
export default function PhoneFrame(props: PhoneFrameProps) {
  const [wanted, setOpen] = useState<Open>("none");
  // With no menu (the game is gone) nothing stays open, so the screen and its
  // way back are shown.
  const open: Open = props.menu ? wanted : "none";

  return (
    <div className="sh-phone">
      <header className="sh-phone-bar">
        <span className="sh-brand">{copy.brand}</span>
        {props.menu && open === "none" && (
          <button
            type="button"
            className="sh-button sh-button-small"
            onClick={() => setOpen("menu")}
          >
            {copy.menu.button}
          </button>
        )}
      </header>

      {open === "none" && (
        <main className="sh-phone-body">{props.children}</main>
      )}

      {open === "menu" && props.menu && (
        <StartMenu
          {...props.menu}
          onOpenSettings={() => setOpen("settings")}
          onClose={() => setOpen("none")}
        />
      )}
      {open === "settings" && (
        <SettingsPanel
          settings={props.settings}
          onChange={props.onSettingsChange}
          roomCode={props.roomCode}
          joinUrl={props.joinUrl}
          onBack={() => setOpen("menu")}
        />
      )}
    </div>
  );
}
