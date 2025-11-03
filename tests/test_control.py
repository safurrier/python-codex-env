"""Tests for the actuator controller utilities."""

from __future__ import annotations

from src.admute.control import ActuatorController


class DummyActuator:
    def __init__(self) -> None:
        self.commands: list[str] = []

    def mute(self) -> None:
        self.commands.append("mute")

    def unmute(self) -> None:
        self.commands.append("unmute")

    def close(self) -> None:
        self.commands.append("close")


def test_controller_tracks_state_and_avoids_duplicate_commands() -> None:
    actuator = DummyActuator()
    controller = ActuatorController(actuator)

    first = controller.mute(reason="unit", origin="test")
    assert first is True
    status = controller.snapshot()
    assert status.muted is True
    assert status.command_count == 1
    assert status.last_reason == "unit"

    second = controller.mute(reason="unit", origin="test")
    assert second is False
    assert controller.snapshot().command_count == 1

    controller.unmute(reason="unit_end", origin="test")
    status = controller.snapshot()
    assert status.muted is False
    assert status.command_count == 2

    controller.close()
    assert actuator.commands == ["mute", "unmute", "close"]


def test_controller_toggle_flips_state() -> None:
    actuator = DummyActuator()
    controller = ActuatorController(actuator)

    controller.toggle(reason="manual", origin="web")
    assert controller.snapshot().muted is True

    controller.toggle(reason="manual", origin="web")
    assert controller.snapshot().muted is False
    assert actuator.commands == ["mute", "unmute"]

