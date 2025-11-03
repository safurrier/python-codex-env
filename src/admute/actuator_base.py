"""Abstract base classes shared by mute actuators."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ActuatorError(RuntimeError):
    """Base exception for actuator failures."""


class MuteActuator(ABC):
    """Interface for actuators capable of muting and unmuting audio."""

    @abstractmethod
    def mute(self) -> None:
        """Mute the attached playback device."""

    @abstractmethod
    def unmute(self) -> None:
        """Unmute the attached playback device."""

    def close(self) -> None:
        """Release any underlying resources held by the actuator."""

        return None

