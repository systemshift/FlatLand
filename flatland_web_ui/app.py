from flask import Flask, render_template, request, jsonify
import json
import os

# Assuming the flatland library is installed and accessible
# Or adjust path if running directly from the repository
# For example, if FlatLand is a sibling directory:
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from flatland import LogicEngine, StateManager # Assuming these are the correct imports

app = Flask(__name__)

# Global variable to hold the engine instance
# In a real app, you might manage this differently (e.g., per session)
engine = None
current_environment_data = None

# Path to example environments
EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'examples')
DEFAULT_ENV_FILE = os.path.join(EXAMPLES_DIR, 'sokoban.json')

def load_environment_data(env_path):
    """Loads environment data from a JSON file."""
    try:
        with open(env_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Environment file not found at {env_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {env_path}")
        return None

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/api/load_environment', methods=['POST'])
def load_environment_route():
    """
    Loads a new environment.
    Expects JSON: {"environment_name": "sokoban"} or {"environment_path": "path/to/env.json"}
    or {"environment_data": { ... actual json ... }}
    """
    global engine, current_environment_data
    data = request.get_json()

    env_data_to_load = None

    if 'environment_data' in data:
        env_data_to_load = data['environment_data']
    elif 'environment_name' in data:
        env_file = os.path.join(EXAMPLES_DIR, f"{data['environment_name']}.json")
        env_data_to_load = load_environment_data(env_file)
    elif 'environment_path' in data:
        # For security, ensure this path is within an allowed directory if used in production
        env_data_to_load = load_environment_data(data['environment_path'])
    else: # Default to sokoban if no specific environment is requested
        env_data_to_load = load_environment_data(DEFAULT_ENV_FILE)


    if env_data_to_load:
        try:
            engine = LogicEngine()
            engine.load_environment(env_data_to_load)
            current_environment_data = env_data_to_load
            initial_state = engine.state_manager.get_current_state() # Or however state is fetched
            return jsonify({"success": True, "message": "Environment loaded.", "initial_state": initial_state, "environment_name": env_data_to_load.get("metadata", {}).get("name", "Unknown")}), 200
        except Exception as e:
            return jsonify({"success": False, "message": f"Error loading environment: {str(e)}"}), 500
    else:
        return jsonify({"success": False, "message": "Could not load environment data."}), 400


@app.route('/api/get_initial_state', methods=['GET'])
def get_initial_state_route():
    """Returns the initial state of the currently loaded environment."""
    global engine, current_environment_data
    if engine and current_environment_data:
        try:
            # Re-initialize or get initial state.
            # For simplicity, we might just return the initial_state part of the loaded data
            # Or, if the engine resets, use that.
            initial_state = current_environment_data.get("initial_state")
            if initial_state:
                 # Ensure engine is reset to initial state if needed
                temp_engine = LogicEngine()
                temp_engine.load_environment(current_environment_data)
                return jsonify({"success": True, "initial_state": temp_engine.state_manager.get_current_state(), "environment_name": current_environment_data.get("metadata", {}).get("name", "Unknown")}), 200
            else:
                return jsonify({"success": False, "message": "Initial state not found in environment data."}), 404
        except Exception as e:
            return jsonify({"success": False, "message": f"Error getting initial state: {str(e)}"}), 500
    else:
        return jsonify({"success": False, "message": "No environment loaded."}), 404


@app.route('/api/process_command', methods=['POST'])
def process_command_route():
    """
    Processes a player command.
    Expects JSON: {"command": "your_command_string"}
    """
    global engine
    if not engine:
        return jsonify({"success": False, "message": "No environment loaded. Please load an environment first."}), 400

    data = request.get_json()
    command = data.get('command')

    if not command:
        return jsonify({"success": False, "message": "No command provided."}), 400

    try:
        result = engine.process_input(command) # process_input is from README
        # The result structure might be {"state": new_state, "changes": changes_list, "message": "optional_message"}
        # Adjust based on actual LogicEngine.process_input() return value
        return jsonify({"success": True, "result": result}), 200
    except Exception as e:
        # Catching generic Exception, specific exceptions from LogicEngine would be better
        return jsonify({"success": False, "message": f"Error processing command: {str(e)}"}), 500

if __name__ == '__main__':
    # Try to load default environment on startup
    default_env_data = load_environment_data(DEFAULT_ENV_FILE)
    if default_env_data:
        engine = LogicEngine()
        engine.load_environment(default_env_data)
        current_environment_data = default_env_data
        print(f"Default environment '{default_env_data.get('metadata',{}).get('name', 'sokoban')}' loaded.")
    else:
        print("Could not load default environment on startup.")
    app.run(debug=True, port=5001)
