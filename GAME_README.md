# 🎮 The Button Must Be Clicked 🎮

A progressively absurd web-based button clicking game built with Flask and TDD!

## 🎯 What is this?

A creative, fun, and stupid web app game where you click a button... but the button has *opinions*.

As you progress through levels, the button becomes increasingly uncooperative, developing different personalities:
- **Level 1**: Cooperative 😊 - "Thanks for clicking!"
- **Level 2-3**: Reluctant 😐 - "Fine..."
- **Level 4-5**: Annoyed 😒 - "Again?!"
- **Level 6-7**: Sarcastic 🙄 - "Oh wow, you clicked me. So impressive."
- **Level 8-9**: Angry 😡 - "STOP IT!"
- **Level 10-12**: Begging 🥺 - "Please... no more..."
- **Level 13+**: Chaotic 🌀 - Complete madness!

## ✨ Features

- **Progressive Difficulty**: Button changes personality every few levels
- **Visual Chaos**: Button changes colors, sizes, shakes, spins, and moves around
- **Button Refuses Clicks**: At higher levels, the button sometimes refuses to be clicked
- **Combo System**: Click quickly for combo bonuses
- **Sound Effects**: Dynamic audio feedback using Web Audio API
- **Sassy Messages**: Button insults, pleads, and comments on your life choices
- **Beautiful UI**: Gradient backgrounds, smooth animations, and modern design

## 🧪 Test-Driven Development

Built with comprehensive TDD coverage:
- **20 passing tests**
- **83% code coverage**
- Tests for game logic, Flask routes, and button behaviors

```bash
# Run tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing
```

## 🚀 Quick Start

```bash
# Install dependencies
uv sync

# Run the game
uv run python src/app.py
```

Then open your browser to `http://localhost:5000`

## 🎮 How to Play

1. Click the button
2. Watch it get progressively more upset
3. Try to maintain your combo for bonus points
4. Question your life choices
5. Keep clicking anyway

## 🏗️ Architecture

### Backend (Python + Flask)
- `src/button_game.py` - Core game logic with different button moods
- `src/app.py` - Flask web server with REST API
- Session-based game state management

### Frontend (HTML + CSS + JS)
- Responsive design with gradient backgrounds
- CSS animations for button effects
- Web Audio API for sound effects
- Fetch API for real-time game updates

### Tests
- `tests/test_button_game.py` - Game logic tests
- `tests/test_app.py` - Flask API tests

## 📊 Stats

The game tracks:
- Total clicks
- Score (with combo bonuses)
- Current level
- Combo multiplier

## 🎨 Button Personalities

Each mood affects:
- Button text
- Button color
- Button size
- Animations (shake, spin, pulse)
- Position (button moves around the screen)
- Click refusal rate

## 🤪 Why?

Because sometimes you need to build something completely ridiculous to practice TDD, Flask, and web development. This project demonstrates:
- Comprehensive unit testing
- Flask REST API design
- Session management
- Frontend/backend integration
- CSS animations
- Web Audio API

## 📝 License

MIT - Do whatever you want with this silly game!
