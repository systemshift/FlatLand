from typing import Dict, Any, Optional
import json

class EnvironmentTemplate:
    """Base class for environment templates."""
    
    def get_schema(self) -> dict:
        """Get the schema for this template's parameters."""
        return {
            "type": "object",
            "properties": {}
        }
    
    def generate(self, params: Dict[str, Any]) -> str:
        """Generate environment JSON from parameters."""
        raise NotImplementedError

class MazeTemplate(EnvironmentTemplate):
    """Template for generating maze-like environments."""
    
    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "width": {"type": "integer", "minimum": 5, "default": 10},
                "height": {"type": "integer", "minimum": 5, "default": 10},
                "keys_required": {"type": "integer", "minimum": 0, "default": 1},
                "difficulty": {
                    "type": "string",
                    "enum": ["easy", "medium", "hard"],
                    "default": "medium"
                }
            }
        }
    
    def generate(self, params: Dict[str, Any]) -> str:
        width = params.get("width", 10)
        height = params.get("height", 10)
        keys = params.get("keys_required", 1)
        difficulty = params.get("difficulty", "medium")
        
        # Create basic maze structure
        definition = {
            "metadata": {
                "name": f"{difficulty.title()} Maze",
                "description": f"A {width}x{height} maze with {keys} keys required"
            },
            "grid": {
                "width": width,
                "height": height,
                "initial_state": [[0] * width for _ in range(height)]
            },
            "entities": [],
            "rules": [
                {
                    "type": "cardinal_movement",
                    "properties": {}
                },
                {
                    "type": "inventory_limit",
                    "properties": {"max_items": keys}
                }
            ]
        }
        
        # Add walls around edges
        for x in range(width):
            definition["grid"]["initial_state"][0][x] = 1
            definition["grid"]["initial_state"][height-1][x] = 1
        for y in range(height):
            definition["grid"]["initial_state"][y][0] = 1
            definition["grid"]["initial_state"][y][width-1] = 1
        
        # Add keys and doors based on difficulty
        if difficulty == "easy":
            definition["entities"].append({
                "type": "key",
                "position": [1, 1],
                "properties": {}
            })
            definition["entities"].append({
                "type": "door",
                "position": [width-2, height-2],
                "properties": {}
            })
        elif difficulty == "medium":
            definition["entities"].extend([
                {"type": "key", "position": [1, 1], "properties": {}},
                {"type": "key", "position": [width-2, 1], "properties": {}},
                {"type": "door", "position": [1, height-2], "properties": {}},
                {"type": "door", "position": [width-2, height-2], "properties": {}}
            ])
        else:  # hard
            definition["entities"].extend([
                {"type": "key", "position": [1, 1], "properties": {}},
                {"type": "key", "position": [width-2, 1], "properties": {}},
                {"type": "key", "position": [width//2, height//2], "properties": {}},
                {"type": "door", "position": [1, height-2], "properties": {}},
                {"type": "door", "position": [width-2, height-2], "properties": {}},
                {"type": "door", "position": [width//2, height-2], "properties": {}}
            ])
        
        return json.dumps(definition, indent=2)

class PuzzleTemplate(EnvironmentTemplate):
    """Template for generating puzzle environments."""
    
    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "width": {"type": "integer", "minimum": 5, "default": 8},
                "height": {"type": "integer", "minimum": 5, "default": 8},
                "puzzle_type": {
                    "type": "string",
                    "enum": ["sokoban", "sliding", "switches"],
                    "default": "sokoban"
                }
            }
        }
    
    def generate(self, params: Dict[str, Any]) -> str:
        width = params.get("width", 8)
        height = params.get("height", 8)
        puzzle_type = params.get("puzzle_type", "sokoban")
        
        definition = {
            "metadata": {
                "name": f"{puzzle_type.title()} Puzzle",
                "description": f"A {width}x{height} {puzzle_type} puzzle"
            },
            "grid": {
                "width": width,
                "height": height,
                "initial_state": [[0] * width for _ in range(height)]
            },
            "entities": [],
            "rules": [
                {"type": "cardinal_movement", "properties": {}}
            ]
        }
        
        if puzzle_type == "sokoban":
            # Add pushable blocks and targets
            definition["entities"].extend([
                {"type": "block", "position": [width//2, height//2], "properties": {"pushable": True}},
                {"type": "target", "position": [width-2, height-2], "properties": {}}
            ])
        elif puzzle_type == "sliding":
            # Add sliding tiles
            for i in range(4):
                definition["entities"].append({
                    "type": "tile",
                    "position": [1+i, 1],
                    "properties": {"number": i+1}
                })
        else:  # switches
            # Add switches and doors
            definition["entities"].extend([
                {"type": "switch", "position": [1, 1], "properties": {"id": 1}},
                {"type": "door", "position": [width-2, 1], "properties": {"switch_id": 1}},
                {"type": "switch", "position": [1, height-2], "properties": {"id": 2}},
                {"type": "door", "position": [width-2, height-2], "properties": {"switch_id": 2}}
            ])
        
        return json.dumps(definition, indent=2)

# Registry of available templates
TEMPLATES = {
    "maze": MazeTemplate(),
    "puzzle": PuzzleTemplate()
}

def get_template(name: str) -> Optional[EnvironmentTemplate]:
    """Get a template by name."""
    return TEMPLATES.get(name)

def list_templates() -> Dict[str, dict]:
    """Get all available templates and their schemas."""
    return {name: template.get_schema() for name, template in TEMPLATES.items()}
