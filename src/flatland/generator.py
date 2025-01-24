from typing import Dict, Any, List, Optional
import json
from dataclasses import dataclass
import jsonschema
from .schemas import ENVIRONMENT_SCHEMA, EnvironmentDefinition
from .world import World

@dataclass
class GeneratorResponse:
    """Container for the generator response."""
    definition: EnvironmentDefinition
    metadata: Dict[str, Any]
    error: Optional[str] = None

class EnvironmentGenerator:
    """Handles generation and validation of environments."""
    
    def __init__(self):
        """Initialize the generator."""
        self._default_template = {
            "metadata": {
                "name": "Default Environment",
                "description": "A basic environment"
            },
            "grid": {
                "width": 10,
                "height": 10,
                "initial_state": [[0] * 10 for _ in range(10)]
            },
            "entities": [],
            "rules": []
        }
    
    def validate_definition(self, definition: Dict[str, Any]) -> Optional[str]:
        """Validate an environment definition against the schema.
        
        Args:
            definition: Dictionary containing environment definition
            
        Returns:
            Error message if invalid, None if valid
        """
        try:
            jsonschema.validate(definition, ENVIRONMENT_SCHEMA)
            return None
        except jsonschema.exceptions.ValidationError as e:
            return f"Schema validation error: {str(e)}"
        except Exception as e:
            return f"Validation error: {str(e)}"
    
    def from_json(self, json_str: str) -> GeneratorResponse:
        """Create environment from JSON string.
        
        Args:
            json_str: JSON string containing environment definition
            
        Returns:
            GeneratorResponse containing parsed definition or error
        """
        try:
            data = json.loads(json_str)
            error = self.validate_definition(data)
            if error:
                return GeneratorResponse(
                    definition=EnvironmentDefinition.from_dict(self._default_template),
                    metadata={},
                    error=error
                )
            
            definition = EnvironmentDefinition.from_dict(data)
            return GeneratorResponse(
                definition=definition,
                metadata={
                    "size": (definition.grid["width"], definition.grid["height"]),
                    "entity_count": len(definition.entities),
                    "rule_count": len(definition.rules)
                }
            )
        except Exception as e:
            return GeneratorResponse(
                definition=EnvironmentDefinition.from_dict(self._default_template),
                metadata={},
                error=f"Failed to parse JSON: {str(e)}"
            )
    
    def to_world(self, definition: EnvironmentDefinition) -> World:
        """Convert environment definition to World instance.
        
        Args:
            definition: The environment definition to convert
            
        Returns:
            World instance configured according to definition
        """
        world = World(definition.grid["width"], definition.grid["height"])
        
        # Set initial grid state if provided
        if "initial_state" in definition.grid:
            for y, row in enumerate(definition.grid["initial_state"]):
                for x, cell in enumerate(row):
                    world.grid.set_cell(x, y, cell)
        
        # Add entities
        for entity in definition.entities:
            x, y = entity["position"]
            world.add_entity(
                x, y,
                entity["type"],
                entity.get("properties", {})
            )
        
        # Apply rules
        for rule in definition.rules:
            if rule["type"] == "cardinal_movement":
                world.constraint_engine.add_constraint(
                    "cardinal_movement",
                    lambda w, a: abs(a[1][0]) + abs(a[1][1]) == 1 if a[0] == "move" else True,
                    "Can only move in cardinal directions"
                )
            elif rule["type"] == "inventory_limit":
                limit = rule.get("properties", {}).get("max_items", 1)
                world.constraint_engine.add_constraint(
                    "inventory_limit",
                    lambda w, a, limit=limit: len(w.inventory) < limit if a[0] == "pickup" else True,
                    f"Cannot carry more than {limit} items"
                )
        
        return world
    
    def to_json(self, world: World) -> str:
        """Convert World instance to JSON definition.
        
        Args:
            world: The World instance to convert
            
        Returns:
            JSON string containing environment definition
        """
        definition = {
            "metadata": {
                "name": "Exported Environment",
                "description": "Environment exported from World instance"
            },
            "grid": {
                "width": world.grid.width,
                "height": world.grid.height,
                "initial_state": [
                    [world.grid.get_cell(x, y) for x in range(world.grid.width)]
                    for y in range(world.grid.height)
                ]
            },
            "entities": [
                {
                    "type": entity_type,
                    "position": [x, y],
                    "properties": data if data else {}
                }
                for (x, y), (entity_type, data) in world.entities.items()
            ],
            "rules": []  # TODO: Export constraints as rules
        }
        
        return json.dumps(definition, indent=2)
