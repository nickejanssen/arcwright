// Node 20 (the version CI uses) has no global `navigator`; Node 21 and later
// do. react-dom reads navigator.userAgent when it loads, so the test processes
// preload this file. It adds nothing on newer Node, and the tests that need a
// browser still build their own happy-dom window.
if (typeof globalThis.navigator === "undefined") {
  globalThis.navigator = { userAgent: "node" };
}
