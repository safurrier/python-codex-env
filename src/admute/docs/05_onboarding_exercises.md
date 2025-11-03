# Onboarding Exercises

1. **Trace the simulated ad pod**
   - Open `tests/test_runner_simulation.py`.
   - Follow `test_full_ad_pod_flow` from the synthetic frames through `run_pipeline`.
   - Set a breakpoint or add `print` in `StageADetector.classify` to observe confidence swings.

2. **Inspect state machine hysteresis**
   - Run `pytest tests/test_state_machine.py -k hysteresis` (covers multiple streak cases).
   - Modify `ad_like_threshold` in the fixture to see how transitions change.
   - Re-run the test to confirm expectations.

3. **Exercise the FastHtml control panel**
   - Execute `pytest tests/test_web_app.py` to see how the UI responds to controller updates.
   - Read `_render_page` in `src/admute/web_app.py` to understand the displayed metadata.

4. **Swap actuators in config**
   - Edit a copy of `configs/local.yaml`, set `actuator.type: cec` and tweak `volume_step_count`.
   - Run `pytest tests/test_actuator_cec.py` to verify command batching logic.

5. **Validate detector thresholds on new audio**
   - Use `python -m pytest tests/test_detector.py` to run synthetic heuristic checks.
   - Drop a short PCM snippet into a temporary test and adjust `DetectorConfig` values until the classification matches expectations.
