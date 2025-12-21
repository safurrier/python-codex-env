"""Tests for the Flask web application."""

import pytest
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestFlaskApp:
    """Test the Flask application routes."""

    def test_index_page_loads(self, client) -> None:
        """Test that the main page loads successfully."""
        response = client.get("/")
        assert response.status_code == 200

    def test_get_game_state(self, client) -> None:
        """Test getting initial game state."""
        response = client.get("/api/game/state")
        assert response.status_code == 200

        data = response.get_json()
        assert data["clicks"] == 0
        assert data["score"] == 0
        assert data["level"] == 1
        assert "mood" in data
        assert "button_text" in data

    def test_click_button(self, client) -> None:
        """Test clicking the button via API."""
        response = client.post("/api/game/click")
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert data["clicks"] == 1
        assert "state" in data
        assert data["state"]["clicks"] == 1

    def test_multiple_clicks(self, client) -> None:
        """Test multiple clicks in sequence."""
        # Click 5 times
        for i in range(5):
            response = client.post("/api/game/click")
            data = response.get_json()
            assert data["clicks"] == i + 1

    def test_reset_game(self, client) -> None:
        """Test resetting the game."""
        # Click a few times
        for _ in range(10):
            client.post("/api/game/click")

        # Reset
        response = client.post("/api/game/reset")
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert data["state"]["clicks"] == 0
        assert data["state"]["score"] == 0

    def test_game_state_persists_in_session(self, client) -> None:
        """Test that game state persists across requests in same session."""
        # Click once
        client.post("/api/game/click")

        # Get state
        response = client.get("/api/game/state")
        data = response.get_json()

        assert data["clicks"] == 1

        # Click again
        client.post("/api/game/click")

        # Get state again
        response = client.get("/api/game/state")
        data = response.get_json()

        assert data["clicks"] == 2

    def test_stats_endpoint(self, client) -> None:
        """Test the global statistics endpoint."""
        response = client.get("/api/stats")
        assert response.status_code == 200

        data = response.get_json()
        assert "total_clicks" in data
        assert "total_games" in data
        assert "highest_score" in data
        assert "highest_level" in data

    def test_button_refusal_reflected_in_api(self, client) -> None:
        """Test that button refusals are properly communicated via API."""
        # Get to high level where refusals happen
        for _ in range(50):
            client.post("/api/game/click")

        # Set seed for deterministic behavior
        import random
        random.seed(123)

        # Try clicking many times, should eventually get a refusal
        results = []
        for _ in range(30):
            response = client.post("/api/game/click")
            data = response.get_json()
            results.append(data["success"])

        # Should have at least some refusals at this level
        assert not all(results), "Should have some click refusals at high level"
