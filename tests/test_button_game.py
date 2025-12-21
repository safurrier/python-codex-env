"""Tests for The Button Must Be Clicked game."""

import pytest

from src.button_game import ButtonGame, ButtonMood


class TestButtonGame:
    """Test the ButtonGame class."""

    def test_game_initialization(self) -> None:
        """Test that a new game starts with correct initial state."""
        game = ButtonGame()
        assert game.clicks == 0
        assert game.score == 0
        assert game.level == 1
        assert game.is_active is True

    def test_single_click(self) -> None:
        """Test that clicking increments counters."""
        game = ButtonGame()
        result = game.click()

        assert game.clicks == 1
        assert game.score == 10  # Base score per click
        assert result["success"] is True
        assert result["clicks"] == 1

    def test_multiple_clicks(self) -> None:
        """Test multiple clicks increment properly."""
        game = ButtonGame()

        for i in range(5):
            game.click()

        assert game.clicks == 5
        # Score includes combo bonuses, so it will be > base 50
        assert game.score >= 50

    def test_level_progression(self) -> None:
        """Test that levels increase after threshold clicks."""
        game = ButtonGame()

        # Click enough to reach level 2 (every 10 clicks)
        for _ in range(10):
            game.click()

        assert game.level == 2

        # Click to reach level 3
        for _ in range(10):
            game.click()

        assert game.level == 3

    def test_button_mood_changes(self) -> None:
        """Test that button mood changes at different levels."""
        game = ButtonGame()

        # Level 1 - Cooperative
        assert game.get_button_mood() == ButtonMood.COOPERATIVE

        # Level 2 - Reluctant
        for _ in range(10):
            game.click()
        assert game.get_button_mood() == ButtonMood.RELUCTANT

        # Level 4 - Annoyed (need to reach level 4+)
        for _ in range(20):
            game.click()
        assert game.get_button_mood() == ButtonMood.ANNOYED

    def test_button_text_changes_with_mood(self) -> None:
        """Test that button text reflects current mood."""
        game = ButtonGame()

        text1 = game.get_button_text()
        assert "Click me" in text1 or "click" in text1.lower()

        # Progress to next level
        for _ in range(10):
            game.click()

        text2 = game.get_button_text()
        assert text1 != text2  # Text should change

    def test_button_refuses_click_sometimes(self) -> None:
        """Test that button can refuse clicks at higher levels."""
        game = ButtonGame()

        # Progress to angry level (level 5)
        for _ in range(40):
            game.click()

        assert game.level >= 5

        # Set seed for deterministic testing
        import random
        random.seed(42)

        # At angry level, button sometimes refuses
        results = [game.click()["success"] for _ in range(20)]

        # Should have at least some failures
        assert not all(results), "Button should refuse some clicks at high levels"

    def test_get_game_state(self) -> None:
        """Test that game state is returned correctly."""
        game = ButtonGame()
        game.click()

        state = game.get_state()

        assert state["clicks"] == 1
        assert state["score"] == 10
        assert state["level"] == 1
        assert "mood" in state
        assert "button_text" in state
        assert "button_style" in state

    def test_reset_game(self) -> None:
        """Test that game can be reset."""
        game = ButtonGame()

        # Play some
        for _ in range(15):
            game.click()

        # Reset
        game.reset()

        assert game.clicks == 0
        assert game.score == 0
        assert game.level == 1

    def test_button_style_changes(self) -> None:
        """Test that button style properties change with level."""
        game = ButtonGame()

        style1 = game.get_button_style()

        # Progress levels
        for _ in range(30):
            game.click()

        style2 = game.get_button_style()

        # Some style property should be different
        assert style1 != style2

    def test_combo_multiplier(self) -> None:
        """Test that rapid clicks create combo multipliers."""
        game = ButtonGame()

        # Quick succession clicks
        import time
        game.click()
        game.click()
        result = game.click()

        # Should have combo bonus
        assert "combo" in result
        assert game.score > 30  # More than just 3 * 10

    def test_button_insults_at_high_levels(self) -> None:
        """Test that button generates insults at high levels."""
        game = ButtonGame()

        # Get to angry/begging/chaotic level (level 8+)
        for _ in range(80):
            game.click()

        mood = game.get_button_mood()
        assert mood in [ButtonMood.ANGRY, ButtonMood.BEGGING, ButtonMood.CHAOTIC]

        # Should have some sassy text
        text = game.get_button_text()
        assert len(text) > 0
