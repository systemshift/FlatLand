"""
Simplified Flask demo for FlatLand web interface - without actual API calls
"""
import os
import json
import uuid
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, static_folder='app/static', template_folder='app/templates')

# Session storage for environments
sessions = {}

# Example environment definition
EXAMPLE_ENVIRONMENTS = {
    "sokoban": {
        "metadata": {
            "name": "Sokoban Game",
            "description": "Push boxes onto target locations to win!"
        },
        "grid": [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1]
        ],
        "entities": [
            {"id": "player", "type": "player", "position": [3, 3]},
            {"id": "box1", "type": "box", "position": [3, 4]},
            {"id": "goal1", "type": "goal", "position": [5, 5]}
        ],
        "rules": [
            {
                "id": "rule1",
                "name": "Player Movement",
                "when": {"type": "adjacent", "entity": "player"},
                "then": {"type": "move", "entity": "player"}
            },
            {
                "id": "rule2",
                "name": "Box Pushing",
                "when": {"type": "push", "entity": "box"},
                "then": {"type": "move", "entity": "box"}
            }
        ]
    },
    
    "snake": {
        "metadata": {
            "name": "Snake Game",
            "description": "Collect food to grow your snake. Don't hit the walls or yourself!"
        },
        "grid": [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ],
        "entities": [
            {"id": "snake_head", "type": "player", "position": [5, 5]},
            {"id": "snake_body1", "type": "snake_body", "position": [5, 4]},
            {"id": "snake_body2", "type": "snake_body", "position": [5, 3]},
            {"id": "food", "type": "food", "position": [3, 7]}
        ],
        "rules": [
            {
                "id": "rule1",
                "name": "Snake Movement",
                "when": {"type": "input", "entity": "snake_head"},
                "then": {"type": "move", "entity": "snake_head"}
            }
        ]
    }
}

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_environment():
    """Generate a new environment from a text description (mock)"""
    try:
        data = request.json
        description = data.get('description', '').lower()
        
        # Very simple keyword matching to select a pre-defined environment
        if "sokoban" in description or "box" in description or "push" in description:
            environment = EXAMPLE_ENVIRONMENTS["sokoban"]
        else:
            environment = EXAMPLE_ENVIRONMENTS["snake"]
        
        # Create a session ID
        session_id = str(uuid.uuid4())
        
        # Store session data with initial state
        initial_state = {
            "grid": environment["grid"],
            "entities": environment["entities"]
        }
        
        sessions[session_id] = {
            "environment": environment,
            "current_state": initial_state
        }
        
        # Return the initial state
        return jsonify({
            "session_id": session_id,
            "environment": environment,
            "state": initial_state
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/input', methods=['POST'])
def process_input():
    """Process user input for a simulation (simplified)"""
    try:
        data = request.json
        session_id = data.get('session_id')
        input_command = data.get('input_command')
        
        if session_id not in sessions:
            return jsonify({"error": "Session not found"}), 404
        
        session = sessions[session_id]
        current_state = session["current_state"]
        
        # Basic movement logic
        for entity in current_state["entities"]:
            if entity["type"] == "player":
                y, x = entity["position"]
                
                if input_command == "up" and current_state["grid"][y-1][x] != 1:
                    entity["position"][0] -= 1
                elif input_command == "down" and current_state["grid"][y+1][x] != 1:
                    entity["position"][0] += 1
                elif input_command == "left" and current_state["grid"][y][x-1] != 1:
                    entity["position"][1] -= 1
                elif input_command == "right" and current_state["grid"][y][x+1] != 1:
                    entity["position"][1] += 1
                
                # Basic box pushing for Sokoban
                if "sokoban" in session["environment"]["metadata"]["name"].lower():
                    for box in [e for e in current_state["entities"] if e["type"] == "box"]:
                        if box["position"] == entity["position"]:
                            # Determine push direction
                            if input_command == "up":
                                box["position"][0] -= 1
                            elif input_command == "down":
                                box["position"][0] += 1
                            elif input_command == "left":
                                box["position"][1] -= 1
                            elif input_command == "right":
                                box["position"][1] += 1
                break
        
        # Return the updated state
        return jsonify({
            "success": True,
            "state": current_state
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/step', methods=['POST'])
def step_simulation():
    """Process a single step in the simulation (simplified)"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if session_id not in sessions:
            return jsonify({"error": "Session not found"}), 404
        
        session = sessions[session_id]
        current_state = session["current_state"]
        
        # Simplified step logic
        if "snake" in session["environment"]["metadata"]["name"].lower():
            # Move snake body
            snake_parts = sorted([e for e in current_state["entities"] 
                                  if e["type"] == "player" or e["type"] == "snake_body"],
                                key=lambda x: x["id"])
            
            # Follow-the-leader movement - very simplified
            prev_positions = [list(part["position"]) for part in snake_parts]
            
            for i in range(1, len(snake_parts)):
                snake_parts[i]["position"] = prev_positions[i-1]
        
        # Return the updated state
        return jsonify({
            "success": True,
            "state": current_state
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/state/<session_id>', methods=['GET'])
def get_state(session_id):
    """Get the current state of a simulation"""
    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404
    
    session = sessions[session_id]
    
    return jsonify({
        "state": session["current_state"],
        "environment": session["environment"]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)