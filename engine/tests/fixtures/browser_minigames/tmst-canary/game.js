/* global CustomEvent, document, window */

(() => {
  "use strict";

  const status = document.querySelector("#status");
  const startButton = document.querySelector("#start");
  const finishButton = document.querySelector("#finish");
  const resetButton = document.querySelector("#reset");
  const inputButtons = [...document.querySelectorAll(".input")];

  let active = false;
  let inputs = [];

  function publish(type, detail = {}) {
    const envelope = {
      bridge: "browser-minigame-canary",
      protocol_version: "1.0",
      type,
      detail,
    };

    window.dispatchEvent(
      new CustomEvent(`browser-minigame:${type}`, { detail: envelope }),
    );
    if (window.parent !== window) {
      window.parent.postMessage(envelope, "*");
    }
  }

  function render(message) {
    status.textContent = message;
    startButton.disabled = active;
    finishButton.disabled = !active;
    inputButtons.forEach((button) => {
      button.disabled = !active;
    });
  }

  function start() {
    active = true;
    inputs = [];
    render("Running");
    publish("start", { state: "running" });
  }

  function input(value) {
    if (!active) return;
    inputs.push(value);
    render(`Recorded ${value}`);
    publish("input", { value, sequence: inputs.length });
  }

  function finish() {
    if (!active) return;
    active = false;
    render("Complete");
    publish("finish", { state: "complete" });
    publish("result", {
      status: "completed",
      input_count: inputs.length,
      last_input: inputs.at(-1) ?? null,
      authoritative: false,
    });
  }

  function reset() {
    active = false;
    inputs = [];
    render("Ready");
    publish("reset", { state: "ready" });
  }

  startButton.addEventListener("click", start);
  finishButton.addEventListener("click", finish);
  resetButton.addEventListener("click", reset);
  inputButtons.forEach((button) => {
    button.addEventListener("click", () => input(button.dataset.value));
  });

  window.BrowserMiniGameCanary = Object.freeze({
    start,
    input,
    finish,
    reset,
  });
})();
