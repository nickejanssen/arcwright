import { useState } from "react";
import { copy } from "./copy";
import type {
  MotionPreference,
  Settings as SettingsValue,
  TextSize,
} from "./settings";

interface SettingsProps {
  settings: SettingsValue;
  onChange: (next: SettingsValue) => void;
  roomCode: string | null;
  joinUrl: string | null;
  onBack: () => void;
}

const TEXT_SIZES: TextSize[] = ["normal", "large", "xlarge"];
const MOTION: MotionPreference[] = ["system", "always"];

export default function SettingsPanel(props: SettingsProps) {
  const { settings, onChange } = props;
  const [copied, setCopied] = useState(false);

  async function copyLink() {
    if (!props.joinUrl) return;
    try {
      await navigator.clipboard.writeText(props.joinUrl);
      setCopied(true);
    } catch {
      // The link is also shown in full, so it can be copied by hand.
    }
  }

  return (
    <div role="dialog" aria-modal="true" aria-label={copy.settings.title}>
      <h2 className="sh-heading">{copy.settings.title}</h2>

      <fieldset className="sh-group">
        <legend>{copy.settings.textSize}</legend>
        {TEXT_SIZES.map((size) => (
          <label key={size} className="sh-choice">
            <input
              type="radio"
              name="text-size"
              checked={settings.textSize === size}
              onChange={() => onChange({ ...settings, textSize: size })}
            />
            {copy.settings.textSizes[size]}
          </label>
        ))}
      </fieldset>

      <fieldset className="sh-group">
        <legend>{copy.settings.reduceMotion}</legend>
        {MOTION.map((choice) => (
          <label key={choice} className="sh-choice">
            <input
              type="radio"
              name="reduce-motion"
              checked={settings.reduceMotion === choice}
              onChange={() => onChange({ ...settings, reduceMotion: choice })}
            />
            {copy.settings.motion[choice]}
          </label>
        ))}
      </fieldset>

      {props.roomCode && (
        <p className="sh-line">{copy.settings.roomCode(props.roomCode)}</p>
      )}
      {props.joinUrl && (
        <div className="sh-group">
          <p className="sh-line">{copy.settings.rejoinLink}</p>
          <p className="sh-link">{props.joinUrl}</p>
          <button type="button" className="sh-button" onClick={copyLink}>
            {copied ? copy.settings.copied : copy.settings.copyLink}
          </button>
        </div>
      )}

      <button
        type="button"
        className="sh-button sh-button-quiet"
        onClick={props.onBack}
      >
        {copy.settings.back}
      </button>
    </div>
  );
}
