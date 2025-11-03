"""Tests for the stage A detector heuristics."""

from __future__ import annotations

import numpy as np

from src.admute.detector import StageADetector


def generate_tone(
    frequency: float, seconds: float, sample_rate: int = 16_000, amplitude: float = 0.2
) -> np.ndarray:
    t = np.linspace(0, seconds, int(sample_rate * seconds), endpoint=False)
    return amplitude * np.sin(2 * np.pi * frequency * t)


def test_detector_marks_sustained_speech_as_content() -> None:
    detector = StageADetector()
    frame = generate_tone(220.0, 1.0, amplitude=0.05)
    classifications = [detector.classify(frame) for _ in range(20)]
    assert all(c.kind == "content" for c in classifications[5:])


def test_detector_identifies_loud_music_as_adlike() -> None:
    detector = StageADetector()
    silence = np.zeros(16_000)
    detector.classify(silence)
    music = generate_tone(1200.0, 1.0, amplitude=0.5) + generate_tone(
        1800.0, 1.0, amplitude=0.4
    )
    classifications = [detector.classify(music) for _ in range(5)]
    assert any(c.kind == "adlike" for c in classifications)
