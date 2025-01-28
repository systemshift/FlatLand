# FlatLand 🗺️

**A Minimalist, Constraint-Driven 2D Framework for Testing LLM-Generated Environments**  
*"Can your LLM build NetHack?"*

[![PyPI Version](https://img.shields.io/pypi/v/flatland.svg)](https://pypi.org/project/flatland/)
[![Tests](https://github.com/systemshift/flatland/actions/workflows/tests.yml/badge.svg)](https://github.com/yourusername/flatland/actions)

![](docs/demo.gif)  
*Example: Sokoban puzzle with rule-based interactions*

## Quick Example

```json
{
  "metadata": {
    "name": "Ice & Fire",
    "description": "Elements interact through rules"
  },
  "rules": [
    {
      "name": "water_freezing",
      "type": "conditional",
      "when": {
        "condition": "entity.type == 'water' && adjacent_to('ice')",
        "entities": ["water", "ice"]
      },
      "then": {
        "action": "transform",
        "parameters": { "type": "ice" }
      }
    }
  ]
}
```

```python
from flatland import LogicEngine

# Load your world definition
engine = LogicEngine()
engine.load_environment("ice_world.json")

# Watch it evolve
while True:
    result = engine.step()
    print(f"Changes: {result['changes']}")
```

## Key Features

- 🎯 **Rule-Based Logic**: Define complex behaviors through conditional, transformation, and constraint rules
- 🔄 **State Management**: Track and validate state changes with built-in history
- ⚡ **Priority System**: Fine-grained control over rule execution order
- 🛡️ **Validation**: Comprehensive JSON schema validation for environments
- 🧩 **Built-in Functions**: Rich toolkit for spatial and state queries
- 🤖 **LLM-Ready**: JSON format designed for AI environment generation

## Installation

```bash
pip install flatland-logic
```

## Core Concepts

### 1. Rule Types

#### Conditional Rules
```json
{
  "name": "push_box",
  "type": "conditional",
  "when": {
    "condition": "entity.type == 'player' && adjacent_to('box')",
    "entities": ["player", "box"]
  },
  "then": {
    "action": "push",
    "parameters": { "direction": "movement_direction" }
  }
}
```

#### Transformation Rules
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
      "probability": 0.3,
      "type": "fire"
    }
  }
}
```

#### Constraint Rules
```json
{
  "name": "gravity",
  "type": "constraint",
  "when": {
    "condition": "entity.movable == true",
    "entities": ["any"]
  },
  "then": {
    "action": "validate",
    "parameters": {
      "condition": "has_support_below"
    }
  }
}
```

### 2. Built-in Functions

| Function | Description |
|----------|-------------|
| `adjacent_to(type)` | Check if entity neighbors type |
| `distance_to(type, max)` | Check distance to nearest type |
| `count_nearby(type, radius)` | Count entities within radius |
| `has_property(prop)` | Check entity properties |
| `can_move_to(x, y)` | Validate movement target |

### 3. State Management

```python
# Get current state
state = engine.state_manager.get_current_state()

# Check history
changes = engine.state_manager.history[-5:]

# Validate state transitions
engine.rule_validator.validate_state(new_state)
```

## Example Environments

Check `examples/` for complete environments:

- 🎮 `sokoban.json`: Classic box-pushing puzzle
- 🌊 `water_physics.json`: Fluid simulation rules
- 🧟 `zombie_spread.json`: Contagion mechanics
- 🔥 `wildfire.json`: Environmental interactions

## LLM Integration

### With Function Calling

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Create a puzzle..."}],
    functions=[{
        "name": "create_environment",
        "parameters": ENVIRONMENT_SCHEMA
    }]
)
```

### With Direct Generation

```python
prompt = """
Create a FlatLand environment where:
1. Water freezes when touching ice
2. Fire melts ice into water
3. Water extinguishes fire
"""

# LLM generates valid JSON following schema
```

## Contributing

1. Fork & Clone
2. Install: `pip install -e .[dev]`
3. Test: `pytest tests/`

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Roadmap

- 📊 Visualization Tools
- 🤖 LLM Generation Templates
- 🔄 State Diffing & Replay
- 🎮 Interactive Debug Mode

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.
