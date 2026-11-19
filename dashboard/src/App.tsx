import { useEffect, useState } from "react";
import DisplayScreen from "./screens/DisplayScreen";
import JoinScreen from "./screens/JoinScreen";
import WaitingScreen from "./screens/WaitingScreen";
import { copy } from "./shell/copy";
import { parseRoute } from "./shell/routes";

export default function App() {
  const [route] = useState(() => parseRoute(window.location));

  useEffect(() => {
    document.title = "Nightcap";
  }, []);

  if (route.page === "display") {
    return <DisplayScreen sessionId={route.sessionId} />;
  }
  if (route.page === "join") {
    return <JoinScreen code={route.code} />;
  }
  if (route.page === "play") {
    return <WaitingScreen />;
  }
  return (
    <div className="tv-center">
      <p className="sh-line">{copy.home}</p>
    </div>
  );
}
