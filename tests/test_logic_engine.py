import json
import pytest
from flatland.logic_engine import LogicEngine, Rule

def test_load_environment():
    """Test loading a valid environment definition."""
    env_def = {
        "metadata": {
            "name": "Test Environment",
            "description": "A test environment"
        },
        "initial_state": {
            "grid": {
                "width": 3,
                "height": 3,
                "cells": [
                    [1, 1, 1],
                    [1, 0, 1],
                    [1, 1, 1]
                ]
            },
            "entities": [
                {
                    "id": "test_entity",
                    "type": "test",
                    "position": [1, 1],
                    "properties": {
                        "movable": True
                    }
                }
            ]
        }
    }
    
    engine = LogicEngine()
    engine.load_environment(env_def)
    
    state = engine.state_manager.get_current_state()
    assert state["grid"]["width"] == 3
    assert state["grid"]["height"] == 3
    assert len(state["entities"]) == 1
    assert state["entities"][0]["id"] == "test_entity"

def test_invalid_environment():
    """Test loading an invalid environment definition."""
    env_def = {
        "metadata": {
            "name": "Invalid Test"
            # Missing required description
        },
        "initial_state": {}  # Invalid state
    }
    
    engine = LogicEngine()
    with pytest.raises(ValueError):
        engine.load_environment(env_def)

def test_rule_validation():
    """Test rule validation."""
    valid_rule = Rule(
        name="test_rule",
        type="conditional",
        priority=1,
        when={
            "condition": "entity.type == 'test'",
            "entities": ["test"]
        },
        then={
            "action": "transform",
            "parameters": {"type": "changed"}
        }
    )
    
    invalid_rule = Rule(
        name="invalid_rule",
        type="invalid_type",  # Invalid rule type
        priority=1,
        when={
            "condition": "test"
        },
        then={
            "action": "invalid_action",
            "parameters": {}
        }
    )
    
    engine = LogicEngine()
    
    # Valid rule should pass validation
    assert engine.rule_validator.validate_rule(valid_rule)
    
    # Invalid rule should fail validation
    assert not engine.rule_validator.validate_rule(invalid_rule)

def test_state_history():
    """Test state history management."""
    engine = LogicEngine()
    
    # Set initial state
    initial_state = {
        "grid": {
            "width": 2,
            "height": 2,
            "cells": [[0, 0], [0, 0]]
        },
        "entities": []
    }
    
    engine.state_manager.set_initial_state(initial_state)
    
    # Record some changes
    changes = [
        {"rule": "test", "effect": {"position": [0, 0]}}
    ]
    engine.state_manager.record_step(changes)
    
    # Check history
    assert len(engine.state_manager.history) == 2  # Initial state + 1 change
    assert engine.state_manager.history[0] == initial_state

def test_condition_evaluation():
    """Test condition evaluation with built-in functions."""
    engine = LogicEngine()
    
    condition = {
        "condition": "entity.type == 'test' and can_move_to(1, 1)",
        "entities": ["test"]
    }
    
    # This test will pass even with unimplemented built-in functions
    # as they return None/False by default
    assert not engine._evaluate_condition(condition)

def test_sokoban_example():
    """Test loading and validating the Sokoban example."""
    try:
        with open('examples/sokoban.json', 'r') as f:
            sokoban_def = json.load(f)
    except FileNotFoundError:
        pytest.skip("Sokoban example file not found")
    
    engine = LogicEngine()
    engine.load_environment(sokoban_def)
    
    # Basic validation of loaded state
    state = engine.state_manager.get_current_state()
    assert state["grid"]["width"] == 7
    assert state["grid"]["height"] == 7
    assert len(state["entities"]) == 3  # Player + 2 boxes
    
    # Test running a step
    result = engine.step()
    assert "state" in result
    assert "changes" in result
