"""Top-level package for the AdMute project."""

from __future__ import annotations

from .actuator_base import ActuatorError, MuteActuator
from .state_machine import FrameClassification, FrameKind, StateMachine, Transition

__all__ = [
    "ActuatorError",
    "FrameClassification",
    "FrameKind",
    "MuteActuator",
    "StateMachine",
    "Transition",
]
