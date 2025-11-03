# Data & State

## In-memory structures
- `FrameClassification(kind, confidence)` — produced per frame; `kind ∈ {"content", "adlike"}`.
- `Transition(from_state, to_state, event, force_unmute)` — emitted when the state machine flips modes.
- `ActuatorStatus(muted, last_reason, origin, updated_at, command_count)` — stored inside the controller for UI display and debouncing.

## Configuration inputs
Values come from YAML passed to `admute.runner`:
- `capture_device`, `ffmpeg_path`, `channels`, `sample_rate`, `frame_seconds` configure ingest.
- `detector` section overrides thresholds (`min_ad_rms`, `rms_delta_threshold`, etc.).
- `actuator` selects `type` (`webos` or `cec`) plus host, credentials, or bus details.
- `ad_max_seconds`, `ad_like_threshold`, `content_like_threshold` tune state-machine behavior.
- Optional `web_app` block exposes the FastHtml server.

## Persisted artefacts
- WebOS actuator optionally stores a client key on disk (path supplied via config).
- No other persistent state is written; recordings and ML artefacts would live in `scratch/` if enabled manually.

## Invariants
- `ActuatorController` updates `command_count` monotonically.
- State machine resets timers whenever it returns to `CONTENT`.
- Force unmute always transitions to `CONTENT` and clears streak counters.
