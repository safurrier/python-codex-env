"""Thread-safe helpers for coordinating actuator commands."""
from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol


class SupportsMute(Protocol):
    """Minimal protocol for actuators that can mute and unmute."""

    def mute(self) -> None:  # pragma: no cover - protocol definition
        ...

    def unmute(self) -> None:  # pragma: no cover - protocol definition
        ...


@dataclass(frozen=True)
class ActuatorStatus:
    """Snapshot of the controller state."""

    muted: bool
    last_reason: str
    origin: str
    updated_at: datetime
    command_count: int


class ActuatorController:
    """Wrap an actuator and track the most recent command issued."""

    def __init__(self, actuator: SupportsMute) -> None:
        self._actuator = actuator
        self._lock = threading.Lock()
        self._status = ActuatorStatus(
            muted=False,
            last_reason="startup",
            origin="system",
            updated_at=datetime.now(timezone.utc),
            command_count=0,
        )

    def mute(self, *, reason: str, origin: str, force: bool = False) -> bool:
        """Mute the TV if not already muted.

        Returns ``True`` if a mute command was issued.
        """

        with self._lock:
            if not force and self._status.muted:
                return False
            self._actuator.mute()
            self._status = ActuatorStatus(
                muted=True,
                last_reason=reason,
                origin=origin,
                updated_at=datetime.now(timezone.utc),
                command_count=self._status.command_count + 1,
            )
            return True

    def unmute(self, *, reason: str, origin: str, force: bool = False) -> bool:
        """Unmute the TV if currently muted.

        Returns ``True`` if an unmute command was issued.
        """

        with self._lock:
            if not force and not self._status.muted:
                return False
            self._actuator.unmute()
            self._status = ActuatorStatus(
                muted=False,
                last_reason=reason,
                origin=origin,
                updated_at=datetime.now(timezone.utc),
                command_count=self._status.command_count + 1,
            )
            return True

    def toggle(self, *, reason: str, origin: str) -> bool:
        """Toggle the mute state."""

        with self._lock:
            if self._status.muted:
                self._actuator.unmute()
                new_status = ActuatorStatus(
                    muted=False,
                    last_reason=reason,
                    origin=origin,
                    updated_at=datetime.now(timezone.utc),
                    command_count=self._status.command_count + 1,
                )
            else:
                self._actuator.mute()
                new_status = ActuatorStatus(
                    muted=True,
                    last_reason=reason,
                    origin=origin,
                    updated_at=datetime.now(timezone.utc),
                    command_count=self._status.command_count + 1,
                )
            self._status = new_status
            return True

    def snapshot(self) -> ActuatorStatus:
        """Return the most recent status."""

        with self._lock:
            return self._status

    def close(self) -> None:
        """Close the underlying actuator if it exposes ``close``."""

        close_method = getattr(self._actuator, "close", None)
        if callable(close_method):
            close_method()

    @property
    def muted(self) -> bool:
        """Return whether the controller believes the TV is muted."""

        return self.snapshot().muted

