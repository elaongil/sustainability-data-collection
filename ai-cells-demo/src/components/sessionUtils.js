import { v4 as uuidv4 } from "uuid";

const SESSION_KEY = "app_session_id";

export function getSessionId() {
  // Check if the session ID exists
  let sessionId = sessionStorage.getItem(SESSION_KEY);

  if (!sessionId) {
    sessionId = uuidv4();
    sessionStorage.setItem(SESSION_KEY, sessionId);
    console.log("New session ID created:", sessionId);
  }

  return sessionId;
}
