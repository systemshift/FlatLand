import flask
from flask import Flask, request, jsonify
import json
import uuid # For generating unique game IDs
from .game_engine import GameEngine
# Assuming sgd_schema_v0.1.json is in the same directory or accessible path
SGD_SCHEMA_PATH = "prompt_to_game_engine/sgd_schema_v0.1.json" # Relative to project root

app = Flask(__name__)

# In-memory store for active game engines (game_id -> GameEngine instance)
# In a production system, this might be more robust (e.g., using a database or distributed cache)
active_games: dict[str, GameEngine] = {}
sgd_schema_content: dict = {}

def load_sgd_schema():
    """Loads the SGD schema from file."""
    global sgd_schema_content
    try:
        with open(SGD_SCHEMA_PATH, 'r') as f:
            sgd_schema_content = json.load(f)
        print("SGD Schema loaded successfully.")
    except Exception as e:
        print(f"Error loading SGD Schema: {e}. MCP tool 'get_sgd_schema' will fail.")
        sgd_schema_content = {"error": "Schema not loaded"}

# --- MCP Tool Implementations as HTTP Endpoints ---

@app.route('/mcp/get_sgd_schema', methods=['POST'])
def mcp_get_sgd_schema():
    """MCP Tool: get_sgd_schema"""
    # This tool typically takes no arguments in MCP, but POST is used for consistency.
    # We could also use GET.
    if sgd_schema_content and "error" not in sgd_schema_content:
        return jsonify({"success": True, "schema": sgd_schema_content}), 200
    else:
        return jsonify({"success": False, "message": "SGD Schema not available."}), 500

@app.route('/mcp/create_game', methods=['POST'])
def mcp_create_game():
    """MCP Tool: create_game"""
    data = request.get_json()
    if not data or 'sgd_json_string' not in data:
        return jsonify({"success": False, "message": "Missing 'sgd_json_string' in request."}), 400

    sgd_json_string = data['sgd_json_string']
    
    engine = GameEngine()
    if engine.load_game_from_sgd(sgd_json_string):
        game_id = str(uuid.uuid4()) # Generate a unique ID for this game instance
        active_games[game_id] = engine
        initial_state = engine.get_current_state_dict()
        return jsonify({
            "success": True, 
            "game_id": game_id,
            "initial_state": initial_state,
            "message": "Game created successfully."
        }), 201 # 201 Created
    else:
        return jsonify({"success": False, "message": "Failed to load game from SGD."}), 500

@app.route('/mcp/submit_player_action', methods=['POST'])
def mcp_submit_player_action():
    """MCP Tool: submit_player_action"""
    data = request.get_json()
    if not data or 'game_id' not in data or 'action_key' not in data:
        return jsonify({"success": False, "message": "Missing 'game_id' or 'action_key'."}), 400

    game_id = data['game_id']
    action_key = data['action_key']

    engine = active_games.get(game_id)
    if not engine:
        return jsonify({"success": False, "message": f"Game with ID '{game_id}' not found."}), 404
    
    updated_state = engine.process_player_input(action_key)
    if updated_state:
         # Check if the game ended to potentially remove it from active_games
        if updated_state.get("game_status") not in ["running", "paused"]:
            # Optional: Clean up ended games. Consider if state should still be queryable.
            # del active_games[game_id] 
            # print(f"Game '{game_id}' ended with status: {updated_state.get('game_status')}. Removed from active games.")
            pass

        return jsonify({"success": True, "new_state": updated_state, "message": updated_state.get("message", "Action processed.")}), 200
    else:
        # This case should ideally be handled within process_player_input to return a state with an error message
        return jsonify({"success": False, "message": "Error processing player input."}), 500


@app.route('/mcp/get_game_state', methods=['POST'])
def mcp_get_game_state():
    """MCP Tool: get_game_state"""
    data = request.get_json()
    if not data or 'game_id' not in data:
        return jsonify({"success": False, "message": "Missing 'game_id'."}), 400

    game_id = data['game_id']
    engine = active_games.get(game_id)

    if not engine:
        return jsonify({"success": False, "message": f"Game with ID '{game_id}' not found."}), 404
    
    current_state = engine.get_current_state_dict()
    if current_state:
        return jsonify({"success": True, "current_state": current_state}), 200
    else:
        # Should not happen if engine exists and get_current_state_dict is robust
        return jsonify({"success": False, "message": "Error retrieving game state."}), 500

if __name__ == '__main__':
    load_sgd_schema()
    # It's good practice to ensure Flask is installed if running this directly
    try:
        import flask
    except ImportError:
        print("Flask is not installed. Please install it: pip install Flask")
        exit(1)
        
    print("Starting Game MCP Server on http://127.0.0.1:5002")
    app.run(debug=True, port=5002)
