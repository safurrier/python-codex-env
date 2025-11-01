"""Actuator that controls the LG TV through HDMI-CEC commands."""

from __future__ import annotations

import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol


class SubprocessRunner(Protocol):
    """Minimal protocol for running subprocess commands."""

    def __call__(
        self, args: list[str], *, input: bytes | None, check: bool
    ) -> None: ...


@dataclass
class CECConfig:
    """Configuration for the CEC actuator."""

    command: str = "cec-client"
    device: int = 1
    volume_step_count: int = 20


class CECActuator:
    """Send mute/unmute using HDMI-CEC volume commands."""

    def __init__(
        self,
        config: CECConfig,
        *,
        runner: SubprocessRunner | None = None,
    ) -> None:
        self._config = config
        self._runner = runner or self._default_runner

    def mute(self) -> None:
        self._drive_volume(["volumedown"] * self._config.volume_step_count)

    def unmute(self) -> None:
        self._drive_volume(["volumeup"] * self._config.volume_step_count)

    def _drive_volume(self, commands: Iterable[str]) -> None:
        for command in commands:
            self._runner(
                [self._config.command, "-s", "-d", str(self._config.device)],
                input=f"{command}\n".encode(),
                check=True,
            )

    @staticmethod
    def _default_runner(
        args: list[str], *, input: bytes | None, check: bool
    ) -> None:  # pragma: no cover - thin wrapper around subprocess
        subprocess.run(args, input=input, check=check)  # noqa: S603
