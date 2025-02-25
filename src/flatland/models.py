"""
Data models for FlatLand.
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Rule:
    """Represents a single rule in the logic system."""
    name: str
    type: str  # conditional | transformation | constraint
    priority: int
    when: Dict[str, Any]  # condition and entities
    then: Dict[str, Any]  # action and parameters
