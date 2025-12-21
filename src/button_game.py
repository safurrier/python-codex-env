"""The Button Must Be Clicked - A progressively absurd button clicking game."""

import random
import time
from enum import Enum
from typing import Any


class ButtonMood(Enum):
    """Different moods/personalities the button can have."""

    COOPERATIVE = "cooperative"
    RELUCTANT = "reluctant"
    ANNOYED = "annoyed"
    SARCASTIC = "sarcastic"
    ANGRY = "angry"
    BEGGING = "begging"
    CHAOTIC = "chaotic"


class ButtonGame:
    """Main game logic for The Button Must Be Clicked."""

    def __init__(self) -> None:
        """Initialize a new game."""
        self.clicks = 0
        self.score = 0
        self.level = 1
        self.is_active = True
        self.last_click_time = 0.0
        self.combo = 0
        self.combo_timeout = 1.0  # seconds for combo to reset

    def click(self) -> dict[str, Any]:
        """
        Process a button click.

        Returns:
            Dictionary with click result and updated game state
        """
        current_time = time.time()

        # Check if button refuses the click (happens at higher levels)
        if self._should_refuse_click():
            return {
                "success": False,
                "message": self._get_refusal_message(),
                "clicks": self.clicks,
                "score": self.score,
            }

        # Check for combo
        if current_time - self.last_click_time < self.combo_timeout:
            self.combo += 1
        else:
            self.combo = 0

        self.last_click_time = current_time

        # Calculate score with combo multiplier
        base_score = 10
        combo_bonus = self.combo * 5
        points = base_score + combo_bonus

        self.clicks += 1
        self.score += points

        # Update level (every 10 clicks)
        self.level = (self.clicks // 10) + 1

        return {
            "success": True,
            "message": self._get_click_message(),
            "clicks": self.clicks,
            "score": self.score,
            "combo": self.combo if self.combo > 0 else None,
            "points": points,
        }

    def _should_refuse_click(self) -> bool:
        """Determine if button should refuse the click based on level."""
        if self.level < 5:
            return False

        # Higher levels = more refusals
        refusal_chance = (self.level - 4) * 0.1  # 10% at level 5, 20% at level 6, etc.
        refusal_chance = min(refusal_chance, 0.5)  # Cap at 50%

        return random.random() < refusal_chance

    def _get_refusal_message(self) -> str:
        """Get a random refusal message."""
        messages = [
            "Nope!",
            "I don't think so...",
            "Leave me alone!",
            "Stop it!",
            "You can't make me!",
            "My lawyer will hear about this!",
            "I'm on break.",
            "404 Click Not Found",
            "Access Denied!",
            "I'm tired...",
        ]
        return random.choice(messages)

    def _get_click_message(self) -> str:
        """Get a message after successful click based on mood."""
        mood = self.get_button_mood()

        messages = {
            ButtonMood.COOPERATIVE: [
                "Thanks for clicking!",
                "Great job!",
                "Awesome!",
                "Keep going!",
            ],
            ButtonMood.RELUCTANT: [
                "Fine...",
                "I guess that counts...",
                "Whatever you say...",
                "Okay, okay...",
            ],
            ButtonMood.ANNOYED: [
                "Again?!",
                "Seriously?",
                "This is getting old...",
                "Ugh, fine.",
            ],
            ButtonMood.SARCASTIC: [
                "Oh wow, you clicked me. So impressive.",
                "What an achievement.",
                "Your parents must be so proud.",
                "Revolutionary.",
            ],
            ButtonMood.ANGRY: [
                "STOP IT!",
                "I SAID STOP!",
                "WHY ARE YOU LIKE THIS?!",
                "LEAVE ME ALONE!",
            ],
            ButtonMood.BEGGING: [
                "Please... no more...",
                "I beg you to stop...",
                "Have mercy!",
                "I have a family!",
            ],
            ButtonMood.CHAOTIC: [
                "AHHHHHHH!!!",
                "🔥🔥🔥",
                "ERROR ERROR ERROR",
                "I am become button, destroyer of clicks",
                "The void stares back",
            ],
        }

        return random.choice(messages.get(mood, ["Click!"]))

    def get_button_mood(self) -> ButtonMood:
        """Get current button mood based on level."""
        if self.level == 1:
            return ButtonMood.COOPERATIVE
        if self.level <= 3:
            return ButtonMood.RELUCTANT
        if self.level <= 5:
            return ButtonMood.ANNOYED
        if self.level <= 7:
            return ButtonMood.SARCASTIC
        if self.level <= 9:
            return ButtonMood.ANGRY
        if self.level <= 12:
            return ButtonMood.BEGGING
        return ButtonMood.CHAOTIC

    def get_button_text(self) -> str:
        """Get button text based on current mood."""
        mood = self.get_button_mood()

        texts = {
            ButtonMood.COOPERATIVE: "Click me! 😊",
            ButtonMood.RELUCTANT: "Click me... I guess 😐",
            ButtonMood.ANNOYED: "Seriously? Again? 😒",
            ButtonMood.SARCASTIC: "Oh please, click me more 🙄",
            ButtonMood.ANGRY: "STOP CLICKING ME 😡",
            ButtonMood.BEGGING: "Please... no more... 🥺",
            ButtonMood.CHAOTIC: "C̷̢̛͉L̴̰̈́I̶͓̚C̸̱͠K̵̰̏ ̶̱̓M̸̰̈́E̵͇̊ 🌀",
        }

        return texts.get(mood, "Click me!")

    def get_button_style(self) -> dict[str, Any]:
        """Get button style properties based on level."""
        mood = self.get_button_mood()

        # Base style
        style = {
            "size": "normal",
            "color": "blue",
            "shake": False,
            "spin": False,
            "opacity": 1.0,
            "position_offset": {"x": 0, "y": 0},
        }

        # Modify based on mood
        if mood == ButtonMood.RELUCTANT:
            style["color"] = "gray"
            style["size"] = "small"

        elif mood == ButtonMood.ANNOYED:
            style["color"] = "orange"
            style["shake"] = True

        elif mood == ButtonMood.SARCASTIC:
            style["color"] = "purple"
            style["size"] = "large"
            style["spin"] = True

        elif mood == ButtonMood.ANGRY:
            style["color"] = "red"
            style["shake"] = True
            style["size"] = "large"

        elif mood == ButtonMood.BEGGING:
            style["color"] = "yellow"
            style["opacity"] = 0.7
            style["position_offset"] = {
                "x": random.randint(-50, 50),
                "y": random.randint(-50, 50),
            }

        elif mood == ButtonMood.CHAOTIC:
            style["color"] = random.choice(["red", "blue", "green", "purple", "orange"])
            style["shake"] = True
            style["spin"] = True
            style["size"] = random.choice(["tiny", "small", "normal", "large", "huge"])
            style["position_offset"] = {
                "x": random.randint(-100, 100),
                "y": random.randint(-100, 100),
            }

        return style

    def get_state(self) -> dict[str, Any]:
        """Get complete game state."""
        return {
            "clicks": self.clicks,
            "score": self.score,
            "level": self.level,
            "mood": self.get_button_mood().value,
            "button_text": self.get_button_text(),
            "button_style": self.get_button_style(),
            "is_active": self.is_active,
            "combo": self.combo if self.combo > 0 else 0,
        }

    def reset(self) -> None:
        """Reset the game to initial state."""
        self.clicks = 0
        self.score = 0
        self.level = 1
        self.is_active = True
        self.last_click_time = 0.0
        self.combo = 0
