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
        can_move = self._check_movement(state, target_x, target_y)
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
    # Core Grid Operations
    def _get_cell(self, state: Dict[str, Any], x: int, y: int) -> int:
        """Get cell value at coordinates."""
        grid = state["grid"]
        if 0 <= x < grid["width"] and 0 <= y < grid["height"]:
            return grid["cells"][y][x]
        return -1  # Out of bounds
    
    def _set_cell(self, state: Dict[str, Any], x: int, y: int, value: int) -> bool:
        """Set cell value at coordinates."""
        grid = state["grid"]
        if 0 <= x < grid["width"] and 0 <= y < grid["height"]:
            grid["cells"][y][x] = value
            return True
        return False
    
    def _get_entity_at(self, state: Dict[str, Any], x: int, y: int) -> Optional[Dict[str, Any]]:
        """Find entity at given position."""
        for entity in state["entities"]:
            if entity["position"] == [x, y]:
                return entity
        return None

    def _get_current_entity(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Get current entity being evaluated."""
        # In the context of rule evaluation, this would be set before
        # evaluating conditions. For now, we'll use a simple implementation.
        return state.get("current_entity", {})

    # Entity Operations
    def _check_type(self, state: Dict[str, Any], type_str: str) -> bool:
        """Check if current entity is of given type."""
        current = self._get_current_entity(state)
        return current.get("type", "") == type_str
    
    def _check_property(self, state: Dict[str, Any], prop: str) -> bool:
        """Check if current entity has property."""
        current = self._get_current_entity(state)
        return prop in current.get("properties", {})
    
    def _has_entity_type(self, state: Dict[str, Any], entity_type: str) -> bool:
        """Check if state contains entity type."""
        return any(e["type"] == entity_type for e in state["entities"])

    # Spatial Operations
    def _check_adjacent(self, state: Dict[str, Any], type_str: str) -> bool:
        """Check if entity is adjacent to type."""
        current = self._get_current_entity(state)
        if not current:
            return False
            
        x, y = current["position"]
        # Check all four directions
        directions = [(0,1), (1,0), (0,-1), (-1,0)]
        for dx, dy in directions:
            entity = self._get_entity_at(state, x+dx, y+dy)
            if entity and entity["type"] == type_str:
                return True
        return False
    
    def _check_distance(self, state: Dict[str, Any], type_str: str, max_dist: int) -> bool:
        """Manhattan distance check to nearest entity of type."""
        current = self._get_current_entity(state)
        if not current:
            return False
            
        x1, y1 = current["position"]
        for other in state["entities"]:
            if other["type"] == type_str:
                x2, y2 = other["position"]
                if abs(x2-x1) + abs(y2-y1) <= max_dist:
                    return True
        return False
    
    def _check_movement(self, state: Dict[str, Any], x: int, y: int) -> bool:
        """Check if position is valid for movement."""
        # Check if position is in bounds
        grid = state["grid"]
        if not (0 <= x < grid["width"] and 0 <= y < grid["height"]):
            return False
            
        # Check for walls (cell value 1)
        if grid["cells"][y][x] == 1:
            return False
            
        # Check for boxes (cell value 3)
        if grid["cells"][y][x] == 3:
            # Get movement direction
            current = self._get_current_entity(state)
            if not current:
                return False
                
            dx = x - current["position"][0]
            dy = y - current["position"][1]
            
            # Check if we can push the box
            next_x = x + dx
            next_y = y + dy
            
            # Box can be pushed if next position is empty (0) or goal (4)
            if not (0 <= next_x < grid["width"] and 0 <= next_y < grid["height"]):
                return False
                
            next_cell = grid["cells"][next_y][next_x]
            return next_cell in [0, 4]
            
        # Position is empty (0) or goal (4)
        return grid["cells"][y][x] in [0, 4]
    
    def _count_entities(self, state: Dict[str, Any], type_str: str, radius: int) -> int:
        """Count entities of type within radius."""
        current = self._get_current_entity(state)
        if not current:
            return 0
            
        count = 0
        x1, y1 = current["position"]
        for other in state["entities"]:
            if other["type"] == type_str:
                x2, y2 = other["position"]
                if abs(x2-x1) + abs(y2-y1) <= radius:
                    count += 1
        return count


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
        """Transform entity properties."""
        current = self.current_state.get("current_entity")
        if not current:
            return {}

        changes = {}
        for key, value in params.items():
            if key in current["properties"]:
                current["properties"][key] = value
                changes[key] = value

        return {
            "entity": current["id"],
            "changes": changes
        }
        
    def move_entity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Move entity to new position."""
        current = self.current_state.get("current_entity")
        if not current:
            print("Debug: No current entity found")
            return {}

        old_pos = current["position"]
        new_pos = params["position"]
        print(f"Debug: Moving from {old_pos} to {new_pos}")
        
        # Get grid cell values
        grid = self.current_state["grid"]
        if not (0 <= new_pos[0] < grid["width"] and 0 <= new_pos[1] < grid["height"]):
            return {}  # Invalid position
            
        # Check if we're pushing a box
        if grid["cells"][new_pos[1]][new_pos[0]] == 3:  # Box
            # Calculate box's new position
            dx = new_pos[0] - old_pos[0]
            dy = new_pos[1] - old_pos[1]
            box_new_pos = [new_pos[0] + dx, new_pos[1] + dy]
            
            # Find the box entity
            box_entity = next(
                (e for e in self.current_state["entities"] 
                 if e["position"] == new_pos),
                None
            )
            if box_entity:
                # Check if box's new position is valid
                if grid["cells"][box_new_pos[1]][box_new_pos[0]] in [0, 4]:
                    # Update box position in grid
                    grid["cells"][new_pos[1]][new_pos[0]] = 0  # Clear box's old position
                    grid["cells"][box_new_pos[1]][box_new_pos[0]] = 3  # Set box's new position
                    # Update box entity position
                    box_entity["position"] = box_new_pos
                else:
                    return {}  # Invalid move
        
        # Get entity type value and handle goal cells
        entity_type_value = grid["cells"][old_pos[1]][old_pos[0]]
        old_cell_was_goal = False
        
        # Check if we're moving from a goal cell
        if grid["cells"][old_pos[1]][old_pos[0]] == 2 and any(
            e["position"] == old_pos and e["type"] == "player"
            for e in self.current_state["entities"]
        ):
            old_cell_was_goal = True
            
        # Update grid cells
        grid["cells"][old_pos[1]][old_pos[0]] = 4 if old_cell_was_goal else 0  # Restore goal or clear
        
        # Preserve goal cell if moving onto one
        if grid["cells"][new_pos[1]][new_pos[0]] == 4:
            entity_type_value = 2  # Player on goal
            
        grid["cells"][new_pos[1]][new_pos[0]] = entity_type_value  # Set new position
        
        # Update player entity position
        current["position"] = new_pos
        
        return {
            "entity": current["id"],
            "from": old_pos,
            "to": new_pos
        }
        
    def validate_state(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate state according to parameters."""
        condition = params.get("condition")
        if not condition:
            return {}
            
        # For now, just check if the condition key exists
        # In a full implementation, we would evaluate the condition
        return {
            "valid": True,
            "condition": condition
        }


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
