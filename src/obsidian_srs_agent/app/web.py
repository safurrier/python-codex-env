"""FastAPI interface for the Obsidian SRS Agent."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .agent import ObsidianSRSAgent, PipelineConfig, PipelinePreview
from .models import Card, CardGenControls, SourceDoc

LOGGER = logging.getLogger(__name__)

template_dir = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(template_dir))
app = FastAPI(title="Obsidian SRS Agent")
_agent = ObsidianSRSAgent()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "form.html", {})


@app.post("/process", response_class=HTMLResponse)
async def process(
    request: Request,
    vault_path: str = Form(...),
    domain: str = Form(...),
    topic: str = Form(...),
    url: Optional[str] = Form(None),
    raw_text: Optional[str] = Form(None),
    num_cards: int = Form(10),
    difficulty: Optional[str] = Form(None),
    focus_area: Optional[str] = Form(None),
    style: Optional[str] = Form(None),
    confirm: Optional[str] = Form(None),
    cards_payload: Optional[str] = Form(None),
    source_title_hidden: Optional[str] = Form(None),
    source_url_hidden: Optional[str] = Form(None),
):
    if not vault_path:
        raise HTTPException(status_code=400, detail="Vault path is required")
    if not Path(vault_path).expanduser().exists():
        raise HTTPException(status_code=400, detail="Vault path does not exist")
    if not url and not raw_text:
        raise HTTPException(status_code=400, detail="Provide a URL or raw text")

    config = PipelineConfig(
        vault_path=vault_path,
        domain=domain,
        topic=topic,
        url=url or None,
        raw_text=raw_text or None,
        num_cards=num_cards,
        difficulty=difficulty or None,
        focus_area=focus_area or None,
        style=style or None,
    )

    if confirm == "yes":
        if not cards_payload:
            raise HTTPException(status_code=400, detail="Missing card payload for write")
        try:
            parsed = json.loads(cards_payload)
        except json.JSONDecodeError as exc:  # pragma: no cover - handled as HTTP error
            raise HTTPException(status_code=400, detail="Invalid card payload") from exc
        cards = [
            Card(
                front=entry.get("front", ""),
                back=entry.get("back", ""),
                style=entry.get("style", style or "basic"),
                difficulty=entry.get("difficulty", difficulty or "medium"),
                tags=list(entry.get("tags", [])),
            )
            for entry in parsed
            if entry.get("front") and entry.get("back")
        ]
        controls = CardGenControls(
            num_cards=num_cards,
            difficulty=difficulty,
            focus_area=focus_area,
            style=style,
        )
        preview = PipelinePreview(
            cards=cards,
            source=SourceDoc(
                text=raw_text or "",
                title=source_title_hidden or None,
                url=source_url_hidden or url or None,
            ),
            controls=controls,
        )
        try:
            result = _agent.write(preview, config)
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Write failed")
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        message = f"✅ Wrote cards → {result.path}"
        form_values = {
            "vault_path": vault_path,
            "domain": domain,
            "topic": topic,
            "url": url,
            "raw_text": raw_text,
            "num_cards": num_cards,
            "difficulty": difficulty,
            "focus_area": focus_area,
            "style": style,
        }
        return templates.TemplateResponse(
            request,
            "form.html",
            {
                "success": message,
                "written_cards": cards,
                "deck_tag": result.deck_tag,
                "written_path": result.path,
                "form_values": form_values,
            },
        )

    try:
        preview = _agent.generate(config)
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("Processing failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    payload = [
        {
            "front": card.front,
            "back": card.back,
            "style": card.style,
            "difficulty": card.difficulty,
            "tags": card.tags,
        }
        for card in preview.cards
    ]

    return templates.TemplateResponse(
        request,
        "form.html",
        {
            "preview": preview,
            "cards_payload": payload,
            "source_title": preview.source.title,
            "source_url": preview.source.url,
            "form_values": {
                "vault_path": vault_path,
                "domain": domain,
                "topic": topic,
                "url": url,
                "raw_text": raw_text,
                "num_cards": num_cards,
                "difficulty": difficulty,
                "focus_area": focus_area,
                "style": style,
            },
        },
    )

