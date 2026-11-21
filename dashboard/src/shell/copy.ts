// Every fixed word the shell screens show, in one place so it is reviewed in
// one place (spec 0095 Part L). Square-bracket values are filled in by the
// screens. No internal name or ID is ever part of these words.

export const copy = {
  brand: "NIGHTCAP",
  unnamedPlayer: "Guest",
  home: "Open /join on a phone or /display/<game> on the TV.",

  tv: {
    joinOnPhone: "Join on your phone",
    roomCode: "Room code",
    needsPlayers: (min: number) => `Needs ${min} or more players to start.`,
    readyToStart: (seated: number) =>
      `${seated} seated. The host can start the game.`,
    atTheTable: "At the table:",
    connecting: "Connecting...",
    cannotReach: "Cannot reach the game. Trying again.",
    gameGone: "This game is no longer running.",
    playContinues: "Play continues.",
    gameOver: "The game has ended.",
    paused: "Paused",
    timeLeft: (clock: string) => `${clock} left in this part`,
    qrAlt: "QR code to join",
  },

  join: {
    nameLabel: "Your name",
    codeLabel: "Room code",
    submit: "Join",
    joining: "Joining...",
    errors: {
      noName: "Enter your name.",
      noCode: "Enter the room code.",
      badCode: "That code did not work. Check the TV.",
      started: "This game has started. Use the phone you joined with.",
      failed: "Something went wrong. Try again.",
      cannotSave:
        "This phone would not save your seat. Allow this site to store data, then tap Join again.",
    },
    resuming: "Finding your seat...",
  },

  seated: {
    youAreIn: (name: string) => `You are in, ${name}.`,
    waitingForHost: "Waiting for the host to start. Look at the TV.",
    atTheTable: (names: string) => `At the table: ${names}`,
    eyesOnTv: "Eyes on the TV.",
    gameOver: "The game has ended.",
    gameGone: "This game is no longer running.",
    joinAgain: "Join another game",
  },

  paused: {
    phone: "Paused. Tap Menu, then Resume, when everyone is back.",
  },

  menu: {
    button: "Menu",
    title: "Menu",
    close: "Close",
    pause: "Pause",
    resume: "Resume",
    settings: "Settings",
    startGame: "Start game",
    moveOn: "Move on",
    finishMiniGame: "Finish mini-game now",
    cancelMiniGame: "Cancel mini-game",
    endGame: "End game",
    handOver: "Make someone else host",
    working: "Working...",
    notAllowed: "Only the host can do that for now.",
    failed: "That did not work. Try again.",
    needsPlayers: (min: number) => `Needs ${min} or more players.`,
  },

  confirm: {
    moveOn: {
      text: "Move on now? This locks every saved theory.",
      yes: "Lock and move on",
      no: "Keep waiting",
    },
    endGame: {
      text: "End the game for everyone? It cannot be restarted.",
      yes: "End game",
      no: "Keep playing",
    },
  },

  // The round screens (AW-332, the approved sample on issue #435). Square
  // brackets in the sample are filled in by the screens. The case and the arc
  // file supply the round title, the lines, the subject and choice labels and
  // the notebook text.
  round: {
    ready: "Ready:",
    readyWord: "ready",
    notReadyWord: "not yet",
    speaker: (name: string) => `${name}:`,
    investigateOnPhones: "Investigate on your phones.",
    eyesUp: "Eyes on the TV.",
    imReady: "I'm ready",
    readyWaiting: "Ready. Waiting for the others.",
    whoYouAre: "Who you are",
    lookInto: "Look into:",
    left: (n: number) => `${n} left`,
    isNew: "new",
    isSeen: "seen",
    kinds: {
      person: "Person",
      place: "Place",
      object: "Object",
      record: "Record",
    } as Readonly<Record<string, string>>,
    spend: (cost: number, left: number) => `Spend ${cost} of your ${left}?`,
    spendIt: "Spend it",
    notNow: "Not now",
    noneLeft: "No investigations left. You can still reread.",
    failed: "That did not work. Try again.",
    timesUp: "Time's up. It's in your notebook.",
    saved: "Saved to your notebook.",
    backToList: "Back to the list",
    tabNow: "Now",
    tabNotebook: "Notebook",
    ok: "OK",
    gettingGameReady: "Getting the game ready...",
    earnedInvestigation: "You earned one more investigation.",
    noMiniGameInProgress: "No mini-game in progress.",
    miniGameUnavailable: "Could not reach the mini-game.",
  },

  notebook: {
    title: "Notebook",
    found: (n: number) => `${n} found`,
    atTheStart: "At the start",
    round: (n: number, title: string | null) =>
      title ? `Round ${n}: ${title}` : `Round ${n}`,
    empty: "Nothing yet. Look into something.",
  },

  settings: {
    title: "Settings",
    back: "Back",
    textSize: "Text size",
    textSizes: { normal: "Normal", large: "Large", xlarge: "Extra large" },
    reduceMotion: "Reduce motion",
    motion: { system: "Follow my phone", always: "Always" },
    roomCode: (code: string) => `Room code: ${code}`,
    rejoinLink: "Rejoin link",
    copyLink: "Copy link",
    copied: "Copied",
  },
} as const;
