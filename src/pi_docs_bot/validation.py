"""Doc system detection and validation plan construction."""

from __future__ import annotations

import json
from pathlib import Path

from .models import DocSystemInfo, PiDocsConfig, ValidationPlan


def detect_doc_systems(repo_root: Path, config: PiDocsConfig) -> DocSystemInfo:
    """Detect documentation systems and recommended commands."""

    systems: list[str] = []
    notes: list[str] = []
    build_command = config.doc_build_command
    lint_command = config.doc_lint_command

    if (repo_root / "mkdocs.yml").exists():
        systems.append("mkdocs")
        build_command = build_command or "mkdocs build --strict"
    if (repo_root / "docs" / "conf.py").exists():
        systems.append("sphinx")
        build_command = build_command or "sphinx-build -b html docs docs/_build/html"

    package_json = repo_root / "package.json"
    if package_json.exists():
        scripts = _read_package_scripts(package_json)
        if "docs:build" in scripts:
            systems.append("docusaurus")
            build_command = build_command or "npm run docs:build"
        if "docs:lint" in scripts:
            lint_command = lint_command or "npm run docs:lint"

    if not systems:
        notes.append("No doc system detected")

    return DocSystemInfo(
        systems=tuple(systems),
        build_command=build_command,
        lint_command=lint_command,
        notes=tuple(notes),
    )


def build_validation_plan(repo_root: Path, config: PiDocsConfig) -> ValidationPlan:
    """Return a validation plan from detection and config."""

    info = detect_doc_systems(repo_root, config)
    return ValidationPlan(
        build_command=info.build_command,
        lint_command=info.lint_command,
        detected_systems=info.systems,
    )


def _read_package_scripts(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if isinstance(data, dict) and isinstance(data.get("scripts"), dict):
        return {str(k): str(v) for k, v in data["scripts"].items()}
    return {}
