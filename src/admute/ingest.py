"""Audio ingest pipeline based on ffmpeg."""

from __future__ import annotations

import logging
import subprocess
import threading
from collections import deque
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import IO

import numpy as np

LOGGER = logging.getLogger(__name__)


@dataclass
class IngestConfig:
    """Parameters describing the capture pipeline."""

    device: str
    ffmpeg_path: str = "ffmpeg"
    channels: int = 1
    sample_rate: int = 16_000
    frame_seconds: float = 1.0
    input_format: str | None = None  # e.g. "v4l2" or "alsa"
    extra_args: list[str] | None = None


class FFmpegAudioIngestor:
    """Read PCM audio samples from an HDMI capture device."""

    def __init__(self, config: IngestConfig) -> None:
        if config.channels <= 0:
            raise ValueError("channels must be positive")
        if config.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if config.frame_seconds <= 0:
            raise ValueError("frame_seconds must be positive")
        self._config = config
        self._frame_bytes = int(
            config.sample_rate * config.frame_seconds * config.channels * 2
        )

    def stream_frames(self) -> Iterator[np.ndarray]:
        """Yield floating point frames normalized to [-1, 1]."""

        command = self._build_command()
        LOGGER.debug("Starting ffmpeg ingest: %s", " ".join(command))
        process = subprocess.Popen(  # noqa: S603
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert process.stdout is not None
        stderr_thread = None
        if process.stderr is not None:
            stderr_thread = self._spawn_stderr_drain(process.stderr)
        try:
            while True:
                chunk = process.stdout.read(self._frame_bytes)
                if not chunk:
                    break
                if len(chunk) < self._frame_bytes:
                    LOGGER.debug("Incomplete frame received; stopping ingest")
                    break
                frame = np.frombuffer(chunk, dtype=np.int16)
                frame = frame.astype(np.float32) / 32768.0
                yield frame
        finally:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:  # pragma: no cover - defensive
                process.kill()
            if stderr_thread is not None:
                stderr_thread.join(timeout=1)

    def _build_command(self) -> list[str]:
        config = self._config
        command = [config.ffmpeg_path]
        if config.input_format:
            command.extend(["-f", config.input_format])
        command.extend(["-i", config.device])
        command.extend(
            [
                "-vn",
                "-f",
                "s16le",
                "-ac",
                str(config.channels),
                "-ar",
                str(config.sample_rate),
                "pipe:1",
            ]
        )
        if config.extra_args:
            command.extend(config.extra_args)
        return command

    def _spawn_stderr_drain(self, stream: IO[bytes]) -> threading.Thread:
        """Drain stderr from the ffmpeg process to avoid deadlocks."""

        def _drain() -> None:
            with stream:
                for raw_line in iter(stream.readline, b""):
                    line = raw_line.decode("utf-8", errors="replace").rstrip()
                    if line:
                        LOGGER.debug("ffmpeg stderr: %s", line)

        thread = threading.Thread(target=_drain, daemon=True)
        thread.start()
        return thread


class RollingRMS:
    """Compute rolling RMS statistics for debug tooling."""

    def __init__(self, window: int = 8) -> None:
        self._values: deque[float] = deque(maxlen=window)

    def add(self, frame: np.ndarray) -> float:
        value = float(np.sqrt(np.mean(np.square(frame))))
        self._values.append(value)
        return value

    def average(self) -> float:
        if not self._values:
            return 0.0
        return sum(self._values) / len(self._values)


def dump_rms(
    ingestor: FFmpegAudioIngestor, limit: int | None = None
) -> Iterable[float]:
    """Yield RMS values for debugging."""

    counter = 0
    for frame in ingestor.stream_frames():
        rms = float(np.sqrt(np.mean(np.square(frame))))
        yield rms
        counter += 1
        if limit is not None and counter >= limit:
            break
