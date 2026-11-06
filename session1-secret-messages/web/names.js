// The page hides messages sent under its own name, so every laptop needs a different one.
export function chatName(param, rand = Math.random) {
  return (param || "").trim().slice(0, 20) || `Guest-${1000 + Math.floor(rand() * 9000)}`;
}
