import flask
from flask import Flask, request, jsonify
import json
import uuid # For generating unique game IDs
import os

# Flatland core components (now in src/flatland)
from flatland.logic_engine import LogicEngine
from flatland.llm.client import generate_environment, FlatlandLLMError, SchemaValidationError, RateLimitError as FlatlandRateLimitError
from flatland.schemas import ENVIRONMENT_SCHEMA, EnvironmentDefinition # ENVIRONMENT_SCHEMA is the dict, EnvironmentDefinition is the class

app = Flask(__name__)

# In-memory store for active game engines (game_id -> LogicEngine instance)
active_games: dict[str, LogicEngine] = {}
environment_schema_content: dict = {}

def load_environment_schema():
    """Loads the Flatland environment schema."""
    global environment_schema_content
    if ENVIRONMENT_SCHEMA:
        environment_schema_content = ENVIRONMENT_SCHEMA
        print("Flatland Environment Schema loaded successfully.")
    else:
        print(f"Error: Flatland ENVIRONMENT_SCHEMA not found or empty.")
        environment_schema_content = {"error": "Flatland Environment Schema not loaded"}

# --- MCP Tool Implementations as HTTP Endpoints ---

@app.route('/mcp/get_environment_schema', methods=['POST'])
def mcp_get_environment_schema():
    """MCP Tool: get_environment_schema"""
    if environment_schema_content and "error" not in environment_schema_content:
        return jsonify({"success": True, "schema": environment_schema_content}), 200
    else:
        return jsonify({"success": False, "message": "Flatland Environment Schema not available."}), 500

@app.route('/mcp/create_game_from_prompt', methods=['POST'])
def mcp_create_game_from_prompt():
    """MCP Tool: create_game_from_prompt"""
    data = request.get_json()
    if not data or 'prompt_text' not in data:
        return jsonify({"success": False, "message": "Missing 'prompt_text' in request."}), 400

    prompt_text = data['prompt_text']
    style_guidance = data.get('style_guidance') # Optional

    try:
        print(f"Generating environment for prompt: '{prompt_text}'...")
        # Ensure API key is available for the LLM client
        if not os.getenv("FLATLAND_OPENAI_KEY") and not os.getenv("OPENAI_API_KEY"):
            # Try to set it from OPENAI_API_KEY if FLATLAND_OPENAI_KEY is not set,
            # as prompt_to_game_engine used OPENAI_API_KEY
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                os.environ["FLATLAND_OPENAI_KEY"] = openai_key
                print("Using OPENAI_API_KEY for Flatland LLM.")
            else:
                 return jsonify({"success": False, "message": "OpenAI API key (FLATLAND_OPENAI_KEY or OPENAI_API_KEY) not set."}), 500


        env_definition: EnvironmentDefinition = generate_environment(
            description=prompt_text,
            style_guidance=style_guidance
        )
        print("Environment generated successfully by LLM.")

        engine = LogicEngine()
        engine.load_environment(env_definition.to_dict()) # LogicEngine expects a dict
        print("Environment loaded into LogicEngine.")

        game_id = str(uuid.uuid4())
        active_games[game_id] = engine
        
        # The initial state is implicitly set when loading the environment.
        # LogicEngine.get_current_state() should provide what's needed.
        initial_state = engine.get_current_state() 

        return jsonify({
            "success": True,
            "game_id": game_id,
            "initial_state": initial_state, # Assuming get_current_state() returns a serializable dict
            "message": "Game created and loaded successfully from prompt."
        }), 201

    except FlatlandRateLimitError as e:
        print(f"LLM Rate Limit Error: {e}")
        return jsonify({"success": False, "message": f"LLM Rate Limit Error: {e.message}", "retry_after": e.retry_after}), 429
    except SchemaValidationError as e:
        print(f"LLM Schema Validation Error: {e}")
        return jsonify({"success": False, "message": f"LLM generated data failed schema validation: {e.message}", "errors": e.validation_errors}), 500
    except FlatlandLLMError as e:
        print(f"Flatland LLM Error: {e}")
        return jsonify({"success": False, "message": f"Error generating environment with LLM: {e.message}"}), 500
    except Exception as e:
        print(f"Error in create_game_from_prompt: {e}")
        return jsonify({"success": False, "message": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/mcp/submit_player_action', methods=['POST'])
def mcp_submit_player_action():
    """MCP Tool: submit_player_action"""
    data = request.get_json()
    if not data or 'game_id' not in data or 'command' not in data: # Changed 'action_key' to 'command'
        return jsonify({"success": False, "message": "Missing 'game_id' or 'command'."}), 400

    game_id = data['game_id']
    command = data['command']

    engine = active_games.get(game_id)
    if not engine:
        return jsonify({"success": False, "message": f"Game with ID '{game_id}' not found."}), 404
    
    try:
        # LogicEngine.process_input directly returns the new state or an error structure
        new_state = engine.process_input(command)
        
        # Check for victory/failure conditions based on the new state
        # LogicEngine might update its internal state regarding victory/failure
        # The returned new_state should ideally include game status.
        
        # Example: if engine.check_victory_conditions() or engine.check_failure_conditions():
        #    pass # Potentially remove from active_games or mark as ended

        return jsonify({"success": True, "new_state": new_state, "message": "Action processed."}), 200
    except Exception as e:
        print(f"Error processing player action for game {game_id}: {e}")
        # LogicEngine's process_input might raise specific exceptions for invalid commands
        return jsonify({"success": False, "message": f"Error processing action: {str(e)}"}), 500


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
    
    try:
        current_state = engine.get_current_state() # Assuming this returns a serializable dict
        if current_state:
            return jsonify({"success": True, "current_state": current_state}), 200
        else:
            return jsonify({"success": False, "message": "Error retrieving game state (state is None)."}), 500
    except Exception as e:
        print(f"Error in get_game_state for game {game_id}: {e}")
        return jsonify({"success": False, "message": f"Error retrieving game state: {str(e)}"}), 500

if __name__ == '__main__':
    load_environment_schema()
    try:
        import flask
    except ImportError:
        print("Flask is not installed. Please install it: pip install Flask")
        exit(1)
    
    # For the LLM client to work, OPENAI_API_KEY or FLATLAND_OPENAI_KEY needs to be set.
    # The create_game_from_prompt endpoint has a check, but good to be aware.
    print("Starting Flatland MCP Server on http://127.0.0.1:5003") # Changed port
    app.run(debug=True, port=5003)
