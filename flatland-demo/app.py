"""
Simplified Flask demo for FlatLand web interface
"""
import os
import sys
import json
import uuid
from flask import Flask, request, jsonify, render_template

# Add the FlatLand directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import FlatLand modules
try:
    from src.flatland.llm.client import EnvironmentGenerator
    from src.flatland.logic_engine import LogicEngine
    from src.flatland.state_manager import StateManager
except ImportError:
    print("Error importing FlatLand modules. Make sure the path is correct.")
    sys.exit(1)

app = Flask(__name__, static_folder='app/static', template_folder='app/templates')

# Session storage for environments
sessions = {}

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_environment():
    """Generate a new environment from a text description"""
    try:
        data = request.json
        description = data.get('description', '')
        style_guidance = data.get('style_guidance', '')
        model = data.get('model', 'gpt-4-turbo-preview')
        
        # Initialize environment generator
        generator = EnvironmentGenerator()
        
        # Generate environment
        environment = generator.generate(
            description=description,
            style_guidance=style_guidance,
            model=model
        )
        
        # Create a session ID
        session_id = str(uuid.uuid4())
        
        # Initialize LogicEngine and StateManager
        logic_engine = LogicEngine(environment)
        state_manager = StateManager(environment)
        
        # Store session data
        sessions[session_id] = {
            "environment": environment,
            "logic_engine": logic_engine,
            "state_manager": state_manager
        }
        
        # Return the initial state
        return jsonify({
            "session_id": session_id,
            "environment": environment,
            "state": state_manager.current_state
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/input', methods=['POST'])
def process_input():
    """Process user input for a simulation"""
    try:
        data = request.json
        session_id = data.get('session_id')
        input_command = data.get('input_command')
        
        if session_id not in sessions:
            return jsonify({"error": "Session not found"}), 404
        
        session = sessions[session_id]
        logic_engine = session["logic_engine"]
        state_manager = session["state_manager"]
        
        # Process input
        logic_engine.process_input(input_command)
        
        # Return the updated state
        return jsonify({
            "success": True,
            "state": state_manager.current_state
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/step', methods=['POST'])
def step_simulation():
    """Process a single step in the simulation"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if session_id not in sessions:
            return jsonify({"error": "Session not found"}), 404
        
        session = sessions[session_id]
        logic_engine = session["logic_engine"]
        state_manager = session["state_manager"]
        
        # Process step
        logic_engine.step()
        
        # Return the updated state
        return jsonify({
            "success": True,
            "state": state_manager.current_state
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/state/<session_id>', methods=['GET'])
def get_state(session_id):
    """Get the current state of a simulation"""
    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404
    
    session = sessions[session_id]
    state_manager = session["state_manager"]
    
    return jsonify({
        "state": state_manager.current_state,
        "environment": session["environment"]
    })

if __name__ == '__main__':
    # Load OpenAI API key from environment
    openai_key = os.environ.get('OPENAI_API_KEY')
    if not openai_key:
        with open('.env') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    openai_key = line.split('=', 1)[1].strip()
                    os.environ['OPENAI_API_KEY'] = openai_key
                    os.environ['FLATLAND_OPENAI_KEY'] = openai_key
                    break
    
    app.run(debug=True, host='0.0.0.0', port=5000)