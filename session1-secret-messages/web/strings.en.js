// All kid-facing text for the chat page and Eve's TV page.
// To translate: copy this file to strings.de.js and change the import in chat.js and eve.js.
export default {
  chat: {
    title: "Secret Chat",
    youAre: "You are",
    dialLabel: "Wheel setting",
    vpnOn: "VPN on",
    vpnOff: "VPN off",
    placeholder: "Write a secret message…",
    send: "Send",
    sentAs: "sent as",
    lockBadge: "came through the VPN",
    vpnError: "The VPN isn't working, so your message wasn't sent.",
    notSent: "not sent",
    disconnected: "Connecting to the internet…",
    empty: "No messages yet. Say hello!",
  },
  eve: {
    title: "Eve is listening",
    subtitle: "I can see everything that goes over the internet. Can you hide from me?",
    from: "From",
    unknownSender: "???",
    saw: "I saw",
    trying: "Trying wheel setting",
    setting: "Wheel setting",
    guess: "I think you said",
    unlocked: "You didn't even lock it!",
    noCrack: "Hmm… I couldn't crack this one.",
    locked: "I tried all 26 settings… I can't read this!",
    waiting: "Waiting for someone to send a message…",
    disconnected: "Eve lost the internet… reconnecting",
  },
};
