const shiftRange = (ch, base, shift) =>
  String.fromCharCode(((ch.charCodeAt(0) - base + shift) % 26) + base);

export function encode(text, shift) {
  shift = ((shift % 26) + 26) % 26;
  return text.replace(/[A-Za-z]/g, (ch) => shiftRange(ch, ch <= "Z" ? 65 : 97, shift));
}

export function decode(text, shift) {
  return encode(text, -shift);
}
