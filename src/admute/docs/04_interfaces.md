# Interfaces

## Public classes
- `MuteActuator` (`src/admute/actuator_base.py`)
  - `mute()` → silence playback.
  - `unmute()` → restore playback.
  - `close()` → optional teardown hook.
- `FFmpegAudioIngestor` (`src/admute/ingest.py`)
  - `stream_frames()` → iterator of `np.ndarray` frames sized by `frame_seconds`.
- `StageADetector` (`src/admute/detector.py`)
  - `classify(frame)` → returns `FrameClassification` using RMS and spectral heuristics.
- `StateMachine` (`src/admute/state_machine.py`)
  - `update(frame_classification)` → optional `Transition` when state changes.
  - `batch_update(iterable)` → convenience helper for simulations/tests.
- `ActuatorController` (`src/admute/control.py`)
  - `mute(reason, origin, force=False)` / `unmute(...)` / `toggle(...)` — deduplicate commands.
  - `snapshot()` → latest `ActuatorStatus` for dashboards.
  - `close()` → pass-through to actuator.
- `WebAppServer` (`src/admute/web_app.py`)
  - `start()` / `stop()` — manage the FastHtml server thread.
  - `address` property → bound host/port once running.

## CLI entrypoint
`python -m admute.runner --config <yaml>`
- Loads YAML, constructs ingestor, detector, state machine, controller, actuator, and optional web app.
- Registers signal handlers for graceful shutdown.

## Configuration schema highlights
- `capture_device`: ffmpeg `-i` target, e.g. `/dev/video0` or `hw:1,0`.
- `detector.min_ad_rms`, `detector.rms_delta_threshold`, `detector.centroid_threshold`, `detector.flatness_threshold` tune heuristics.
- `actuator.type`: `webos` (needs `host`, optional `client_key`, `secure`, `port`) or `cec` (needs `command`, `device`, `volume_step_count`).
- `web_app.host`, `web_app.port`, `web_app.title` control the FastHtml UI exposure.

## Error handling
- `ActuatorError` surfaces failures inside actuators; callers should catch if they add retries.
- The runner logs and exits with status `1` on unhandled exceptions.
