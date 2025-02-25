"""
Main logic engine for FlatLand environments.
"""

from typing import Dict, List, Any, Optional, Set, Tuple
import json

from .models import Rule
from .validator import SchemaValidator, RuleConflictDetector, DependencyResolver, ValidationError
from .state_manager import StateManager
from .built_in_functions import BuiltInFunctions

class LogicEngine:
    """Main engine that evaluates rules and manages state transitions."""
    
    def __init__(self):
        self.rules: List[Rule] = []
        self.state_manager = StateManager(max_history=1000)
        self.schema_validator = SchemaValidator()
        
    def load_environment(self, json_data: Dict[str, Any]):
        """Load an environment definition from JSON."""
        # Validate environment definition
        is_valid, errors = self.schema_validator.validate_environment(json_data)
        if not is_valid:
            raise ValidationError("Invalid environment definition", errors)
            
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
            is_valid, errors = self.schema_validator.validate_rule(rule)
            if is_valid:
                self.rules.append(rule)
            else:
                raise ValidationError(f"Invalid rule: {rule.name}", errors)
        
        # Sort rules by priority
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        
        # Check for rule conflicts
        conflicts = RuleConflictDetector.detect_conflicts(self.rules)
        if conflicts:
            conflict_msgs = [f"Conflict between {r1.name} and {r2.name}: {reason}" 
                            for r1, r2, reason in conflicts]
            print("Warning: Rule conflicts detected:")
            for msg in conflict_msgs:
                print(f"  - {msg}")
        
        # Build dependency graph
        self.dependency_graph = DependencyResolver.build_dependency_graph(self.rules)
        
        # Check for dependency cycles
        cycles = DependencyResolver.detect_cycles(self.dependency_graph)
        if cycles:
            cycle_msgs = [" -> ".join(cycle) for cycle in cycles]
            print("Warning: Rule dependency cycles detected:")
            for msg in cycle_msgs:
                print(f"  - {msg}")
        
        # Load victory and failure conditions
        self.victory_conditions = json_data.get("victory_conditions", [])
        self.failure_conditions = json_data.get("failure_conditions", [])
        
    def process_input(self, command: str) -> Dict[str, Any]:
        """Process player input command and execute a simulation step.
        
        Args:
            command: String command (e.g., "up", "down", "left", "right")
            
        Returns:
            Dict containing the new state, changes, and victory/failure status
        """
        # Convert command to target position
        state = self.state_manager.get_current_state()
        current_entity = next(
            (e for e in state["entities"] if e["type"] == "player"),
            None
        )
        
        if not current_entity:
            return {"error": "No player entity found"}
            
        x, y = current_entity["position"]
        
        # Calculate target position based on command
        if command == "up":
            target_x, target_y = x, y - 1
        elif command == "down":
            target_x, target_y = x, y + 1
        elif command == "left":
            target_x, target_y = x - 1, y
        elif command == "right":
            target_x, target_y = x + 1, y
        else:
            return {"error": f"Unknown command: {command}"}
            
        # Debug movement check
        print(f"\nDebug: Checking movement to ({target_x}, {target_y})")
        print(f"Cell value at target: {state['grid']['cells'][target_y][target_x]}")
        
        # Check if target position is valid
        can_move = BuiltInFunctions.check_movement(state, target_x, target_y)
        if not can_move:
            return {"error": "Cannot move there"}
            
        # Set current entity in the state manager's state
        self.state_manager.current_state["current_entity"] = current_entity
        
        # Create a move action
        action = {
            "action": "move",
            "parameters": {
                "position": [target_x, target_y]
            }
        }
        
        # Apply the move directly
        result = self._apply_action(action)
        if result:
            changes = [{
                "rule": "player_movement",
                "effect": result
            }]
            self.state_manager.record_step(changes)
            
            return {
                "state": self.state_manager.get_current_state(),
                "changes": changes,
                "victory": self.check_victory_conditions(),
                "failure": self.check_failure_conditions()
            }
            
        return {"error": "Move failed"}
        
    def step(self) -> Dict[str, Any]:
        """Execute one step of the simulation.
        
        Returns:
            Dict containing the new state, changes, and victory/failure status
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
        
        # Check victory/failure conditions
        victory = self.check_victory_conditions()
        failure = self.check_failure_conditions()
        
        return {
            "state": self.state_manager.get_current_state(),
            "changes": changes,
            "victory": victory,
            "failure": failure
        }

    def check_victory_conditions(self) -> bool:
        """Check if any victory conditions are met."""
        if not hasattr(self, 'victory_conditions'):
            return False
            
        state = self.state_manager.get_current_state()
        for condition in self.victory_conditions:
            # Set the state context for condition evaluation
            state["current_entity"] = None  # Reset for global conditions
            
            if not self._evaluate_condition({"condition": condition["condition"]}):
                return False
        return True
        
    def check_failure_conditions(self) -> bool:
        """Check if any failure conditions are met."""
        if not hasattr(self, 'failure_conditions'):
            return False
            
        state = self.state_manager.get_current_state()
        for condition in self.failure_conditions:
            # Set the state context for condition evaluation
            state["current_entity"] = None  # Reset for global conditions
            
            if self._evaluate_condition({"condition": condition["condition"]}):
                return True
        return False
        
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
                if not BuiltInFunctions.has_entity_type(state, entity_type):
                    return False
        
        # Evaluate condition using built-in functions
        try:
            return self._evaluate_condition_string(condition_str, state)
        except Exception as e:
            print(f"Error evaluating condition: {e}")
            return False
            
    def _evaluate_condition_string(self, condition: str, state: Dict[str, Any]) -> bool:
        """Evaluate a condition string with built-in functions."""
        # Create context with built-in functions
        context = BuiltInFunctions.create_function_context(state)
        
        # Evaluate condition in context
        try:
            return eval(condition, {"__builtins__": {}}, context)
        except Exception as e:
            print(f"Error evaluating condition string: {e}")
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
