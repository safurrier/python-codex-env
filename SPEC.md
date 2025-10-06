# SPEC.md

## 1. Product overview

**Name:** Obsidian SRS Agent
**Goal:** Given a URL or raw text, extract the main content, generate high-quality spaced-repetition cards via LLM, and write them into an Obsidian vault using the Obsidian Spaced Repetition plugin syntax.
**Primary users:** Knowledge workers/students who read the web and want auto-generated flashcards organized into decks.

---

## 2. Core features & requirements

### 2.1 Inputs

* **URL** (preferred): fetched via **Jina Reader** (`https://r.jina.ai/<URL>`) returning Markdown/plaintext.
* **Raw text**: pasted text area.

### 2.2 Processing

* **Extraction**: Use Jina Reader (no key) → Markdown/text.
* **(Optional) Chunking**: Split long content into ~6–8k chars for generation.
* **Card Generation (LLM)**:

  * Implemented with **BAML** to enforce typed outputs.
  * Controls: `num_cards`, `difficulty` (`easy|medium|hard`), `focus_area` (free text), `style` (`basic|reversed|cloze`).
  * **Provider routing**:

    * **Dev default**: OpenAI **gpt-4o-mini** (uses `OPENAI_API_KEY`).
    * Optionally add a “big” model (e.g., `gpt-4o`) for polishing; keep both defined for easy switching.

### 2.3 Outputs

* **Markdown file(s)** into an **Obsidian vault** folder structure:

  * Folder: `Decks/<domain>/<topic>/`
  * Frontmatter:

    ```yaml
    ---
    title: "<best-effort title or slug>"
    source_url: "<URL or empty>"
    created: YYYY-MM-DD
    sr_deck: true
    ---
    ```
  * Tag: `#deck/<domain>/<topic>`
  * Card lines (Obsidian SR plugin compatible):

    * Basic: `Question::Answer`
    * Reversed: `Question:::Answer`
    * Cloze: `Question::{{c1::…}}` (LLM returns cloze on the right); also accept `==cloze==` if produced.

### 2.4 Web UI

* **FastAPI** app with a simple HTML form:

  * Fields: vault path, domain, topic, URL, text, `num_cards`, `difficulty`, `focus_area`, `style`.
  * POST to `/process` → runs pipeline → returns success with written path.

---

## 3. Architecture

```
obsidian-srs-agent/
  baml/
    cards.baml            # Types + functions + @provider annotations
  app/
    agent.py              # Strands Agent + tools (function wrappers)
    tools.py              # Extraction helpers (Jina Reader), chunking
    vault.py              # Markdown writer for Obsidian
    web.py                # FastAPI frontend (form)
    main.py               # CLI entrypoint (optional)
  baml.yaml               # Provider mapping (openai minis, etc.)
  requirements.txt
  SPEC.md
  PLAN.md
```

**Key libs:**

* **BAML**: Typed prompt functions; OpenAI-compatible providers.
* **Strands Agents**: Agent + Tool abstraction to orchestrate steps.
* **FastAPI**: Minimal UI.
* **Requests**: URL fetch from Jina Reader.
* **python-slugify**: Safe filenames.

---

## 4. Data contracts

### 4.1 BAML schema (conceptual)

```baml
class Card {
  front string
  back string
  tags string[]
  style string       // "basic"|"reversed"|"cloze"
  difficulty string  // "easy"|"medium"|"hard"
}

class CardGenControls {
  num_cards int
  difficulty string?
  focus_area string?
  style string?      // default "basic"
  cloze_hint string?
}

class SourceDoc {
  title string?
  url string?
  text string
}

@provider("openai_mini")
function GenerateSRS(doc: SourceDoc, controls: CardGenControls) -> Card[] @prompt("""...""");

@provider("openai_mini")
function SummarizeForFocus(doc: SourceDoc) -> string @prompt("""...""");
```

### 4.2 Tool interfaces (Strands)

* `fetch_extract(url) -> {title?: str, text: str}`
* `generate_cards(text, title?, url?, num_cards, difficulty?, focus_area?, style?) -> {cards: Card[]}`
* `write_obsidian(vault_root, cards, source_title?, source_url?, domain, topic, file_basename?) -> {path: str}`

---

## 5. Configuration

* **Environment**

  * `OPENAI_API_KEY` (required; we’ll default to `gpt-4o-mini`).
* **baml.yaml**

  ```yaml
  providers:
    openai_mini:
      type: openai
      options:
        model: gpt-4o-mini
        # api key taken from OPENAI_API_KEY env
    openai_big:
      type: openai
      options:
        model: gpt-4o
  ```
* **Runtime flags** (UI/CLI):

  * Vault path, domain, topic, URL/text, num_cards, difficulty, focus_area, style.

---

## 6. UX details

* If both URL and Text are provided, **URL wins** (explicit note under form).
* On success, show the absolute path of the created `.md`.
* Render basic validation errors inline (missing vault path, no content, etc.).

---

## 7. Error handling

* **Network**: timeouts/backoff on Jina Reader; show clear message if non-200.
* **LLM**: if BAML validation fails, retry once with stricter hints; if still failing, show partial results (cards that validated).
* **Filesystem**: ensure folders, catch permission errors, sanitize filenames.

---

## 8. Observability & logs

* Structured logs per request: `request_id`, url/text-size, model name, tokens used (if available), cards_count, file_path.
* Debug logging of raw LLM output behind a flag.

---

## 9. Security & privacy

* Do not store source text or LLM outputs beyond the generated Markdown.
* No analytics by default.
* Clearly warn users that content at private URLs may not be accessible by Jina Reader.

---

## 10. Performance

* Single pass normally; optional chunking for very long docs.
* Parallelization deferred; most latency is the LLM call.

---

## 11. Testing

* **Unit**: vault writer produces correct SR syntax; Jina reader wrapper returns strings; BAML client mocked.
* **Integration**: end-to-end run on 2–3 public URLs; verify deck paths and card counts.

---

## 12. Future work (non-blocking)

* Big-model polishing pass; semantic chunking; dedupe similar cards; CSV/APKG export; background jobs; simple auth for the UI.

---
