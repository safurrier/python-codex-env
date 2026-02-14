from __future__ import annotations

import json


def render_json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True, default=str)


def message_preview(content: str, max_len: int = 80) -> str:
    clean = content.replace("\n", " ")
    if len(clean) <= max_len:
        return clean
    return f"{clean[: max_len - 1]}…"
