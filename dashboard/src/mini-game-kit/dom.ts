// Minimal DOM helpers used by the kit and by renderers.
// Pure functions; no global state. Safe to call in happy-dom tests.

export type AttrValue = string | number | boolean | null | undefined;

export function el<K extends keyof HTMLElementTagNameMap>(
  doc: Document,
  tag: K,
  attrs?: Record<string, AttrValue>,
  children?: Array<Node | string>,
): HTMLElementTagNameMap[K] {
  const node = doc.createElement(tag);
  if (attrs) {
    for (const [name, value] of Object.entries(attrs)) {
      if (value === null || value === undefined || value === false) continue;
      if (value === true) {
        node.setAttribute(name, "");
        continue;
      }
      node.setAttribute(name, String(value));
    }
  }
  if (children) {
    for (const child of children) {
      if (typeof child === "string") {
        node.appendChild(doc.createTextNode(child));
      } else {
        node.appendChild(child);
      }
    }
  }
  return node;
}

export function on<K extends keyof HTMLElementEventMap>(
  node: HTMLElement,
  event: K,
  handler: (e: HTMLElementEventMap[K]) => void,
  opts?: AddEventListenerOptions,
): () => void {
  node.addEventListener(event, handler as EventListener, opts);
  return () => {
    node.removeEventListener(event, handler as EventListener, opts);
  };
}

export function setText(node: Element, value: string): void {
  if (node.textContent !== value) {
    node.textContent = value;
  }
}

export function setHidden(node: HTMLElement, hidden: boolean): void {
  if (node.hidden !== hidden) {
    node.hidden = hidden;
  }
}

export function setDisabled(node: HTMLButtonElement, disabled: boolean): void {
  if (node.disabled !== disabled) {
    node.disabled = disabled;
  }
}

export function clearChildren(node: Element): void {
  while (node.firstChild) {
    node.removeChild(node.firstChild);
  }
}

export function prefersReducedMotion(view: Window | undefined | null): boolean {
  if (!view || typeof view.matchMedia !== "function") return false;
  try {
    return view.matchMedia("(prefers-reduced-motion: reduce)").matches;
  } catch {
    return false;
  }
}
