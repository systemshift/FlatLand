"""
Integration tests for the FlatLand library.
"""

import json
import pytest

from flatland import (
    LogicEngine, 
    StateManager, 
    BuiltInFunctions, 
    SchemaValidator,
    ValidationError
)

# Sample valid environment for testing
VALID_ENV = {
    "metadata": {
        "name": "Test Environment",
        "description": "A test environment for integration testing"
    },
    "initial_state": {
        "grid": {
            "width": 5,
            "height": 5,
            "cells": [
                [1, 1, 1, 1, 1],
                [1, 0, 0, 0, 1],
                [1, 0, 2, 0, 1],
                [1, 0, 0, 0, 1],
                [1, 1, 1, 1, 1]
            ]
        },
        "entities": [
            {
                "id": "player",
                "type": "player",
                "position": [2, 2],
                "properties": {
                    "movable": True
                }
            }
        ]
    },
    "rules": [
        {
            "name": "player_movement",
            "type": "conditional",
            "priority": 1,
            "when": {
                "condition": "entity.type == 'player' && can_move_to(target_x, target_y)",
                "entities": ["player"]
            },
            "then": {
                "action": "move",
                "parameters": {
                    "position": ["target_x", "target_y"]
                }
            }
        }
    ]
}

def test_schema_validator():
    """Test that the schema validator works correctly."""
    validator = SchemaValidator()
    
    # Test valid environment
    is_valid, errors = validator.validate_environment(VALID_ENV)
    assert is_valid
    assert errors is None
    
    # Test invalid environment (missing description)
    invalid_env = {
        "metadata": {
            "name": "Invalid Environment"
            # Missing description
        },
        "initial_state": VALID_ENV["initial_state"]
    }
    
    is_valid, errors = validator.validate_environment(invalid_env)
    assert not is_valid
    assert errors is not None
    assert len(errors) > 0

def test_state_manager():
    """Test that the state manager works correctly."""
    state_manager = StateManager()
    
    # Set initial state
    state_manager.set_initial_state(VALID_ENV["initial_state"])
    
    # Get current state
    state = state_manager.get_current_state()
    assert state["grid"]["width"] == 5
    assert state["grid"]["height"] == 5
    assert len(state["entities"]) == 1
    assert state["entities"][0]["id"] == "player"
    
    # Test state diffing
    modified_state = state_manager.get_current_state()
    modified_state["entities"][0]["position"] = [3, 2]
    
    diff = state_manager.compute_state_diff(state, modified_state)
    assert len(diff["entities"]) == 1
    assert diff["entities"][0]["action"] == "modify"
    assert diff["entities"][0]["changes"]["position"]["old"] == [2, 2]
    assert diff["entities"][0]["changes"]["position"]["new"] == [3, 2]
    
    # Test applying diff
    new_state = state_manager.apply_diff(state, diff)
    assert new_state["entities"][0]["position"] == [3, 2]

def test_built_in_functions():
    """Test that the built-in functions work correctly."""
    state = VALID_ENV["initial_state"]
    
    # Add current entity for testing
    state["current_entity"] = state["entities"][0]
    
    # Test check_movement
    assert BuiltInFunctions.check_movement(state, 1, 2)  # Valid move
    assert not BuiltInFunctions.check_movement(state, 0, 0)  # Wall
    
    # Test check_adjacent
    assert not BuiltInFunctions.check_adjacent(state, "wall")  # No wall adjacent
    
    # Test function context
    context = BuiltInFunctions.create_function_context(state)
    assert "adjacent_to" in context
    assert "distance_to" in context
    assert "count_nearby" in context
    assert "has_property" in context
    assert "is_type" in context
    assert "can_move_to" in context

def test_logic_engine():
    """Test that the logic engine works correctly."""
    engine = LogicEngine()
    
    # Load environment
    engine.load_environment(VALID_ENV)
    
    # Test process_input
    result = engine.process_input("right")
    assert "error" not in result
    assert result["changes"][0]["effect"]["from"] == [2, 2]
    assert result["changes"][0]["effect"]["to"] == [3, 2]
    
    # Test step
    result = engine.step()
    assert "state" in result
    assert "changes" in result
    assert "victory" in result
    assert "failure" in result

def test_integration():
    """Test the integration of all components."""
    # Create engine
    engine = LogicEngine()
    
    # Load environment
    engine.load_environment(VALID_ENV)
    
    # Process input
    result = engine.process_input("right")
    print(f"Process input result: {result}")
    assert "error" not in result
    
    # Get state
    state = result["state"]
    
    # Verify player moved
    player = next((e for e in state["entities"] if e["type"] == "player"), None)
    print(f"Player entity: {player}")
    assert player is not None
    
    # Check if player position is updated
    print(f"Player position: {player['position']}")
    assert player["position"] == [3, 2]
    
    # Verify grid updated
    print(f"Grid cell at old position: {state['grid']['cells'][2][2]}")
    print(f"Grid cell at new position: {state['grid']['cells'][2][3]}")
    assert state["grid"]["cells"][2][2] == 4  # Old position is marked as goal (4)
    assert state["grid"]["cells"][2][3] == 2  # New position has player (2)
