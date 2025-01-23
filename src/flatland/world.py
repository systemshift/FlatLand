from typing import Tuple, List, Optional, Dict, Any
from .grid import Grid
from .constraints import ConstraintEngine

class World:
    """Main class that manages the game world state and coordinates systems."""
    
    def __init__(self, width: int, height: int):
        """Initialize a new world with given dimensions.
        
        Args:
            width: The width of the world grid
            height: The height of the world grid
        """
        self.grid = Grid(width, height)
        self.constraint_engine = ConstraintEngine()
        self.player_pos = (0, 0)
        self.inventory: List[str] = []
        self.entities: Dict[Tuple[int, int], Any] = {}
        self.step_count = 0
        
    def move_player(self, dx: int, dy: int) -> Tuple[bool, Optional[str]]:
        """Attempt to move the player by the given delta.
        
        Args:
            dx: Change in x position
            dy: Change in y position
            
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message if failed)
        """
        action = ("move", (dx, dy))
        valid, errors = self.constraint_engine.validate_action(self, action)
        
        if not valid:
            return False, errors[0] if errors else "Invalid move"
            
        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy
        
        if self.grid.is_walkable(new_x, new_y):
            # Update grid
            old_x, old_y = self.player_pos
            self.grid.set_cell(old_x, old_y, 0)  # Clear old position
            self.grid.set_cell(new_x, new_y, 2)  # Set new position
            self.player_pos = (new_x, new_y)
            self.step_count += 1
            return True, None
            
        return False, "Position is not walkable"
        
    def add_entity(self, x: int, y: int, entity_type: str, data: Any = None):
        """Add an entity to the world at the specified position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            entity_type: Type of entity (e.g., "key", "door", "goal")
            data: Optional additional data for the entity
        """
        if self.grid.in_bounds(x, y):
            self.entities[(x, y)] = (entity_type, data)
            
    def pickup_item(self, x: int, y: int) -> Tuple[bool, Optional[str]]:
        """Attempt to pick up an item at the given position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message if failed)
        """
        action = ("pickup", (x, y))
        valid, errors = self.constraint_engine.validate_action(self, action)
        
        if not valid:
            return False, errors[0] if errors else "Cannot pickup item"
            
        if (x, y) in self.entities:
            entity_type, data = self.entities[(x, y)]
            self.inventory.append(entity_type)
            del self.entities[(x, y)]
            return True, None
            
        return False, "No item at this position"
        
    def use_item(self, item: str, x: int, y: int) -> Tuple[bool, Optional[str]]:
        """Attempt to use an item from inventory at the given position.
        
        Args:
            item: The item to use
            x: X coordinate to use item at
            y: Y coordinate to use item at
            
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message if failed)
        """
        if item not in self.inventory:
            return False, f"Don't have item: {item}"
            
        action = ("use", (item, x, y))
        valid, errors = self.constraint_engine.validate_action(self, action)
        
        if not valid:
            return False, errors[0] if errors else "Cannot use item here"
            
        # Handle item usage (e.g., key opening door)
        if (x, y) in self.entities:
            entity_type, data = self.entities[(x, y)]
            if entity_type == "door" and item == "key":
                self.inventory.remove(item)
                del self.entities[(x, y)]
                self.grid.set_cell(x, y, 0)  # Clear the door
                return True, None
                
        return False, "Cannot use item here"
        
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the world.
        
        Returns:
            Dict containing current world state
        """
        return {
            "player_pos": self.player_pos,
            "inventory": self.inventory.copy(),
            "entities": self.entities.copy(),
            "step_count": self.step_count,
            "grid_size": self.grid.get_size()
        }
        
    def reset(self):
        """Reset the world to its initial state."""
        self.grid.clear()
        self.player_pos = (0, 0)
        self.inventory.clear()
        self.entities.clear()
        self.step_count = 0
