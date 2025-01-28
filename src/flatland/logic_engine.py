from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
import json

@dataclass
class Rule:
    """Represents a single rule in the logic system."""
    name: str
    type: str  # conditional | transformation | constraint
    priority: int
    when: Dict[str, Any]  # condition and entities
    then: Dict[str, Any]  # action and parameters

class LogicEngine:
    """Main engine that evaluates rules and manages state transitions."""
    
    def __init__(self):
        self.rules: List[Rule] = []
        self.state_manager = StateManager()
        self.rule_validator = RuleValidator()
        
    def load_environment(self, json_data: Dict[str, Any]):
        """Load an environment definition from JSON."""
        # Validate environment definition
        if not self.rule_validator.validate_environment(json_data):
            raise ValueError("Invalid environment definition")
            
        # Load initial state
        self.state_manager.set_initial_state(json_data["initial_state"])
        
        # Parse and validate rules
        self.rules = []
        for rule_def in json_data.get("rules", []):
            rule = Rule(
                name=rule_def["name"],
                type=rule_def["type"],
                priority=rule_def.get("priority", 0),
                when=rule_def["when"],
                then=rule_def["then"]
            )
            if self.rule_validator.validate_rule(rule):
                self.rules.append(rule)
        
        # Sort rules by priority
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        
    def step(self) -> Dict[str, Any]:
        """Execute one step of the simulation.
        
        Returns:
            Dict containing the new state and any events/changes
        """
        changes = []
        
        # Evaluate rules in priority order
        for rule in self.rules:
            if self._evaluate_condition(rule.when):
                result = self._apply_action(rule.then)
                if result:
                    changes.append({
                        "rule": rule.name,
                        "effect": result
                    })
                    
        # Update state history
        self.state_manager.record_step(changes)
        
        return {
            "state": self.state_manager.get_current_state(),
            "changes": changes
        }
        
    def _evaluate_condition(self, condition: Dict[str, Any]) -> bool:
        """Evaluate a rule's condition against current state."""
        # Get current state
        state = self.state_manager.get_current_state()
        
        # Extract condition components
        condition_str = condition["condition"]
        required_entities = condition.get("entities", [])
        
        # Check entity requirements
        if "any" not in required_entities:
            for entity_type in required_entities:
                if not self._has_entity_type(state, entity_type):
                    return False
        
        # Evaluate condition using built-in functions
        try:
            return self._evaluate_condition_string(condition_str, state)
        except Exception:
            return False
            
    def _evaluate_condition_string(self, condition: str, state: Dict[str, Any]) -> bool:
        """Evaluate a condition string with built-in functions."""
        # Create context with built-in functions
        context = {
            "adjacent_to": lambda type: self._check_adjacent(state, type),
            "distance_to": lambda type, max_dist: self._check_distance(state, type, max_dist),
            "count_nearby": lambda type, radius: self._count_entities(state, type, radius),
            "has_property": lambda prop: self._check_property(state, prop),
            "is_type": lambda type: self._check_type(state, type),
            "can_move_to": lambda x, y: self._check_movement(state, x, y),
            "entity": self._get_current_entity(state),
            "state": state
        }
        
        # Evaluate condition in context
        try:
            return eval(condition, {"__builtins__": {}}, context)
        except Exception:
            return False
            
    def _apply_action(self, action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Apply a rule's action to modify state."""
        action_type = action["action"]
        params = action["parameters"]
        
        if action_type == "transform":
            return self.state_manager.transform_entity(params)
        elif action_type == "move":
            return self.state_manager.move_entity(params)
        elif action_type == "validate":
            return self.state_manager.validate_state(params)
        
        return None

    # Built-in function implementations
    def _check_adjacent(self, state: Dict[str, Any], type: str) -> bool:
        """Check if entity is adjacent to type."""
        pass  # Implementation details
        
    def _check_distance(self, state: Dict[str, Any], type: str, max_dist: int) -> bool:
        """Check if entity is within distance of type."""
        pass  # Implementation details
        
    def _count_entities(self, state: Dict[str, Any], type: str, radius: int) -> int:
        """Count entities of type within radius."""
        pass  # Implementation details
        
    def _check_property(self, state: Dict[str, Any], prop: str) -> bool:
        """Check if entity has property."""
        pass  # Implementation details
        
    def _check_type(self, state: Dict[str, Any], type: str) -> bool:
        """Check if entity is of type."""
        pass  # Implementation details
        
    def _check_movement(self, state: Dict[str, Any], x: int, y: int) -> bool:
        """Check if position is valid for movement."""
        pass  # Implementation details
        
    def _get_current_entity(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Get current entity being evaluated."""
        pass  # Implementation details
        
    def _has_entity_type(self, state: Dict[str, Any], entity_type: str) -> bool:
        """Check if state contains entity of given type."""
        pass  # Implementation details


class StateManager:
    """Manages the simulation state and history."""
    
    def __init__(self):
        self.current_state: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
        self.max_history = 1000
        
    def set_initial_state(self, state: Dict[str, Any]):
        """Set the initial simulation state."""
        self.current_state = state.copy()
        self.history = [state.copy()]
        
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current simulation state."""
        return self.current_state.copy()
        
    def record_step(self, changes: List[Dict[str, Any]]):
        """Record a new state after applying changes."""
        if len(self.history) >= self.max_history:
            self.history.pop(0)
        self.history.append(self.current_state.copy())
        
    def transform_entity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Transform an entity according to parameters."""
        pass  # Implementation details
        
    def move_entity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Move an entity according to parameters."""
        pass  # Implementation details
        
    def validate_state(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate state according to parameters."""
        pass  # Implementation details


class RuleValidator:
    """Validates rules and detects conflicts."""
    
    def __init__(self):
        self.seen_rules: Set[str] = set()
        
    def validate_environment(self, env_def: Dict[str, Any]) -> bool:
        """Validate complete environment definition."""
        required_keys = {"metadata", "initial_state"}
        if not all(key in env_def for key in required_keys):
            return False
            
        # Validate metadata
        if not self._validate_metadata(env_def["metadata"]):
            return False
            
        # Validate initial state
        if not self._validate_initial_state(env_def["initial_state"]):
            return False
            
        # Validate rules if present
        if "rules" in env_def:
            if not isinstance(env_def["rules"], list):
                return False
            for rule in env_def["rules"]:
                if not self._validate_rule_definition(rule):
                    return False
                    
        return True
        
    def validate_rule(self, rule: Rule) -> bool:
        """Validate a single rule and check for conflicts."""
        # Check for duplicate names
        if rule.name in self.seen_rules:
            return False
        self.seen_rules.add(rule.name)
        
        # Validate rule type
        if rule.type not in {"conditional", "transformation", "constraint"}:
            return False
            
        # Validate condition
        if not self._validate_condition(rule.when):
            return False
            
        # Validate action
        if not self._validate_action(rule.then):
            return False
            
        return True
        
    def _validate_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Validate environment metadata."""
        required_keys = {"name", "description"}
        return all(key in metadata for key in required_keys)
        
    def _validate_initial_state(self, state: Dict[str, Any]) -> bool:
        """Validate initial state definition."""
        required_keys = {"grid", "entities"}
        if not all(key in state for key in required_keys):
            return False
            
        # Validate grid
        grid = state["grid"]
        if not isinstance(grid, dict) or "width" not in grid or "height" not in grid:
            return False
            
        # Validate entities
        entities = state["entities"]
        if not isinstance(entities, list):
            return False
            
        return True
        
    def _validate_rule_definition(self, rule: Dict[str, Any]) -> bool:
        """Validate raw rule definition from JSON."""
        required_keys = {"name", "type", "when", "then"}
        return all(key in rule for key in required_keys)
        
    def _validate_condition(self, condition: Dict[str, Any]) -> bool:
        """Validate rule condition."""
        required_keys = {"condition"}
        if not all(key in condition for key in required_keys):
            return False
            
        # Validate condition string
        if not isinstance(condition["condition"], str):
            return False
            
        # Validate entities list if present
        if "entities" in condition and not isinstance(condition["entities"], list):
            return False
            
        return True
        
    def _validate_action(self, action: Dict[str, Any]) -> bool:
        """Validate rule action."""
        required_keys = {"action", "parameters"}
        if not all(key in action for key in required_keys):
            return False
            
        # Validate action type
        if action["action"] not in {"transform", "move", "validate"}:
            return False
            
        # Validate parameters
        if not isinstance(action["parameters"], dict):
            return False
            
        return True
