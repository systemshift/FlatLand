from typing import Dict, Any
from dataclasses import dataclass

ENVIRONMENT_SCHEMA = {
    "type": "object",
    "required": ["metadata", "initial_state"],
    "properties": {
        "metadata": {
            "type": "object",
            "required": ["name", "description"],
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "version": {"type": "string"}
            }
        },
        "initial_state": {
            "type": "object",
            "required": ["grid", "entities"],
            "properties": {
                "grid": {
                    "type": "object",
                    "required": ["width", "height", "cells"],
                    "properties": {
                        "width": {"type": "number"},
                        "height": {"type": "number"},
                        "cells": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {"type": "number"}
                            }
                        }
                    }
                },
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["id", "type", "position"],
                        "properties": {
                            "id": {"type": "string"},
                            "type": {"type": "string"},
                            "position": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 2,
                                "maxItems": 2
                            },
                            "properties": {
                                "type": "object",
                                "properties": {
                                    "movable": {"type": "boolean"},
                                    "destructible": {"type": "boolean"},
                                    "state": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "rules": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "type", "when", "then"],
                "properties": {
                    "name": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": ["conditional", "transformation", "constraint"]
                    },
                    "priority": {"type": "number"},
                    "when": {
                        "type": "object",
                        "required": ["condition"],
                        "properties": {
                            "condition": {"type": "string"},
                            "entities": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    },
                    "then": {
                        "type": "object",
                        "required": ["action", "parameters"],
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["transform", "move", "validate"]
                            },
                            "parameters": {
                                "type": "object",
                                "additionalProperties": True
                            }
                        }
                    }
                }
            }
        },
        "victory_conditions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type", "condition"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["state", "position", "collection"]
                    },
                    "condition": {"type": "string"}
                }
            }
        },
        "failure_conditions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type", "condition"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["state", "position", "collection"]
                    },
                    "condition": {"type": "string"}
                }
            }
        }
    }
}

@dataclass
class EnvironmentDefinition:
    """Container for parsed environment definition."""
    metadata: Dict[str, str]
    initial_state: Dict[str, Any]
    rules: list
    victory_conditions: list
    failure_conditions: list

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnvironmentDefinition':
        """Create EnvironmentDefinition from dictionary."""
        return cls(
            metadata=data["metadata"],
            initial_state=data["initial_state"],
            rules=data.get("rules", []),
            victory_conditions=data.get("victory_conditions", []),
            failure_conditions=data.get("failure_conditions", [])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "metadata": self.metadata,
            "initial_state": self.initial_state,
            "rules": self.rules,
            "victory_conditions": self.victory_conditions,
            "failure_conditions": self.failure_conditions
        }
