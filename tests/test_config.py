from __future__ import annotations

import stat
from pathlib import Path

from dread.config import get_token, set_token


def test_set_and_get_token_from_file(tmp_path: Path) -> None:
    config = tmp_path / "config.toml"
    set_token("abc", path=config)
    assert get_token(path=config) == "abc"
    mode = stat.S_IMODE(config.stat().st_mode)
    assert mode == 0o600
