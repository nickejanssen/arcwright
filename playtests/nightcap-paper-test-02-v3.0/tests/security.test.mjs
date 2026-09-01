import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const appSource = fs.readFileSync(path.join(here, "..", "app.js"), "utf8");
const indexSource = fs.readFileSync(path.join(here, "..", "index.html"), "utf8");

test("dynamic HTML passes through DOMPurify before reaching innerHTML", () => {
  assert.match(appSource, /DOMPurify\.sanitize\(String\(value\)/);
  assert.match(appSource, /const app = sanitizedHtmlTarget\(document\.querySelector\("#app"\)\)/);
  assert.match(appSource, /const notebook = sanitizedHtmlTarget\(document\.querySelector\("#notebook"\)\)/);
});

test("runtime sanitizer is same-origin and does not require a third-party CDN", () => {
  assert.doesNotMatch(indexSource, /<script[^>]+src="https?:\/\//i);
  assert.match(indexSource, /src="\/arcwright\/vendor\/dompurify-3\.4\.14\.min\.js"/);
});

test("boot failure rendering does not depend on DOMPurify", () => {
  assert.match(appSource, /function renderFatalBootError\(/);
  assert.match(appSource, /renderFatalBootError\(error\)/);
  assert.match(appSource, /replaceChildren\(/);
});
