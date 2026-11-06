import { test } from "node:test";
import assert from "node:assert/strict";
import { chatName } from "./names.js";

test("uses the given name, trimmed and capped at 20", () => {
  assert.equal(chatName("  Alice "), "Alice");
  assert.equal(chatName("x".repeat(30)), "x".repeat(20));
});

test("missing name gets a unique guest name, so two laptops still see each other", () => {
  assert.equal(chatName(null, () => 0.4821), "Guest-5338");
  assert.equal(chatName("   ", () => 0), "Guest-1000");
  assert.notEqual(chatName(null, () => 0.1), chatName(null, () => 0.2));
});
