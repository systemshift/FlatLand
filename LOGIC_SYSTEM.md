# FlatLand Logic System

A constraint-based logic engine for LLM-driven simulations.

## Overview

The FlatLand Logic System is a rule-based simulation engine that enables LLMs to define complex environments and behaviors through declarative JSON. The system focuses on logical rules and state transitions rather than real-time physics, making it ideal for turn-based simulations, puzzle games, and cellular automata.

## Core Components

### 1. LogicEngine
- Evaluates rules and manages state transitions
- Handles rule priority and execution order
- Ensures deterministic behavior
- Detects and prevents rule conflicts

### 2. StateManager
- Maintains the current world state
- Tracks entity positions and properties
- Manages state history for undo/validation
- Provides state query interface

### 3. RuleValidator
- Validates rule definitions
- Checks for circular dependencies
- Ensures rule consistency
- Validates state transitions

## JSON Schema

### Environment Definition
```json
{
  "metadata": {
    "name": "string",
    "description": "string",
    "version": "string"
  },
  "initial_state": {
    "grid": {
      "width": "number",
      "height": "number",
      "cells": [
        [0, 1, 2] // 0=empty, 1=wall, 2=entity, etc.
      ]
    },
    "entities": [
      {
        "id": "string",
        "type": "string",
        "position": [0, 0],
        "properties": {
          "movable": "boolean",
          "destructible": "boolean",
          "state": "string",
          "custom_props": "any"
        }
      }
    ]
  },
  "rules": [
    {
      "name": "string",
      "type": "conditional | transformation | constraint",
      "priority": "number",
      "when": {
        "condition": "string",
        "entities": ["string"]
      },
      "then": {
        "action": "string",
        "parameters": {
          "target": "self | other | position",
          "effect": "object"
        }
      }
    }
  ],
  "victory_conditions": [
    {
      "type": "state | position | collection",
      "condition": "string"
    }
  ],
  "failure_conditions": [
    {
      "type": "state | position | collection",
      "condition": "string"
    }
  ]
}
```

## Rule Types

### 1. Conditional Rules
IF-THEN rules that trigger state changes based on conditions.

Example:
```json
{
  "name": "water_freezing",
  "type": "conditional",
  "priority": 1,
  "when": {
    "condition": "entity.type == 'water' && adjacent_to('ice')",
    "entities": ["water", "ice"]
  },
  "then": {
    "action": "transform",
    "parameters": {
      "target": "self",
      "effect": {
        "type": "ice"
      }
    }
  }
}
```

### 2. Transformation Rules
Rules that define how entities change over time or interact.

Example:
```json
{
  "name": "fire_spread",
  "type": "transformation",
  "priority": 2,
  "when": {
    "condition": "entity.type == 'fire'",
    "entities": ["fire"]
  },
  "then": {
    "action": "spread",
    "parameters": {
      "target": "adjacent",
      "effect": {
        "type": "fire",
        "probability": 0.3
      }
    }
  }
}
```

### 3. Constraint Rules
Rules that enforce limitations and validate actions.

Example:
```json
{
  "name": "gravity",
  "type": "constraint",
  "priority": 0,
  "when": {
    "condition": "entity.movable == true",
    "entities": ["any"]
  },
  "then": {
    "action": "validate",
    "parameters": {
      "condition": "has_support_below",
      "failure": {
        "action": "move",
        "direction": [0, 1]
      }
    }
  }
}
```

## Built-in Functions

The rule system provides several built-in functions for conditions:

- `adjacent_to(type)`: Check if entity is adjacent to type
- `distance_to(type, max)`: Check if entity is within distance
- `count_nearby(type, radius)`: Count entities of type within radius
- `has_property(prop)`: Check if entity has property
- `is_type(type)`: Check if entity is of type
- `can_move_to(x, y)`: Check if position is valid for movement

## Implementation Steps

1. Core System Setup
   - Create LogicEngine class
   - Implement StateManager
   - Build RuleValidator

2. Rule Processing
   - Parse rule definitions
   - Build rule dependency graph
   - Implement rule evaluation engine

3. State Management
   - Design state representation
   - Implement state transitions
   - Add state validation

4. Integration
   - Create JSON parser/validator
   - Add LLM interface
   - Implement simulation loop

## Example: Sokoban Puzzle

```json
{
  "metadata": {
    "name": "Simple Sokoban",
    "description": "Push boxes to goals"
  },
  "initial_state": {
    "grid": {
      "width": 5,
      "height": 5,
      "cells": [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 2, 0, 1],
        [1, 0, 3, 0, 1],
        [1, 1, 1, 1, 1]
      ]
    },
    "entities": [
      {
        "id": "player",
        "type": "player",
        "position": [2, 2],
        "properties": {
          "movable": true
        }
      },
      {
        "id": "box1",
        "type": "box",
        "position": [2, 3],
        "properties": {
          "movable": true,
          "pushable": true
        }
      }
    ]
  },
  "rules": [
    {
      "name": "push_box",
      "type": "conditional",
      "when": {
        "condition": "entity.type == 'player' && adjacent_to('box')",
        "entities": ["player", "box"]
      },
      "then": {
        "action": "push",
        "parameters": {
          "target": "box",
          "direction": "movement_direction"
        }
      }
    }
  ],
  "victory_conditions": [
    {
      "type": "position",
      "condition": "all_boxes_on_goals"
    }
  ]
}
```

## Next Steps

1. Create base classes for core components
2. Implement JSON schema validation
3. Build rule parser and evaluator
4. Add state management system
5. Create example environments
6. Add LLM integration
7. Build testing framework

## Usage with LLMs

LLMs can generate environment definitions by:
1. Analyzing user requirements
2. Creating appropriate entities and rules
3. Defining victory/failure conditions
4. Generating JSON output
5. Iterating based on validation results

The system will validate and execute the LLM-generated environments, providing feedback on any issues or conflicts that need to be resolved.
