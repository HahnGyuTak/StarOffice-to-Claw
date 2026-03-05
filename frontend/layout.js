// Star Office UI - layout and depth configuration
// All coordinates, depth, and asset paths are managed here
// Avoid magic numbers to reduce regression risk

// Core rules:
// - Transparent assets (e.g., desk) must use .png; opaque assets prefer .webp
// - Depth order: low → sofa(10) → starWorking(900) → desk(1000) → flower(1100)

const LAYOUT = {
  // === Game canvas ===
  game: {
    width: 1280,
    height: 720
  },

  // === Area coordinates ===
  areas: {
    door:        { x: 640, y: 550 },
    writing:     { x: 320, y: 360 },
    researching: { x: 320, y: 360 },
    error:       { x: 1066, y: 180 },
    breakroom:   { x: 640, y: 360 }
  },

  // === Decorations & furniture: position + origin + depth ===
  furniture: {
    // Sofa
    sofa: {
      x: 670,
      y: 144,
      origin: { x: 0, y: 0 },
      depth: 10
    },

    // New desk (transparent PNG required)
    desk: {
      x: 218,
      y: 417,
      origin: { x: 0.5, y: 0.5 },
      depth: 1000
    },

    // Desk flower pot
    flower: {
      x: 310,
      y: 390,
      origin: { x: 0.5, y: 0.5 },
      depth: 1100,
      scale: 0.8
    },

    // Star working in front of desk (rendered below desk)
    starWorking: {
      x: 217,
      y: 333,
      origin: { x: 0.5, y: 0.5 },
      depth: 900,
      scale: 1.32
    },

    // Plants
    plants: [
      { x: 565, y: 178, depth: 5 },
      { x: 230, y: 185, depth: 5 },
      { x: 977, y: 496, depth: 5 }
    ],

    // Posters
    poster: {
      x: 252,
      y: 66,
      depth: 4
    },

    // Coffee machine
    coffeeMachine: {
      x: 659,
      y: 397,
      origin: { x: 0.5, y: 0.5 },
      depth: 99
    },

    // Server room
    serverroom: {
      x: 1021,
      y: 142,
      origin: { x: 0.5, y: 0.5 },
      depth: 2
    },

    // Error bug
    errorBug: {
      x: 1007,
      y: 221,
      origin: { x: 0.5, y: 0.5 },
      depth: 50,
      scale: 0.9,
      pingPong: { leftX: 1007, rightX: 1111, speed: 0.6 }
    },

    // Sync animation
    syncAnim: {
      x: 1157,
      y: 592,
      origin: { x: 0.5, y: 0.5 },
      depth: 40
    },

    // Cat
    cat: {
      x: 94,
      y: 557,
      origin: { x: 0.5, y: 0.5 },
      depth: 2000
    }
  },

  // === Plaque ===
  plaque: {
    x: 640,
    y: 720 - 36,
    width: 420,
    height: 44
  },

  // === Asset loading rules: assets forced to PNG (transparent assets) ===
  forcePng: {
    desk_v2: true // New desk must stay transparent; force PNG
  },

  // === Total asset count (for loading progress bar) ===
  totalAssets: 15
};
