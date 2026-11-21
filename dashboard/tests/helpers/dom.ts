// Shared setup for the shell's component tests: a happy-dom window, React's
// own client, and small helpers. No browser. Import this file before any file
// that imports react-dom, so the globals exist first.

import { Window as HappyWindow } from "happy-dom";
import type { ReactElement } from "react";

const happy = new HappyWindow({ url: "https://app.test/" });
const globals = globalThis as Record<string, unknown>;
for (const name of [
  "window",
  "document",
  "HTMLElement",
  "Node",
  "Element",
  "Event",
  "MouseEvent",
]) {
  globals[name] = (happy as unknown as Record<string, unknown>)[name];
}
globals.IS_REACT_ACT_ENVIRONMENT = true;

const { act } = await import("react");
const { createRoot } = await import("react-dom/client");

export function setUrl(url: string): void {
  happy.happyDOM.setURL(url);
}

// Lets promises and zero-delay timers run, inside act so React flushes.
export async function settle(rounds = 4): Promise<void> {
  for (let i = 0; i < rounds; i += 1) {
    await act(async () => {
      await new Promise((done) => setTimeout(done, 0));
    });
  }
}

// Types into a text input the way a browser does, so React sees the change.
export async function typeInto(
  input: HTMLInputElement,
  value: string,
): Promise<void> {
  const setter = Object.getOwnPropertyDescriptor(
    Object.getPrototypeOf(input),
    "value",
  )!.set!;
  await act(async () => {
    setter.call(input, value);
    input.dispatchEvent(
      new (globals.Event as typeof Event)("input", { bubbles: true }),
    );
  });
  await settle();
}

export interface Mounted {
  container: HTMLElement;
  text(): string;
  buttons(): HTMLButtonElement[];
  button(label: string): HTMLButtonElement;
  click(label: string): Promise<void>;
  // Clicks the first button whose text contains `part` (for buttons that hold
  // several words, such as a menu item with its label and cost).
  clickContaining(part: string): Promise<void>;
  rerender(element: ReactElement): Promise<void>;
  unmount(): Promise<void>;
}

export async function mount(element: ReactElement): Promise<Mounted> {
  const container = happy.document.createElement(
    "div",
  ) as unknown as HTMLElement;
  happy.document.body.appendChild(container as unknown as Node);
  const root = createRoot(container);
  await act(async () => {
    root.render(element);
  });
  await settle();

  const buttons = () =>
    Array.from(container.querySelectorAll("button")) as HTMLButtonElement[];
  const button = (label: string): HTMLButtonElement => {
    const found = buttons().find((b) => b.textContent?.trim() === label);
    if (!found) {
      throw new Error(
        `no button "${label}"; buttons: ${buttons()
          .map((b) => b.textContent?.trim())
          .join(" | ")}`,
      );
    }
    return found;
  };
  return {
    container,
    text: () => container.textContent ?? "",
    buttons,
    button,
    async click(label) {
      const target = button(label);
      await act(async () => {
        target.dispatchEvent(
          new (globals.MouseEvent as typeof MouseEvent)("click", {
            bubbles: true,
          }),
        );
      });
      await settle();
    },
    async clickContaining(part) {
      const target = buttons().find((b) => b.textContent?.includes(part));
      if (!target) {
        throw new Error(
          `no button containing "${part}"; buttons: ${buttons()
            .map((b) => b.textContent?.trim())
            .join(" | ")}`,
        );
      }
      await act(async () => {
        target.dispatchEvent(
          new (globals.MouseEvent as typeof MouseEvent)("click", {
            bubbles: true,
          }),
        );
      });
      await settle();
    },
    async rerender(next) {
      await act(async () => {
        root.render(next);
      });
      await settle();
    },
    async unmount() {
      await act(async () => {
        root.unmount();
      });
    },
  };
}

// A storage that behaves like localStorage, kept in memory.
export function memoryStorage(): Storage {
  const data = new Map<string, string>();
  return {
    get length() {
      return data.size;
    },
    key: (i: number) => Array.from(data.keys())[i] ?? null,
    getItem: (k: string) => data.get(k) ?? null,
    setItem: (k: string, v: string) => void data.set(k, v),
    removeItem: (k: string) => void data.delete(k),
    clear: () => data.clear(),
  } as Storage;
}
