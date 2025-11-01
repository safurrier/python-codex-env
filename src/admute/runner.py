"""Command-line entry point for the AdMute service."""

from __future__ import annotations

import argparse
import logging
import signal
import sys
from pathlib import Path
from typing import Any, Callable

import yaml

from .actuator_cec import CECActuator, CECConfig
from .actuator_webos import WebOSActuator, WebOSConfig
from .detector import DetectorConfig, StageADetector
from .ingest import FFmpegAudioIngestor, IngestConfig
from .state_machine import StateMachine, TransitionEvent

LOGGER = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AdMute runner")
    parser.add_argument(
        "--config", type=Path, required=True, help="Path to YAML config"
    )
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args(argv)


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("Configuration file must define a mapping")
    return data


def build_ingestor(config: dict[str, Any]) -> FFmpegAudioIngestor:
    ingest_cfg = IngestConfig(
        device=config["capture_device"],
        ffmpeg_path=config.get("ffmpeg_path", "ffmpeg"),
        channels=config.get("channels", 1),
        sample_rate=config.get("sample_rate", 16_000),
        frame_seconds=config.get("frame_seconds", 1.0),
        input_format=config.get("input_format"),
        extra_args=config.get("extra_args"),
    )
    return FFmpegAudioIngestor(ingest_cfg)


def build_detector(config: dict[str, Any]) -> StageADetector:
    detector_cfg = DetectorConfig(
        sample_rate=config.get("sample_rate", 16_000),
        frame_seconds=config.get("frame_seconds", 1.0),
        min_ad_rms=config.get("min_ad_rms", 0.12),
        rms_delta_threshold=config.get("rms_delta_threshold", 0.05),
        centroid_threshold=config.get("centroid_threshold", 0.35),
        flatness_threshold=config.get("flatness_threshold", 0.25),
        history=config.get("history", 8),
    )
    return StageADetector(detector_cfg)


def build_actuator(config: dict[str, Any]) -> WebOSActuator | CECActuator:
    actuator_config = config.get("actuator", {})
    actuator_type = actuator_config.get("type", "webos")
    if actuator_type == "webos":
        client_key_path = actuator_config.get("client_key")
        key_path = Path(client_key_path) if client_key_path else None
        webos_config = WebOSConfig(
            host=actuator_config["host"],
            client_key_path=key_path,
            secure=actuator_config.get("secure", True),
            port=actuator_config.get("port", 3001),
        )
        return WebOSActuator(webos_config)
    if actuator_type == "cec":
        cec_config = CECConfig(
            command=actuator_config.get("command", "cec-client"),
            device=actuator_config.get("device", 1),
            volume_step_count=actuator_config.get("volume_step_count", 20),
        )
        return CECActuator(cec_config)
    raise ValueError(f"Unsupported actuator type: {actuator_type}")


def run_pipeline(
    ingestor: FFmpegAudioIngestor,
    detector: StageADetector,
    state_machine: StateMachine,
    actuator: WebOSActuator | CECActuator,
    *,
    should_stop: Callable[[], bool] | None = None,
    max_frames: int | None = None,
) -> None:
    """Drive the ingest/detect/actuate loop.

    Parameters
    ----------
    ingestor:
        Source of audio frames.
    detector:
        Frame classifier used to distinguish ads from content.
    state_machine:
        State tracker that interprets frame classifications.
    actuator:
        Control surface for the TV.
    should_stop:
        Optional callback that, when returning :data:`True`, stops the loop.
    max_frames:
        Optional safety limit on the number of frames to process.
    """

    processed = 0
    try:
        for frame in ingestor.stream_frames():
            fc = detector.classify(frame)
            transition = state_machine.update(fc)
            if transition is not None:
                if transition.event == TransitionEvent.AD_START:
                    LOGGER.info("Detected ad block; muting TV")
                    actuator.mute()
                elif transition.event == TransitionEvent.CONTENT_START:
                    LOGGER.info("Content resumed; unmuting TV")
                    actuator.unmute()
                elif transition.force_unmute:
                    LOGGER.warning("Ad exceeded max duration; forcing unmute")
                    actuator.unmute()
            processed += 1
            if max_frames is not None and processed >= max_frames:
                break
            if should_stop and should_stop():
                break
    finally:
        close_method = getattr(actuator, "close", None)
        if callable(close_method):
            close_method()


def run_once(config: dict[str, Any]) -> None:
    logging.basicConfig(level=config.get("log_level", "INFO"))
    ingestor = build_ingestor(config)
    detector = build_detector(config.get("detector", {}))
    state_machine = StateMachine(
        ad_like_threshold=config.get("ad_like_threshold", 3),
        content_like_threshold=config.get("content_like_threshold", 2),
        ad_max_seconds=config.get("ad_max_seconds", 240.0),
        frame_seconds=config.get("frame_seconds", 1.0),
    )
    actuator = build_actuator(config)

    stop = False

    def _handle_signal(signum: int, _frame: object) -> None:
        nonlocal stop
        LOGGER.info("Received signal %s, shutting down", signum)
        stop = True

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    run_pipeline(
        ingestor,
        detector,
        state_machine,
        actuator,
        should_stop=lambda: stop,
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(args.config)
    config.setdefault("log_level", args.log_level)
    try:
        run_once(config)
    except Exception:  # pragma: no cover - entry point guard
        LOGGER.exception("Runner failed")
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
