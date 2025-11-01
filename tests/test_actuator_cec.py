"""Tests for the HDMI-CEC actuator."""

from __future__ import annotations

from src.admute.actuator_cec import CECActuator, CECConfig


def test_cec_actuator_sends_expected_commands() -> None:
    calls: list[list[str]] = []

    def fake_runner(args: list[str], *, input: bytes | None, check: bool) -> None:
        del check
        assert input is not None
        calls.append([*args, input.decode().strip()])

    actuator = CECActuator(CECConfig(volume_step_count=3), runner=fake_runner)
    actuator.mute()
    actuator.unmute()

    expected_prefix = ["cec-client", "-s", "-d", "1"]
    assert len(calls) == 6
    assert all(call[:4] == expected_prefix for call in calls)
    assert calls[0][-1] == "volumedown"
    assert calls[-1][-1] == "volumeup"
