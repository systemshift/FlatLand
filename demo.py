from flatland import set_api_key, LogicEngine

# Read the API key from the file (if available)
try:
    with open("openai_key.txt", "r") as f:
        api_key = f.read().strip()
    set_api_key(api_key)
    print("API key has been set successfully.")
except Exception as e:
    print(f"Could not set API key: {e}")

# Create a simple dummy environment for demonstration
dummy_env = {
    "metadata": {
        "name": "Test Environment",
        "description": "A simple test environment for demo."
    },
    "initial_state": {
        "grid": {
            "width": 5,
            "height": 5,
            "cells": [
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0]
            ]
        },
        "entities": [
            {
                "id": 1,
                "type": "player",
                "position": [2, 2],
                "properties": {}
            }
        ]
    },
    "rules": []
}

# Initialize the simulation engine and load the environment
engine = LogicEngine()
try:
    engine.load_environment(dummy_env)
    print("Environment loaded successfully.")
except Exception as e:
    print(f"Error loading environment: {e}")

# Display the current state of the simulation
current_state = engine.state_manager.get_current_state()
print("Current State:")
print(current_state)
