import { test } from "node:test";
import assert from "node:assert/strict";
import { encode, decode } from "./caesar.js";

test("uppercase", () => assert.equal(encode("HELLO", 3), "KHOOR"));
test("case kept", () => assert.equal(encode("Hello", 3), "Khoor"));
test("wraps", () => assert.equal(encode("XYZ", 3), "ABC"));
test("non-letters unchanged", () => assert.equal(encode("Grüße 3!", 3), "Juüßh 3!"));
test("emoji unchanged", () => assert.equal(encode("hi 🙂", 1), "ij 🙂"));
test("shift mod 26", () => assert.equal(encode("A", 27), "B"));
test("zero is identity", () => assert.equal(encode("Meet me", 0), "Meet me"));
test("decode inverts every setting", () => {
  for (let s = 0; s < 26; s++) assert.equal(decode(encode("Meet me at 3!", s), s), "Meet me at 3!");
});
test("wrong dial is gibberish", () => assert.equal(decode(encode("HELLO", 3), 5), "FCJJM"));
