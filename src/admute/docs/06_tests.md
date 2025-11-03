# Tests

## Commands
- `python -m pytest` — runs unit and integration simulations (`tests/test_runner_simulation.py`, `tests/test_web_app.py`, etc.).
- `ruff check src tests` — style and lint checks aligned with repository CI.
- `mypy src` — static typing pass over the AdMute modules.

## Layout highlights
- `tests/test_runner_simulation.py` — exercises the ingest/detector/state machine loop with synthetic PCM arrays.
- `tests/test_actuator_webos.py` / `tests/test_actuator_cec.py` — mock out sockets and subprocesses to verify mute command payloads.
- `tests/test_web_app.py` — validates FastHtml rendering and manual control actions.
- `tests/test_state_machine.py` — ensures hysteresis, force-unmute, and streak counters behave as expected.
- `tests/test_detector.py` — sanity-checks heuristics on generated audio blocks.

## Fixtures & utilities
- `RunnerHarness` in `tests/test_runner_simulation.py` fabricates frames without launching ffmpeg.
- `FakeWebSocket` in `tests/test_actuator_webos.py` intercepts JSON payloads for assertion.
- `subprocess_run` monkeypatch in `tests/test_actuator_cec.py` captures command invocations.
