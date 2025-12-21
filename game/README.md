# Building Christmas Morning

A magical interactive game that teaches the true spirit of Christmas - it's not about the things you have, but the connections you create.

## About the Game

Build the perfect Christmas morning by placing elements into a cozy living room. Discover that the magic emerges from the invisible web of relationships, shared moments, and emotional connections between people, traditions, and small acts of thoughtfulness.

## Features

### Five Item Categories

1. **People** (6 types) - The heart of everything
   - Child, Parent, Grandparent, Teen, Pet, Partner
   - People react to each other and create moments

2. **Gifts** (8 types) - Catalysts for connection
   - Small, Medium, and Large boxes
   - Gift bags, stockings, handmade gifts
   - Experience gifts and practical items

3. **Decorations** (10 types) - Ambiance amplifiers
   - Christmas tree with ornaments
   - Lights, wreaths, garland, candles
   - Heirloom and handmade ornaments

4. **Comfort** (7 types) - Sensory elements
   - Fireplace, hot cocoa, blankets
   - Fresh breakfast, music, cookies

5. **Traditions** (8 types) - Meaning multipliers
   - Photo albums, storybooks, holiday movies
   - Nativity scenes, letters to Santa
   - Christmas cards and family recipes

### Core Gameplay

- **Drag and Drop**: Place items from the palette into the living room
- **Proximity Interactions**: Items react when placed near each other
- **Connection Energy**: Build meaningful moments to increase energy from 0% to 100%
- **Energy Levels**:
  - Empty (0-10%) - Cool, quiet
  - Decorated (10-30%) - Starting to feel festive
  - Inhabited (30-50%) - Warmth building
  - Connected (50-75%) - Joy and harmony
  - Magic (75-100%) - Peak Christmas spirit

- **Click Interactions**:
  - Unwrap gifts when people are nearby
  - Toggle fireplace, music, and candles
  - Activate traditions like photo albums and movies

### Special Moments (Easter Eggs)

- **Four Generations**: Place child, parent, grandparent, and photo album together
- **Pet's Christmas**: Give a gift to your pet
- **Quiet Moment**: Create an intimate scene with two people, cocoa, and fireplace
- **Handmade Treasure**: Combine handmade ornament, tree, child, and grandparent
- **And more discoveries!**

### Visual Feedback

- Room lighting changes from cool dawn to warm golden morning
- Window frost melts as connection energy increases
- Items glow when creating meaningful interactions
- Snow falls gently outside the window

### Endgame

When you reach 100% connection energy:
- A beautiful endgame message appears
- The room becomes a frozen perfect moment
- The true magic of Christmas is revealed

## Technical Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **React DnD** - Drag and drop with both mouse and touch support
- **Vitest** - Unit testing (12 passing tests)
- **Playwright** - E2E testing
- **ESLint** - Code linting
- **CSS** - Responsive styling with mobile support

## Development

### Zero-Setup Quick Start (Recommended)

On a **fresh dev machine** with no dependencies installed:

```bash
# From the repository root - this handles EVERYTHING automatically:
make game

# That's it! This will:
# ✅ Auto-install Node.js 20 via nvm (if missing)
# ✅ Auto-install all npm dependencies
# ✅ Auto-install Playwright browsers
# ✅ Start the dev server at http://localhost:3000
```

**Customize Node version** (default is 20):
```bash
make game NODE_VERSION=18  # Use Node.js 18 instead
```

### Manual Setup (Alternative)

If you prefer manual control:

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Visit http://localhost:3000
```

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Lint code
npm run type-check   # Run TypeScript type checking
npm run test         # Run unit tests
npm run test:ui      # Run tests with UI
npm run test:e2e     # Run E2E tests
npm run test:e2e:ui  # Run E2E tests with UI
```

### Make Commands (Auto-Install All Dependencies)

All `make` commands automatically ensure Node.js and dependencies are installed:

```bash
make game              # Run the game (starts dev server)
make game-build        # Build for production
make game-lint         # Lint the code
make game-test         # Run unit tests
make game-test-e2e     # Run e2e tests
make game-type-check   # Run type checking
make game-check        # Run all quality checks (lint + type-check + tests)
make game-clean        # Clean build artifacts
```

## Mobile Support

The game is fully responsive and works on:
- Desktop (mouse drag and drop)
- Tablets (touch drag and drop)
- Mobile phones (touch drag and drop with collapsible palette)

On mobile, tap the "🎄 Items" button to open/close the item palette.

## Testing

### Unit Tests (12 passing)
- InteractionSystem: Proximity detection, distance calculations
- EnergySystem: Energy tracking, level progression, visual properties

### E2E Tests (16+ test cases)
- Opening experience verification
- Item placement and interaction
- Energy progression
- Mobile responsiveness
- Design doc compliance
- All 5 item categories
- Connection energy system
- Visual feedback system

## Architecture

```
game/
├── src/
│   ├── components/       # React components
│   │   ├── Room.tsx       # Main game room
│   │   ├── Item.tsx       # Individual items
│   │   └── ItemPalette.tsx # Item selection
│   ├── systems/          # Game logic
│   │   ├── InteractionSystem.ts  # Proximity & reactions
│   │   └── EnergySystem.ts       # Energy tracking
│   ├── types/            # TypeScript types
│   ├── data/             # Item definitions
│   └── styles/           # Global styles
├── e2e/                  # E2E tests
└── public/               # Static assets
```

## Design Philosophy

This game demonstrates that:
- Christmas magic comes from connections, not consumption
- Small moments matter more than expensive gifts
- Every family creates their own unique Christmas
- The best gifts are time, attention, and presence
- Traditions create continuity and meaning

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Optimized for 30-40 active items
- Smooth animations using CSS transforms
- Efficient proximity detection
- Lazy loading where appropriate

## License

Copyright © 2024. All rights reserved.

## Credits

Designed and developed based on comprehensive design documentation focusing on meaningful human connections during the Christmas season.
