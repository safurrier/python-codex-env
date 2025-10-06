# PLAN.md

## Milestones & deliverables

### M0 — Repo bootstrap (½ day)

* ✅ Create structure, `requirements.txt`, `.env.example`.
* ✅ Write SPEC.md / PLAN.md (this doc).
* ✅ Add Make targets (install, dev, test, run).

**Acceptance:** Repo installs in a fresh venv; `make dev` starts FastAPI; root page loads.

---

### M1 — Extraction + Vault writer (1 day)

* Implement `fetch_and_extract_jina(url)` with timeout/backoff.
* Implement `write_markdown_cards()`:

  * Creates `Decks/<domain>/<topic>/`.
  * Frontmatter + `#deck/<domain>/<topic>`.
  * Emits `Question::Answer`, `Question:::Answer`, cloze line forms.

**Acceptance:** Running a stub pipeline (no LLM) writes a static test note.

---

### M2 — BAML + OpenAI mini routing (1 day)

* Add `baml/cards.baml` with `Card`, `CardGenControls`, `SourceDoc`.
* Prompt for `GenerateSRS` (strict rules: exact count, no hallucinations, cloze rules).
* `baml.yaml` with `openai_mini` (`gpt-4o-mini`) + optional `openai_big`.
* Build client; implement tool `generate_cards` that calls BAML and validates outputs.

**Acceptance:** CLI script can take pasted text and write an `.md` with N cards using `gpt-4o-mini`.

---

### M3 — Strands Agent orchestration (½–1 day)

* Wrap steps as Strands **Tools** and a simple **Agent**.
* Provide imperative path (explicit tool calls) for the web route.

**Acceptance:** Single function drives URL → extraction → cards → vault.

---

### M4 — FastAPI front end (1 day)

* `/` GET renders form (vault, domain, topic, url/text, controls).
* `/process` POST runs the pipeline; returns file path (and a link to go back).
* Basic client-side hints and server-side validation.

**Acceptance:** Manually test 2–3 URLs; files appear under vault; cards render in Obsidian.

---

### M5 — Quality & polish (1 day)

* De-dupe near-identical questions; cap tokens by chunking; ensure difficulty/focus is honored.
* Logging (request_id, model, counts).
* Error pages with friendly messages.

**Acceptance:** “Happy path” plus two common errors (bad URL, empty text) show good UX.

---

## Detailed tasks

1. **Setup**

   * `make venv && make install` targets.
   * `.env.example` with `OPENAI_API_KEY=`.

2. **Extraction**

   * `tools.fetch_and_extract_jina(url)` with:

     * `GET https://r.jina.ai/{url}`, timeout=30s, 1 retry on 429/5xx.
     * Title heuristic: first Markdown `#` header; fallback to hostname slug.
   * Unit test: offline fixture string.

3. **Vault writer**

   * `vault.write_markdown_cards(vault_root, cards, source_title, source_url, domain, topic, file_basename?)`.
   * Ensure idempotency: overwrite same filename; filenames are slugified from title/topic/date.

4. **BAML schema & prompts**

   * Prompt checklist:

     * Exact `num_cards` (or fewer if insufficient content; **never invent**).
     * Single atomic concept per card; back is self-contained.
     * Apply `style`: basic→`::`, reversed→`:::`, cloze→exactly one `{{c1::...}}`.
     * Tags include `focus_area` if provided.
   * Add “repair” guidelines: If output fails schema, retry once with stricter instruction.

5. **Strands**

   * Define three tools; lightweight agent with instructions:

     * If URL present → `fetch_extract` → `generate_cards` → `write_obsidian`.
     * Else (text) → `generate_cards` → `write_obsidian`.

6. **FastAPI**

   * Simple `FORM_HTML`; server-side validation for vault path existence; warn if not.

7. **Testing**

   * Unit tests for writer & parsing; integration test with a known public article.

8. **Docs**

   * README quickstart; screenshots (later).

---

## Risk register & mitigations

* **LLM output drift**: cards sometimes violate syntax → use BAML schema + one retry; post-validate fronts/backs not empty; clamp length.
* **Extraction variance**: some sites lack readable content → show warning and let user paste text.
* **Vault path errors**: permissions/nonexistent path → detect early and show clear error.
* **Token limits**: long docs → chunking with per-chunk quotas and dedupe.

---

## Runbook / commands

```bash
# 0) Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...

# 1) Build BAML client
baml build

# 2) Run web UI
uvicorn app.web:app --reload --port 8000

# 3) CLI example (optional)
python -m app.main \
  --vault "$HOME/Obsidian/Vault" \
  --domain "reading" --topic "ml" \
  --url "https://example.com/article" \
  --num_cards 12 --difficulty medium --focus_area definitions --style basic
```

---

## Acceptance criteria (E2E)

* Given a valid public URL and a vault path, submitting the form:

  * Extracts content (≥1k chars),
  * Generates the requested number of cards using **gpt-4o-mini**,
  * Writes a Markdown file to `Decks/<domain>/<topic>/...md`,
  * Card lines are valid for Obsidian Spaced Repetition,
  * Page shows “✅ Wrote cards → <path>”.

---

## Stretch goals

* “Quality mode” toggle to switch provider to `openai_big`.
* Per-card source sentence (quote) beneath `::Answer` (multi-line format).
* CSV/APKG export button.
* Background jobs + progress page.
* Semantic chunking (sentence/paragraph aware).

---
