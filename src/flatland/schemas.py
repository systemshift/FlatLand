from typing import Dict, Any
from dataclasses import dataclass

ENVIRONMENT_SCHEMA = {
    "type": "object",
    "required": ["metadata", "grid", "entities"],
    "properties": {
        "metadata": {
            "type": "object",
            "required": ["name", "description"],
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "version": {"type": "string", "default": "1.0"}
            }
        },
        "grid": {
            "type": "object",
            "required": ["width", "height"],
            "properties": {
                "width": {"type": "integer", "minimum": 1},
                "height": {"type": "integer", "minimum": 1},
                "initial_state": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "integer"}
                    }
                }
            }
        },
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type", "position"],
                "properties": {
                    "type": {"type": "string"},
                    "position": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "minItems": 2,
                        "maxItems": 2
                    },
                    "properties": {
                        "type": "object",
                        "default": {}
                    }
                }
            }
        },
        "rules": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type"],
                "properties": {
                    "type": {"type": "string"},
                    "properties": {
                        "type": "object",
                        "default": {}
                    }
                }
            },
            "default": []
        }
    }
}

@dataclass
class EnvironmentDefinition:
    """Container for parsed environment definition."""
    metadata: Dict[str, str]
    grid: Dict[str, Any]
    entities: list
    rules: list

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnvironmentDefinition':
        """Create EnvironmentDefinition from dictionary."""
        return cls(
            metadata=data["metadata"],
            grid=data["grid"],
            entities=data["entities"],
            rules=data.get("rules", [])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "metadata": self.metadata,
            "grid": self.grid,
            "entities": self.entities,
            "rules": self.rules
        }
