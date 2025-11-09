"""Utilities for discovering and selecting Google Cloud projects."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections.abc import Iterable
from importlib import import_module

from rich.console import Console
from rich.progress import Progress


def list_projects(console: Console) -> list[str]:
    """Return a list of active projects visible to ``gcloud``."""

    gcloud_executable = shutil.which("gcloud")
    if not gcloud_executable:  # pragma: no cover - dependent on environment
        console.print(
            "[yellow]Warning: gcloud is not available; project discovery is disabled.[/yellow]"
        )
        return []

    try:
        subprocess.run(  # noqa: S603
            [gcloud_executable, "--version"], capture_output=True, check=True
        )
    except Exception as exc:  # pragma: no cover - dependent on environment
        console.print(
            "[yellow]Warning: gcloud is not available; project discovery is "
            "disabled.[/yellow]"
        )
        console.print(str(exc))
        return []

    try:
        with Progress(console=console, transient=True) as progress:
            task = progress.add_task("[cyan]Fetching projects...", total=None)
            result = subprocess.run(  # noqa: S603
                [gcloud_executable, "projects", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True,
            )
            progress.update(task, completed=100)
    except Exception as exc:  # pragma: no cover - dependent on environment
        console.print(
            "[yellow]Warning: Unable to retrieve project list. Falling back "
            "to configured defaults.[/yellow]"
        )
        console.print(str(exc))
        return []

    data = json.loads(result.stdout)
    return [
        item["projectId"] for item in data if item.get("lifecycleState") == "ACTIVE"
    ]


def filter_projects(projects: Iterable[str], query: str) -> list[str]:
    """Return projects whose identifiers match ``query`` (case insensitive)."""

    if not query:
        return list(projects)

    pattern = re.compile(f".*{re.escape(query)}.*", re.IGNORECASE)
    return [project for project in projects if pattern.match(project)]


def interactive_project_selection(console: Console, projects: list[str]) -> str:
    """Prompt the user to select a project from ``projects``."""

    if not projects:
        raise ValueError("No projects available for selection")

    if len(projects) == 1:
        return projects[0]

    try:
        inquirer = import_module("InquirerPy").inquirer
    except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "Interactive selection requires InquirerPy. Install the optional "
            "'cli' dependencies or specify --project explicitly."
        ) from exc

    selection = inquirer.select(  # pragma: no cover - requires interactive terminal
        message="Select GCP project:",
        choices=projects,
        default=projects[0],
    ).execute()
    return str(selection)
