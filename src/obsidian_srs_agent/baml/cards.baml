class Card {
  front string
  back string
  tags string[]
  style string
  difficulty string
}

class CardGenControls {
  num_cards int
  difficulty string?
  focus_area string?
  style string?
  cloze_hint string?
}

class SourceDoc {
  title string?
  url string?
  text string
}

@provider("openai_mini")
function GenerateSRS(doc: SourceDoc, controls: CardGenControls) -> Card[] @prompt("""
You are an expert study coach creating high quality spaced repetition flashcards.
Follow these requirements strictly:
- Produce at most {{controls.num_cards}} cards. Never invent information that is not in the source.
- Prefer concise questions and answers that can be reviewed quickly.
- Honour the requested difficulty {{controls.difficulty}} and focus area {{controls.focus_area}}.
- When controls.style is "reversed", emit cards whose back can be swapped with the front.
- When controls.style is "cloze", wrap the occluded text in {{c1::...}} syntax.
- Always output valid JSON matching the schema.
""");

@provider("openai_mini")
function SummarizeForFocus(doc: SourceDoc) -> string @prompt("""
Provide a single paragraph summary of the document that can be used to focus flashcard creation. Mention key topics only.
""");
