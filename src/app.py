"""Flask web application for The Button Must Be Clicked game."""

from flask import Flask, jsonify, render_template, session
from src.button_game import ButtonGame

app = Flask(__name__, template_folder="../templates")
app.secret_key = "super-secret-button-game-key-2024"  # For session management

# Store games in memory (could be replaced with database later)
games: dict[str, ButtonGame] = {}


def get_or_create_game(session_id: str) -> ButtonGame:
    """Get existing game or create new one for session."""
    if session_id not in games:
        games[session_id] = ButtonGame()
    return games[session_id]


@app.route("/")
def index():
    """Serve the main game page."""
    return render_template("index.html")


@app.route("/api/game/state", methods=["GET"])
def get_game_state():
    """Get current game state."""
    session_id = session.get("session_id", "default")
    game = get_or_create_game(session_id)
    return jsonify(game.get_state())


@app.route("/api/game/click", methods=["POST"])
def click_button():
    """Process a button click."""
    session_id = session.get("session_id", "default")

    # Create session ID if doesn't exist
    if "session_id" not in session:
        import secrets
        session["session_id"] = secrets.token_hex(16)
        session_id = session["session_id"]

    game = get_or_create_game(session_id)
    result = game.click()

    # Include full game state in response
    response = {**result, "state": game.get_state()}

    return jsonify(response)


@app.route("/api/game/reset", methods=["POST"])
def reset_game():
    """Reset the current game."""
    session_id = session.get("session_id", "default")
    game = get_or_create_game(session_id)
    game.reset()

    return jsonify({"success": True, "state": game.get_state()})


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get global statistics across all games."""
    total_clicks = sum(game.clicks for game in games.values())
    total_games = len(games)
    highest_score = max((game.score for game in games.values()), default=0)
    highest_level = max((game.level for game in games.values()), default=1)

    return jsonify({
        "total_clicks": total_clicks,
        "total_games": total_games,
        "highest_score": highest_score,
        "highest_level": highest_level,
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
