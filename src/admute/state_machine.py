"""State machine coordinating ad detection events."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal

FrameKind = Literal["content", "adlike"]


@dataclass(frozen=True)
class FrameClassification:
    """Result of classifying a single audio frame."""

    kind: FrameKind
    confidence: float


class State(Enum):
    """Possible high-level playback states."""

    CONTENT = auto()
    MAYBE_AD = auto()
    AD = auto()
    MAYBE_CONTENT = auto()


class TransitionEvent(Enum):
    """Events emitted by the state machine."""

    AD_START = "ad_start"
    CONTENT_START = "content_start"
    FORCE_CONTENT = "force_content"


@dataclass(frozen=True)
class Transition:
    """Description of a state transition."""

    from_state: State
    to_state: State
    event: TransitionEvent
    force_unmute: bool = False


class StateMachine:
    """Detects transitions between content and advertising windows."""

    def __init__(
        self,
        *,
        ad_like_threshold: int = 3,
        content_like_threshold: int = 2,
        ad_max_seconds: float = 240.0,
        frame_seconds: float = 1.0,
    ) -> None:
        if ad_like_threshold < 1:
            raise ValueError("ad_like_threshold must be positive")
        if content_like_threshold < 1:
            raise ValueError("content_like_threshold must be positive")
        if frame_seconds <= 0:
            raise ValueError("frame_seconds must be positive")
        if ad_max_seconds <= 0:
            raise ValueError("ad_max_seconds must be positive")
        self._state: State = State.CONTENT
        self._ad_like_threshold = ad_like_threshold
        self._content_like_threshold = content_like_threshold
        self._frame_seconds = frame_seconds
        self._ad_max_seconds = ad_max_seconds
        self._adlike_streak = 0
        self._content_streak = 0
        self._ad_elapsed = 0.0

    @property
    def state(self) -> State:
        """Return the current high-level state."""

        return self._state

    def update(self, frame: FrameClassification) -> Transition | None:
        """Consume a frame classification and update the state machine."""

        if frame.kind not in ("content", "adlike"):
            raise ValueError(f"Unsupported frame kind: {frame.kind}")

        if self._state == State.CONTENT:
            return self._handle_content_state(frame)
        if self._state == State.MAYBE_AD:
            return self._handle_maybe_ad_state(frame)
        if self._state == State.AD:
            return self._handle_ad_state(frame)
        if self._state == State.MAYBE_CONTENT:
            return self._handle_maybe_content_state(frame)
        raise RuntimeError(f"Unknown state {self._state!r}")

    def _handle_content_state(self, frame: FrameClassification) -> Transition | None:
        if frame.kind == "adlike":
            self._adlike_streak = 1
            self._state = State.MAYBE_AD
        else:
            self._adlike_streak = 0
        return None

    def _handle_maybe_ad_state(
        self, frame: FrameClassification
    ) -> Transition | None:
        if frame.kind == "adlike":
            self._adlike_streak += 1
            if self._adlike_streak >= self._ad_like_threshold:
                transition = Transition(
                    from_state=State.MAYBE_AD,
                    to_state=State.AD,
                    event=TransitionEvent.AD_START,
                )
                self._state = State.AD
                self._content_streak = 0
                self._ad_elapsed = 0.0
                return transition
        else:
            self._state = State.CONTENT
            self._adlike_streak = 0
        return None

    def _handle_ad_state(self, frame: FrameClassification) -> Transition | None:
        self._ad_elapsed += self._frame_seconds
        if frame.kind == "content":
            self._content_streak = 1
            self._state = State.MAYBE_CONTENT
        else:
            self._content_streak = 0
        if self._ad_elapsed >= self._ad_max_seconds:
            transition = Transition(
                from_state=State.AD,
                to_state=State.CONTENT,
                event=TransitionEvent.FORCE_CONTENT,
                force_unmute=True,
            )
            self._reset_to_content()
            return transition
        return None

    def _handle_maybe_content_state(
        self, frame: FrameClassification
    ) -> Transition | None:
        self._ad_elapsed += self._frame_seconds
        if frame.kind == "content":
            self._content_streak += 1
            if self._content_streak >= self._content_like_threshold:
                transition = Transition(
                    from_state=State.MAYBE_CONTENT,
                    to_state=State.CONTENT,
                    event=TransitionEvent.CONTENT_START,
                )
                self._reset_to_content()
                return transition
        else:
            self._state = State.AD
            self._content_streak = 0
        if self._ad_elapsed >= self._ad_max_seconds:
            transition = Transition(
                from_state=State.MAYBE_CONTENT,
                to_state=State.CONTENT,
                event=TransitionEvent.FORCE_CONTENT,
                force_unmute=True,
            )
            self._reset_to_content()
            return transition
        return None

    def _reset_to_content(self) -> None:
        self._state = State.CONTENT
        self._adlike_streak = 0
        self._content_streak = 0
        self._ad_elapsed = 0.0

    def batch_update(self, frames: Iterable[FrameClassification]) -> list[Transition]:
        """Utility helper primarily intended for tests."""

        transitions: list[Transition] = []
        for frame in frames:
            transition = self.update(frame)
            if transition is not None:
                transitions.append(transition)
        return transitions
