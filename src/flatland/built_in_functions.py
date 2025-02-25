"""
Built-in functions for FlatLand rule evaluation.
"""

from typing import Dict, List, Any, Optional, Tuple


class BuiltInFunctions:
    """Collection of built-in functions for rule evaluation."""
    
    @staticmethod
    def get_cell(state: Dict[str, Any], x: int, y: int) -> int:
        """
        Get cell value at coordinates.
        
        Args:
            state: Current state
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Cell value, or -1 if out of bounds
        """
        grid = state.get("grid", {})
        if 0 <= x < grid.get("width", 0) and 0 <= y < grid.get("height", 0):
            return grid["cells"][y][x]
        return -1  # Out of bounds
    
    @staticmethod
    def set_cell(state: Dict[str, Any], x: int, y: int, value: int) -> bool:
        """
        Set cell value at coordinates.
        
        Args:
            state: Current state
            x: X coordinate
            y: Y coordinate
            value: New cell value
            
        Returns:
            True if successful, False if out of bounds
        """
        grid = state.get("grid", {})
        if 0 <= x < grid.get("width", 0) and 0 <= y < grid.get("height", 0):
            grid["cells"][y][x] = value
            return True
        return False
    
    @staticmethod
    def get_entity_at(state: Dict[str, Any], x: int, y: int) -> Optional[Dict[str, Any]]:
        """
        Find entity at given position.
        
        Args:
            state: Current state
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Entity at position, or None if not found
        """
        for entity in state.get("entities", []):
            if entity.get("position") == [x, y]:
                return entity
        return None
    
    @staticmethod
    def get_current_entity(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get current entity being evaluated.
        
        Args:
            state: Current state
            
        Returns:
            Current entity, or empty dict if not set
        """
        return state.get("current_entity", {})
    
    @staticmethod
    def check_type(state: Dict[str, Any], type_str: str) -> bool:
        """
        Check if current entity is of given type.
        
        Args:
            state: Current state
            type_str: Type to check
            
        Returns:
            True if current entity is of given type
        """
        current = BuiltInFunctions.get_current_entity(state)
        return current.get("type", "") == type_str
    
    @staticmethod
    def check_property(state: Dict[str, Any], prop: str) -> bool:
        """
        Check if current entity has property.
        
        Args:
            state: Current state
            prop: Property to check
            
        Returns:
            True if current entity has property
        """
        current = BuiltInFunctions.get_current_entity(state)
        return prop in current.get("properties", {})
    
    @staticmethod
    def has_entity_type(state: Dict[str, Any], entity_type: str) -> bool:
        """
        Check if state contains entity type.
        
        Args:
            state: Current state
            entity_type: Entity type to check
            
        Returns:
            True if state contains entity of given type
        """
        return any(e.get("type") == entity_type for e in state.get("entities", []))
    
    @staticmethod
    def check_adjacent(state: Dict[str, Any], type_str: str) -> bool:
        """
        Check if entity is adjacent to type.
        
        Args:
            state: Current state
            type_str: Entity type to check for
            
        Returns:
            True if current entity is adjacent to entity of given type
        """
        current = BuiltInFunctions.get_current_entity(state)
        if not current or "position" not in current:
            return False
            
        x, y = current["position"]
        # Check all four directions
        directions = [(0,1), (1,0), (0,-1), (-1,0)]
        for dx, dy in directions:
            entity = BuiltInFunctions.get_entity_at(state, x+dx, y+dy)
            if entity and entity.get("type") == type_str:
                return True
        return False
    
    @staticmethod
    def check_distance(state: Dict[str, Any], type_str: str, max_dist: int) -> bool:
        """
        Manhattan distance check to nearest entity of type.
        
        Args:
            state: Current state
            type_str: Entity type to check for
            max_dist: Maximum distance
            
        Returns:
            True if entity of given type is within distance
        """
        current = BuiltInFunctions.get_current_entity(state)
        if not current or "position" not in current:
            return False
            
        x1, y1 = current["position"]
        for other in state.get("entities", []):
            if other.get("type") == type_str and "position" in other:
                x2, y2 = other["position"]
                if abs(x2-x1) + abs(y2-y1) <= max_dist:
                    return True
        return False
    
    @staticmethod
    def check_movement(state: Dict[str, Any], x: int, y: int) -> bool:
        """
        Check if position is valid for movement.
        
        Args:
            state: Current state
            x: Target X coordinate
            y: Target Y coordinate
            
        Returns:
            True if position is valid for movement
        """
        # Check if position is in bounds
        grid = state.get("grid", {})
        if not (0 <= x < grid.get("width", 0) and 0 <= y < grid.get("height", 0)):
            return False
            
        # Check for walls (cell value 1)
        if grid["cells"][y][x] == 1:
            return False
            
        # Check for boxes (cell value 3)
        if grid["cells"][y][x] == 3:
            # Get movement direction
            current = BuiltInFunctions.get_current_entity(state)
            if not current or "position" not in current:
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
    
    @staticmethod
    def count_entities(state: Dict[str, Any], type_str: str, radius: int) -> int:
        """
        Count entities of type within radius.
        
        Args:
            state: Current state
            type_str: Entity type to count
            radius: Maximum distance
            
        Returns:
            Number of entities of given type within radius
        """
        current = BuiltInFunctions.get_current_entity(state)
        if not current or "position" not in current:
            return 0
            
        count = 0
        x1, y1 = current["position"]
        for other in state.get("entities", []):
            if other.get("type") == type_str and "position" in other:
                x2, y2 = other["position"]
                if abs(x2-x1) + abs(y2-y1) <= radius:
                    count += 1
        return count
    
    @staticmethod
    def has_support_below(state: Dict[str, Any]) -> bool:
        """
        Check if entity has support below it.
        
        Args:
            state: Current state
            
        Returns:
            True if entity has support below
        """
        current = BuiltInFunctions.get_current_entity(state)
        if not current or "position" not in current:
            return False
            
        x, y = current["position"]
        below_y = y + 1
        
        # Check if below is within bounds
        grid = state.get("grid", {})
        if not (0 <= below_y < grid.get("height", 0)):
            return False
            
        # Check if cell below is solid (wall or other solid entity)
        cell_below = grid["cells"][below_y][x]
        return cell_below in [1, 3]  # Wall or box
    
    @staticmethod
    def can_see(state: Dict[str, Any], type_str: str, max_dist: int) -> bool:
        """
        Check if entity has line of sight to another entity.
        
        Args:
            state: Current state
            type_str: Entity type to check for
            max_dist: Maximum distance
            
        Returns:
            True if entity has line of sight to entity of given type
        """
        current = BuiltInFunctions.get_current_entity(state)
        if not current or "position" not in current:
            return False
            
        x1, y1 = current["position"]
        grid = state.get("grid", {})
        
        for other in state.get("entities", []):
            if other.get("type") == type_str and "position" in other:
                x2, y2 = other["position"]
                
                # Check distance
                dist = abs(x2 - x1) + abs(y2 - y1)
                if dist > max_dist:
                    continue
                
                # Check line of sight (simplified)
                if x1 == x2:  # Vertical line
                    start_y, end_y = min(y1, y2), max(y1, y2)
                    has_los = True
                    for y in range(start_y + 1, end_y):
                        if grid["cells"][y][x1] == 1:  # Wall
                            has_los = False
                            break
                    if has_los:
                        return True
                        
                elif y1 == y2:  # Horizontal line
                    start_x, end_x = min(x1, x2), max(x1, x2)
                    has_los = True
                    for x in range(start_x + 1, end_x):
                        if grid["cells"][y1][x] == 1:  # Wall
                            has_los = False
                            break
                    if has_los:
                        return True
        
        return False
    
    @staticmethod
    def count_entities_on_goals(state: Dict[str, Any], type_str: str) -> int:
        """
        Count entities of type on goal cells.
        
        Args:
            state: Current state
            type_str: Entity type to count
            
        Returns:
            Number of entities of given type on goal cells
        """
        count = 0
        grid = state.get("grid", {})
        
        for entity in state.get("entities", []):
            if entity.get("type") == type_str and "position" in entity:
                x, y = entity["position"]
                if grid["cells"][y][x] == 4:  # Goal cell
                    count += 1
        
        return count
    
    @staticmethod
    def create_function_context(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a context with all built-in functions for condition evaluation.
        
        Args:
            state: Current state
            
        Returns:
            Dictionary of function names to function objects
        """
        return {
            "adjacent_to": lambda type_str: BuiltInFunctions.check_adjacent(state, type_str),
            "distance_to": lambda type_str, max_dist: BuiltInFunctions.check_distance(state, type_str, max_dist),
            "count_nearby": lambda type_str, radius: BuiltInFunctions.count_entities(state, type_str, radius),
            "has_property": lambda prop: BuiltInFunctions.check_property(state, prop),
            "is_type": lambda type_str: BuiltInFunctions.check_type(state, type_str),
            "can_move_to": lambda x, y: BuiltInFunctions.check_movement(state, x, y),
            "has_support_below": lambda: BuiltInFunctions.has_support_below(state),
            "can_see": lambda type_str, max_dist: BuiltInFunctions.can_see(state, type_str, max_dist),
            "count_entities_on_goals": lambda type_str: BuiltInFunctions.count_entities_on_goals(state, type_str),
            "entity": BuiltInFunctions.get_current_entity(state),
            "state": state
        }
