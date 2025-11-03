"""Stage-A heuristic detector for advertisement audio."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np

from .state_machine import FrameClassification, FrameKind


@dataclass
class DetectorConfig:
    sample_rate: int = 16_000
    frame_seconds: float = 1.0
    min_ad_rms: float = 0.12
    rms_delta_threshold: float = 0.05
    centroid_threshold: float = 0.35
    flatness_threshold: float = 0.25
    history: int = 8


class StageADetector:
    """Basic heuristic detector that classifies 1-second audio frames."""

    def __init__(self, config: DetectorConfig | None = None) -> None:
        self._config = config or DetectorConfig()
        self._rms_history: deque[float] = deque(maxlen=self._config.history)

    def classify(self, frame: np.ndarray) -> FrameClassification:
        if frame.size == 0:
            return FrameClassification(kind="content", confidence=0.0)
        rms = float(np.sqrt(np.mean(np.square(frame))))
        delta_rms = self._delta_rms(rms)
        centroid = self._spectral_centroid(frame)
        flatness = self._spectral_flatness(frame)

        adlike = self._is_adlike(rms, delta_rms, centroid, flatness)
        confidence = float(
            min(
                1.0,
                max(
                    0.0,
                    (rms / max(self._config.min_ad_rms, 1e-6)) * 0.4 + flatness * 0.3,
                ),
            )
        )
        kind: FrameKind = "adlike" if adlike else "content"
        return FrameClassification(kind=kind, confidence=confidence)

    def _delta_rms(self, current_rms: float) -> float:
        if self._rms_history:
            baseline = sum(self._rms_history) / len(self._rms_history)
        else:
            baseline = current_rms
        self._rms_history.append(current_rms)
        return current_rms - baseline

    def _spectral_centroid(self, frame: np.ndarray) -> float:
        spectrum = np.fft.rfft(frame)
        magnitude = np.abs(spectrum)
        total: float = float(np.sum(magnitude))
        if total <= 0:
            return 0.0
        freqs = np.fft.rfftfreq(frame.size, d=1.0 / self._config.sample_rate)
        return float(np.sum(freqs * magnitude) / total / (self._config.sample_rate / 2))

    def _spectral_flatness(self, frame: np.ndarray) -> float:
        magnitude = np.abs(np.fft.rfft(frame)) + 1e-12
        geometric_mean = np.exp(np.mean(np.log(magnitude)))
        arithmetic_mean = np.mean(magnitude)
        if arithmetic_mean <= 0:
            return 0.0
        return float(geometric_mean / arithmetic_mean)

    def _is_adlike(
        self, rms: float, delta_rms: float, centroid: float, flatness: float
    ) -> bool:
        config = self._config
        if rms >= config.min_ad_rms and delta_rms >= config.rms_delta_threshold:
            return True
        if (
            centroid >= config.centroid_threshold
            and flatness >= config.flatness_threshold
        ):
            return True
        if (
            flatness >= config.flatness_threshold * 1.5
            and rms >= config.min_ad_rms * 0.75
        ):
            return True
        return False
