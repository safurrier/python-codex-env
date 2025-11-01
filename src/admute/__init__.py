"""Top-level package for the AdMute project."""

from __future__ import annotations

from .state_machine import FrameClassification, FrameKind, StateMachine, Transition

__all__ = [
    "FrameClassification",
    "FrameKind",
    "StateMachine",
    "Transition",
]
