"""Tests for the state machine transitions."""

from __future__ import annotations

from src.admute.state_machine import (
    FrameClassification,
    State,
    StateMachine,
    TransitionEvent,
)


def test_state_machine_enters_ad_after_three_adlike_frames() -> None:
    sm = StateMachine(ad_like_threshold=3, content_like_threshold=2, frame_seconds=1.0)
    frames = [
        FrameClassification("content", 0.5),
        FrameClassification("content", 0.5),
        FrameClassification("adlike", 0.7),
        FrameClassification("adlike", 0.8),
        FrameClassification("adlike", 0.8),
    ]
    transitions = sm.batch_update(frames)
    assert transitions
    assert transitions[-1].event == TransitionEvent.AD_START
    assert sm.state == State.AD


def test_state_machine_exits_ad_after_two_content_frames() -> None:
    sm = StateMachine(ad_like_threshold=3, content_like_threshold=2, frame_seconds=1.0)
    sm.batch_update(
        [
            FrameClassification("adlike", 0.8),
            FrameClassification("adlike", 0.8),
            FrameClassification("adlike", 0.9),
        ]
    )
    assert sm.state == State.AD

    transitions = sm.batch_update(
        [
            FrameClassification("content", 0.4),
            FrameClassification("content", 0.4),
        ]
    )
    assert transitions
    assert transitions[-1].event == TransitionEvent.CONTENT_START
    assert sm.state == State.CONTENT


def test_state_machine_forces_unmute_after_timeout() -> None:
    sm = StateMachine(
        ad_like_threshold=3,
        content_like_threshold=2,
        frame_seconds=1.0,
        ad_max_seconds=5.0,
    )
    sm.batch_update(
        [
            FrameClassification("adlike", 0.8),
            FrameClassification("adlike", 0.8),
            FrameClassification("adlike", 0.8),
        ]
    )
    transitions = []
    for _ in range(10):
        transition = sm.update(FrameClassification("adlike", 0.8))
        if transition is not None:
            transitions.append(transition)
            if transition.force_unmute:
                break
    assert transitions
    assert transitions[-1].force_unmute
    assert transitions[-1].event == TransitionEvent.FORCE_CONTENT
    assert sm.state == State.CONTENT
