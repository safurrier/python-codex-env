# Project Structure

This template keeps the Godot project in a dedicated `godot/` directory so that repository-level docs, scripts, and tooling stay separate from game content.

## Recommended Layout

```
Godot Game Template/
├── godot/                       # Godot project root
│   ├── project.godot             # Project settings
│   ├── scenes/                   # Scene files (.tscn)
│   │   ├── Main.tscn
│   │   └── player/               # Feature-focused scenes
│   ├── scripts/                  # GDScript files (.gd)
│   ├── assets/                   # Art, audio, fonts
│   ├── ui/                       # UI scenes and scripts
│   ├── levels/                   # Level scenes or tilemaps
│   ├── autoload/                 # Global singletons
│   └── addons/                   # Plugins (GDUnit4, GUT, etc.)
├── docs/                         # Documentation
└── README.md
```

## Key Ideas

### Scenes are Building Blocks
Use small, reusable scenes:
- **Player.tscn** for the player
- **Enemy.tscn** for enemies
- **HUD.tscn** for UI

### Scripts Live Next to Scenes
Keep scripts close to the scenes they control:
```
scenes/player/Player.tscn
scripts/player/Player.gd
```

### Autoloads for Globals
Use `autoload/` for global managers (Audio, GameState, SceneLoader). Register them in **Project Settings → Autoload**.

### Asset Organization
Organize assets by type or feature:
```
assets/audio/
assets/sprites/
assets/fonts/
```

## Naming Conventions

- **Scenes**: `PascalCase.tscn` (e.g., `Player.tscn`)
- **Scripts**: `PascalCase.gd` or `snake_case.gd`
- **Folders**: `snake_case` or feature-based

## Version Control Tips

- Commit `.tscn`, `.gd`, `.tres`, `.import` settings as needed.
- Ignore `.godot/` and generated import artifacts (already in `.gitignore`).
- Consider Git LFS for large binary assets (audio, textures, models).
