# Tooling & Exports

This page covers recommended tools and workflows for working on a Godot project.

## Godot Editor Essentials

- **Godot 4.x editor**: primary development tool.
- **Export templates**: required to build playable binaries.

Install templates from **Editor → Manage Export Templates**.

## Recommended Plugins

- **GDUnit4** or **GUT** for automated tests.
- **Dialogic** for narrative-heavy projects.
- **Godot-Redux** or custom input remapping addons for accessibility.

Keep plugins in `godot/addons/` and commit the addon source to version control.

### Installing GUT (Godot Unit Test)

1. Open **AssetLib** inside the Godot editor.
2. Search for **GUT** and click **Download**.
3. Install it to `godot/addons/`.
4. Enable it in **Project Settings → Plugins**.

### Installing GDUnit4

1. Open **AssetLib** inside the Godot editor.
2. Search for **GDUnit4** and click **Download**.
3. Install it to `godot/addons/`.
4. Enable it in **Project Settings → Plugins**.

## GDScript Formatting & Linting

Suggested tools (install via pip or as editor plugins):
- **gdformat** (formatter)
- **gdlint** (lint rules)

Example commands:
```bash
gdformat godot/scripts
gdlint godot/scripts
```

### Install gdformat / gdlint

The formatter and linter live in the `godot-gdscript-toolkit` project:

```bash
pip install godot-gdscript-toolkit
```

If you want isolated tooling for CI, you can install them in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install godot-gdscript-toolkit
```

## Running Godot in Headless Mode

For CI or automated tests, use Godot's headless mode:
```bash
godot --headless --quit --path godot
```

## Exporting Builds

1. Go to **Project → Export**.
2. Add a preset for your target (Windows, macOS, Linux, Web).
3. Configure:
   - Export path
   - Icon
   - Compression and debug settings
4. Click **Export Project**.

Store the `export_presets.cfg` file in your repo so the settings are shared.

## Build Checklist

- ✅ Main scene set in `project.godot`
- ✅ Input actions configured (Project Settings → Input Map)
- ✅ Export presets configured
- ✅ Version metadata in Project Settings
- ✅ Release build tested
