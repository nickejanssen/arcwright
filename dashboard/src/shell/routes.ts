// Which page a link opens. The TV page carries the game in its address
// (it is on the TV, not a secret); the phone pages carry no ID at all.

export type Route =
  | { page: "display"; sessionId: string }
  | { page: "join"; code: string }
  | { page: "play" }
  | { page: "home" };

export function parseRoute(location: {
  pathname: string;
  search: string;
}): Route {
  const { pathname, search } = location;
  const display = pathname.match(/^\/display\/([^/]+)/);
  if (display) return { page: "display", sessionId: display[1] };
  // "/waiting" is the old phone address; it goes to the phone page.
  if (pathname.startsWith("/play") || pathname.startsWith("/waiting")) {
    return { page: "play" };
  }
  if (pathname.startsWith("/join") || pathname === "/") {
    const code = new URLSearchParams(search).get("code") ?? "";
    return { page: "join", code: code.toUpperCase() };
  }
  return { page: "home" };
}
