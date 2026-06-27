import { useEffect, useState } from "react";
import DisplayScreen from "./screens/DisplayScreen";
import JoinScreen from "./screens/JoinScreen";
import WaitingScreen from "./screens/WaitingScreen";

type Route =
  | { screen: "display"; sessionId: string }
  | { screen: "join" }
  | { screen: "waiting" }
  | { screen: "home" };

function parseRoute(): Route {
  const path = window.location.pathname;
  const displayMatch = path.match(/^\/display\/([^/]+)/);
  if (displayMatch) return { screen: "display", sessionId: displayMatch[1] };
  if (path.startsWith("/join")) return { screen: "join" };
  if (path.startsWith("/waiting")) return { screen: "waiting" };
  return { screen: "home" };
}

export default function App() {
  const [route] = useState<Route>(parseRoute);

  useEffect(() => {
    document.title = "Nightcap";
  }, []);

  if (route.screen === "display") {
    return <DisplayScreen sessionId={route.sessionId} />;
  }
  if (route.screen === "join") {
    return <JoinScreen />;
  }
  if (route.screen === "waiting") {
    return <WaitingScreen />;
  }
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        height: "100vh",
      }}
    >
      <p style={{ color: "var(--text-muted)", fontStyle: "italic" }}>
        Navigate to /display/&lt;session-id&gt; or /join
      </p>
    </div>
  );
}
