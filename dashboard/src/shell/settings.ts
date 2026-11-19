// A phone's own display settings (spec 0095, the Settings screen). They hold
// nothing secret and nothing about the game; they only change how this phone
// draws things.

export type TextSize = "normal" | "large" | "xlarge";
export type MotionPreference = "system" | "always";

export interface Settings {
  textSize: TextSize;
  reduceMotion: MotionPreference;
}

export const DEFAULT_SETTINGS: Settings = {
  textSize: "normal",
  reduceMotion: "system",
};

export const SETTINGS_KEY = "arcwright.settings";

const TEXT_SIZES: readonly TextSize[] = ["normal", "large", "xlarge"];
const MOTION: readonly MotionPreference[] = ["system", "always"];

interface Store {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
}

function defaultStore(): Store | null {
  try {
    return (globalThis as { localStorage?: Store }).localStorage ?? null;
  } catch {
    return null;
  }
}

export function loadSettings(store: Store | null = defaultStore()): Settings {
  try {
    const raw = store?.getItem(SETTINGS_KEY);
    if (!raw) return DEFAULT_SETTINGS;
    const parsed = JSON.parse(raw) as Partial<Settings>;
    return {
      textSize: TEXT_SIZES.includes(parsed.textSize as TextSize)
        ? (parsed.textSize as TextSize)
        : DEFAULT_SETTINGS.textSize,
      reduceMotion: MOTION.includes(parsed.reduceMotion as MotionPreference)
        ? (parsed.reduceMotion as MotionPreference)
        : DEFAULT_SETTINGS.reduceMotion,
    };
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export function saveSettings(
  settings: Settings,
  store: Store | null = defaultStore(),
): void {
  try {
    store?.setItem(SETTINGS_KEY, JSON.stringify(settings));
  } catch {
    // The setting still applies for this visit.
  }
}

// The stylesheet reads these two attributes on the page's root element.
export function applySettings(root: HTMLElement, settings: Settings): void {
  root.setAttribute("data-text-size", settings.textSize);
  root.setAttribute("data-reduce-motion", settings.reduceMotion);
}
