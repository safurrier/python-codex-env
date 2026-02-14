from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import Any

import tomli
import tomli_w

CONFIG_PATH = Path.home() / ".config" / "dread" / "config.toml"


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        return tomli.load(handle)


def save_config(config: dict[str, Any], path: Path = CONFIG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        tomli_w.dump(config, handle)
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def get_token(path: Path = CONFIG_PATH) -> str:
    env = os.getenv("DISCORD_TOKEN")
    if env:
        return env
    config = load_config(path)
    token = config.get("discord", {}).get("token")
    if not token:
        raise RuntimeError("No Discord token configured")
    return token


def set_token(token: str, path: Path = CONFIG_PATH) -> None:
    config = load_config(path)
    config.setdefault("discord", {})["token"] = token
    save_config(config, path)
