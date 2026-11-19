import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";
import { applySettings, loadSettings } from "./shell/settings";

// Apply a phone's saved text size and motion choice before the first paint.
applySettings(document.documentElement, loadSettings());

const root = document.getElementById("root");
if (!root) throw new Error("No #root element found");
createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
