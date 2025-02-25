"""
State management module for FlatLand environments.
"""

from typing import Dict, List, Any, Optional, Tuple
import json
import copy


class StateManager:
    """Manages the simulation state and history with enhanced capabilities."""
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize the state manager.
        
        Args:
            max_history: Maximum number of states to keep in history
        """
        self.current_state: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
        self.future: List[Dict[str, Any]] = []  # For redo functionality
        self.max_history = max_history
        
    def set_initial_state(self, state: Dict[str, Any]):
        """
        Set the initial simulation state.
        
        Args:
            state: Initial state dictionary
        """
        self.current_state = copy.deepcopy(state)
        self.history = [copy.deepcopy(state)]
        self.future = []
        
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current simulation state.
        
        Returns:
            Deep copy of the current state
        """
        return copy.deepcopy(self.current_state)
    
    def record_step(self, changes: List[Dict[str, Any]]):
        """
        Record a new state after applying changes.
        
        Args:
            changes: List of changes applied in this step
        """
        # Clear future states when a new step is recorded
        self.future = []
        
        # Trim history if it exceeds max_history
        if len(self.history) >= self.max_history:
            self.history.pop(0)
            
        # Add current state to history before updating
        self.history.append(copy.deepcopy(self.current_state))
        
        # Store changes in the current state for reference
        if "changes_history" not in self.current_state:
            self.current_state["changes_history"] = []
            
        self.current_state["changes_history"].append(changes)
    
    def can_undo(self) -> bool:
        """
        Check if undo is possible.
        
        Returns:
            True if there are states in history to undo to
        """
        return len(self.history) > 0
    
    def can_redo(self) -> bool:
        """
        Check if redo is possible.
        
        Returns:
            True if there are states in future to redo to
        """
        return len(self.future) > 0
    
    def undo(self) -> Optional[Dict[str, Any]]:
        """
        Undo the last step.
        
        Returns:
            The new current state after undo, or None if undo is not possible
        """
        if not self.can_undo():
            return None
            
        # Move current state to future
        self.future.append(copy.deepcopy(self.current_state))
        
        # Restore previous state
        self.current_state = self.history.pop()
        
        return self.get_current_state()
    
    def redo(self) -> Optional[Dict[str, Any]]:
        """
        Redo the last undone step.
        
        Returns:
            The new current state after redo, or None if redo is not possible
        """
        if not self.can_redo():
            return None
            
        # Move current state to history
        self.history.append(copy.deepcopy(self.current_state))
        
        # Restore future state
        self.current_state = self.future.pop()
        
        return self.get_current_state()
    
    def compute_state_diff(self, old_state: Dict[str, Any], new_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute the difference between two states.
        
        Args:
            old_state: Previous state
            new_state: New state
            
        Returns:
            Dictionary describing the differences
        """
        diff = {
            "entities": [],
            "grid": {"cells": []}
        }
        
        # Check entity changes
        old_entities = {e["id"]: e for e in old_state.get("entities", [])}
        new_entities = {e["id"]: e for e in new_state.get("entities", [])}
        
        # Added entities
        for eid, entity in new_entities.items():
            if eid not in old_entities:
                diff["entities"].append({"action": "add", "entity": entity})
        
        # Modified entities
        for eid, entity in new_entities.items():
            if eid in old_entities and entity != old_entities[eid]:
                diff["entities"].append({
                    "action": "modify",
                    "id": eid,
                    "changes": self._compute_entity_diff(old_entities[eid], entity)
                })
        
        # Removed entities
        for eid in old_entities:
            if eid not in new_entities:
                diff["entities"].append({"action": "remove", "id": eid})
        
        # Grid changes
        old_grid = old_state.get("grid", {})
        new_grid = new_state.get("grid", {})
        
        if old_grid and new_grid:
            old_cells = old_grid.get("cells", [])
            new_cells = new_grid.get("cells", [])
            
            for y in range(min(len(old_cells), len(new_cells))):
                for x in range(min(len(old_cells[y]), len(new_cells[y]))):
                    if old_cells[y][x] != new_cells[y][x]:
                        diff["grid"]["cells"].append({
                            "position": [x, y],
                            "old": old_cells[y][x],
                            "new": new_cells[y][x]
                        })
        
        return diff
    
    def _compute_entity_diff(self, old_entity: Dict[str, Any], new_entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute the difference between two entities.
        
        Args:
            old_entity: Previous entity state
            new_entity: New entity state
            
        Returns:
            Dictionary describing the differences
        """
        diff = {}
        
        # Check position changes
        if old_entity.get("position") != new_entity.get("position"):
            diff["position"] = {
                "old": old_entity.get("position"),
                "new": new_entity.get("position")
            }
        
        # Check type changes
        if old_entity.get("type") != new_entity.get("type"):
            diff["type"] = {
                "old": old_entity.get("type"),
                "new": new_entity.get("type")
            }
        
        # Check property changes
        old_props = old_entity.get("properties", {})
        new_props = new_entity.get("properties", {})
        
        prop_diff = {}
        for key in set(old_props.keys()) | set(new_props.keys()):
            if key in old_props and key in new_props:
                if old_props[key] != new_props[key]:
                    prop_diff[key] = {
                        "old": old_props[key],
                        "new": new_props[key]
                    }
            elif key in new_props:
                prop_diff[key] = {
                    "old": None,
                    "new": new_props[key]
                }
            else:
                prop_diff[key] = {
                    "old": old_props[key],
                    "new": None
                }
        
        if prop_diff:
            diff["properties"] = prop_diff
        
        return diff
    
    def apply_diff(self, state: Dict[str, Any], diff: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a diff to a state to get a new state.
        
        Args:
            state: Base state
            diff: Diff to apply
            
        Returns:
            New state after applying diff
        """
        new_state = copy.deepcopy(state)
        
        # Apply entity changes
        for entity_diff in diff.get("entities", []):
            action = entity_diff.get("action")
            
            if action == "add":
                new_state["entities"].append(entity_diff["entity"])
            
            elif action == "remove":
                new_state["entities"] = [
                    e for e in new_state["entities"] 
                    if e["id"] != entity_diff["id"]
                ]
            
            elif action == "modify":
                entity_id = entity_diff["id"]
                changes = entity_diff["changes"]
                
                for i, entity in enumerate(new_state["entities"]):
                    if entity["id"] == entity_id:
                        # Apply position changes
                        if "position" in changes:
                            entity["position"] = changes["position"]["new"]
                        
                        # Apply type changes
                        if "type" in changes:
                            entity["type"] = changes["type"]["new"]
                        
                        # Apply property changes
                        if "properties" in changes:
                            for prop, value in changes["properties"].items():
                                if value["new"] is None:
                                    if prop in entity["properties"]:
                                        del entity["properties"][prop]
                                else:
                                    if "properties" not in entity:
                                        entity["properties"] = {}
                                    entity["properties"][prop] = value["new"]
        
        # Apply grid changes
        for cell_diff in diff.get("grid", {}).get("cells", []):
            x, y = cell_diff["position"]
            new_state["grid"]["cells"][y][x] = cell_diff["new"]
        
        return new_state
    
    def serialize_state(self, state: Dict[str, Any]) -> str:
        """
        Serialize a state to JSON.
        
        Args:
            state: State to serialize
            
        Returns:
            JSON string representation
        """
        return json.dumps(state, indent=2)
    
    def deserialize_state(self, json_str: str) -> Dict[str, Any]:
        """
        Deserialize a state from JSON.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            Deserialized state
        """
        return json.loads(json_str)
    
    def transform_entity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform entity properties.
        
        Args:
            params: Transformation parameters
            
        Returns:
            Dictionary describing the transformation
        """
        current = self.current_state.get("current_entity")
        if not current:
            return {}

        changes = {}
        for key, value in params.items():
            if key in current.get("properties", {}):
                current["properties"][key] = value
                changes[key] = value
            elif key == "type":
                # Allow changing entity type
                old_type = current.get("type")
                current["type"] = value
                changes["type"] = {"old": old_type, "new": value}

        return {
            "entity": current["id"],
            "changes": changes
        }
    
    def move_entity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Move entity to new position.
        
        Args:
            params: Movement parameters
            
        Returns:
            Dictionary describing the movement
        """
        current = self.current_state.get("current_entity")
        if not current:
            return {}

        old_pos = current["position"]
        new_pos = params["position"]
        
        # Get grid cell values
        grid = self.current_state.get("grid", {})
        if not grid:
            return {}
            
        if not (0 <= new_pos[0] < grid.get("width", 0) and 0 <= new_pos[1] < grid.get("height", 0)):
            return {}  # Invalid position
            
        # Check if we're pushing a box (cell value 3)
        if grid["cells"][new_pos[1]][new_pos[0]] == 3:
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
                if (0 <= box_new_pos[0] < grid["width"] and 
                    0 <= box_new_pos[1] < grid["height"] and
                    grid["cells"][box_new_pos[1]][box_new_pos[0]] in [0, 4]):
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
        
        # Update entity position in current_entity
        current["position"] = new_pos
        
        # Also update the entity in the entities list
        for entity in self.current_state["entities"]:
            if entity["id"] == current["id"]:
                entity["position"] = new_pos
                break
        
        return {
            "entity": current["id"],
            "from": old_pos,
            "to": new_pos
        }
    
    def validate_state(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate state according to parameters.
        
        Args:
            params: Validation parameters
            
        Returns:
            Dictionary describing the validation result
        """
        condition = params.get("condition")
        if not condition:
            return {"valid": False, "reason": "No condition specified"}
            
        # In a full implementation, we would evaluate the condition
        # For now, we'll just return a placeholder result
        return {
            "valid": True,
            "condition": condition
        }
