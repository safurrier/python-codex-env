"""Integration-style tests for the runner loop using synthetic audio."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

import numpy as np
import pytest

from src.admute.control import ActuatorController
from src.admute.detector import StageADetector
from src.admute.runner import run_pipeline
from src.admute.state_machine import StateMachine


@dataclass
class FakeIngestor:
    """Minimal ingestor that yields precomputed frames."""

    frames: Iterable[np.ndarray]

    def stream_frames(self) -> Iterator[np.ndarray]:
        yield from self.frames


class RecordingActuator:
    """Actuator implementation that records issued commands."""

    def __init__(self) -> None:
        self.commands: list[str] = []

    def mute(self) -> None:
        self.commands.append("mute")

    def unmute(self) -> None:
        self.commands.append("unmute")

    def close(self) -> None:  # pragma: no cover - included for API parity
        pass


def _generate_tone(
    frequency: float,
    *,
    seconds: float = 1.0,
    sample_rate: int = 16_000,
    amplitude: float = 0.05,
) -> np.ndarray:
    t = np.linspace(0, seconds, int(sample_rate * seconds), endpoint=False)
    return amplitude * np.sin(2 * np.pi * frequency * t)


def _generate_ad_mix() -> np.ndarray:
    sample_rate = 16_000
    t = np.linspace(0, 1.0, sample_rate, endpoint=False)
    return 0.6 * np.sin(2 * np.pi * 1_200 * t) + 0.5 * np.sin(2 * np.pi * 1_800 * t)


def test_run_pipeline_mutes_and_unmutes_with_simulated_audio() -> None:
    detector = StageADetector()
    state_machine = StateMachine()

    content = _generate_tone(220.0, amplitude=0.05)
    ad_mix = _generate_ad_mix()
    frames = [content] * 5 + [ad_mix] * 5 + [content] * 4

    ingestor = FakeIngestor(frames)
    actuator = RecordingActuator()
    controller = ActuatorController(actuator)

    run_pipeline(
        ingestor,
        detector,
        state_machine,
        controller,
        max_frames=len(frames),
    )

    assert actuator.commands == ["mute", "unmute"]


def test_run_pipeline_force_unmute_when_ad_exceeds_limit(
    caplog: pytest.LogCaptureFixture,
) -> None:
    detector = StageADetector()
    state_machine = StateMachine(ad_max_seconds=3.0)

    content = _generate_tone(220.0, amplitude=0.05)
    ad_mix = _generate_ad_mix()
    frames = [content] * 5 + [ad_mix] * 8

    ingestor = FakeIngestor(frames)
    actuator = RecordingActuator()
    controller = ActuatorController(actuator)

    with caplog.at_level(logging.WARNING):
        run_pipeline(
            ingestor,
            detector,
            state_machine,
            controller,
            max_frames=len(frames),
        )

    assert actuator.commands == ["mute", "unmute"]
    assert any("forcing unmute" in message for message in caplog.messages)
