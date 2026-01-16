# Godot Game Project Template

A collaborative template for building Godot games with a clean project layout, starter scene, and documentation aimed at first-time Godot developers.

## Features
- 🎮 **Godot 4 starter project** with a ready-to-run `Main` scene
- 🧭 **Beginner-friendly docs** covering editor basics, scenes, nodes, and GDScript
- 📁 **Opinionated folder layout** for scenes, scripts, assets, and addons
- 🚀 **Export + release guidance** for desktop and web builds
- 🧰 **Suggested tooling** for formatting, linting, and automated checks

## Quickstart

1. **Install Godot 4**
   - Download Godot 4.x from the official website.
   - On first launch, install export templates when prompted.

2. **Open the template project**
   ```bash
   git clone https://github.com/your-username/your-godot-game.git
   cd your-godot-game
   ```

3. **Launch the project in Godot**
   - Open Godot.
   - Click **Import** and select the `godot/` folder.
   - The project should detect `project.godot` automatically.

4. **Run the sample scene**
   - Press **F5** or click **▶ Play**.
   - You should see the output log message: `Godot starter pack loaded.`

## Project Layout

```
your-godot-game/
├── godot/                   # Godot project root
│   ├── project.godot         # Godot project settings
│   ├── scenes/               # Scene files (.tscn)
│   ├── scripts/              # GDScript files (.gd)
│   ├── assets/               # Art, audio, fonts
│   └── addons/               # Plugins (GUT, GDUnit4, etc.)
├── docs/                     # Documentation
└── README.md
```

## Documentation

The documentation is meant to be a starter pack for first-time Godot users. Key sections include:
- **Getting Started**: install Godot, open the project, run the first scene
- **Starter Pack Tutorial**: build a small playable scene with movement
- **Project Structure**: learn how to organize scenes, scripts, assets, and autoloads
- **Tooling & Exports**: format scripts, run tests, build release exports

Run the docs locally (optional):
```bash
make docs-serve
```

## Recommended Next Steps

- Replace the placeholder `Main.tscn` scene with your own gameplay scene.
- Add player movement, camera, and collision as described in the tutorial.
- Create export presets and build your first release.

For full guidance, see the docs in `docs/`.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
