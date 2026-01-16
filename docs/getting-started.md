# Getting Started with Godot

This guide assumes you have never used Godot before. We'll walk through installing the editor, opening the template project, and understanding the basics of scenes and nodes.

## 1. Install Godot

1. Download **Godot 4.x** from the official site.
2. Launch the editor.
3. When prompted, install **Export Templates** (this enables builds for Windows/macOS/Linux/Web).

> Tip: Godot is portable. You can keep the editor in a folder next to your project if you want a fully self-contained setup.

## 2. Open the Template Project

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/your-godot-game.git
   cd your-godot-game
   ```
2. Open Godot.
3. Click **Import** and choose the `godot/` folder.
4. Godot will detect `project.godot` and import the project.

## 3. Run the Sample Scene

1. In Godot, press **F5** (or click **▶ Play**).
2. The first time you run, Godot may ask you to select a main scene.
3. Choose `godot/scenes/Main.tscn`.

You should see a log message:
```
Godot starter pack loaded.
```

## 4. Godot Basics (Quick Orientation)

- **Scene**: A reusable collection of nodes saved as a `.tscn` file.
- **Node**: A building block (Sprite, Camera, CharacterBody2D, etc.).
- **Scene Tree**: The hierarchy of nodes in the current scene.
- **Inspector**: The panel where you edit node properties.
- **Script**: A GDScript file (`.gd`) attached to a node.

### The Minimal Loop

When a scene starts, Godot calls:
- `_ready()` once when the node enters the scene tree
- `_process(delta)` every frame for logic
- `_physics_process(delta)` at a fixed timestep for physics

## 5. Your First Change (Hello, Godot)

Open `godot/scripts/Main.gd` and update the message:
```gdscript
extends Node2D

func _ready() -> void:
    print("Hello from my first Godot project!")
```

Run the project again to see the new message.

## 6. Next Steps

- Continue to the **Starter Pack Tutorial** to build a playable scene.
- Review **Project Structure** to understand how this template organizes files.
- Explore **Tooling & Exports** to learn how to format scripts and ship builds.
