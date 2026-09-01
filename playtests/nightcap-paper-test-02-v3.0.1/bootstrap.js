const APP_ROOT = document.querySelector("#app");
const SOURCE_BASE = "/arcwright/nightcap/paper-test-02/v3.0/";
const PATCH_ID = "nightcap-paper-test-02-v3.0.1";
const PATCH_VERSION = "3.0.1";

function showBootError(message) {
  const section = document.createElement("section");
  section.className = "card";
  const heading = document.createElement("h2");
  heading.textContent = "The case file failed to open.";
  const detail = document.createElement("p");
  detail.textContent = String(
    message || "Please reload the page. If it still fails, report this playtest link."
  );
  section.append(heading, detail);
  APP_ROOT.replaceChildren(section);
}

async function bootPatchedFixture() {
  if (!globalThis.DOMPurify) {
    showBootError("A required local runtime asset did not load. Please reload the page.");
    return;
  }

  const nativeFetch = globalThis.fetch.bind(globalThis);
  globalThis.fetch = async (input, init) => {
    const requested = new URL(input, document.baseURI);
    if (
      requested.pathname.endsWith("/nightcap/paper-test-02/v3.0.1/case.json") ||
      requested.pathname.endsWith("/nightcap-paper-test-02-v3.0.1/case.json")
    ) {
      const response = await nativeFetch(`${SOURCE_BASE}case.json`, {
        ...init,
        cache: "no-store"
      });
      if (!response.ok) return response;
      const caseData = await response.json();
      caseData.fixture_id = PATCH_ID;
      caseData.fixture_version = PATCH_VERSION;
      return new Response(JSON.stringify(caseData), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Cache-Control": "no-store"
        }
      });
    }
    return nativeFetch(input, init);
  };

  try {
    await import(`${SOURCE_BASE}app.js`);
  } catch (error) {
    console.error(error);
    showBootError(error?.message);
  } finally {
    globalThis.fetch = nativeFetch;
  }
}

bootPatchedFixture();
