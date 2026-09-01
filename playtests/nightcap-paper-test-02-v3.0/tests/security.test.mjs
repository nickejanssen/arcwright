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

test("DOMPurify is version-pinned and protected with subresource integrity", () => {
  assert.match(indexSource, /dompurify@3\.4\.10\/dist\/purify\.min\.js/);
  assert.match(
    indexSource,
    /integrity="sha512-zV0\+P1qGCdp57soPEGVEr6xoBBPouKeHMhr5IB979T6DExjQdHZBJcjItIyn\+BkeFU5xl\/8cCW5ZwBUHM0ThOQ=="/
  );
  assert.match(indexSource, /crossorigin="anonymous"/);
});
