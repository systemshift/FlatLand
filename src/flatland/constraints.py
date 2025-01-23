from typing import Callable, List, Tuple, Any, Optional
from dataclasses import dataclass

@dataclass
class Constraint:
    """A single constraint that enforces a rule in the world."""
    
    name: str
    rule: Callable[..., bool]
    error_message: str
    
    def validate(self, world: Any, action: Any) -> Tuple[bool, Optional[str]]:
        """Validate an action against this constraint.
        
        Args:
            world: The world state to validate against
            action: The action to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message if invalid)
        """
        try:
            is_valid = self.rule(world, action)
            return is_valid, None if is_valid else self.error_message
        except Exception as e:
            return False, f"Constraint '{self.name}' error: {str(e)}"

class ConstraintEngine:
    """Manages and validates multiple constraints."""
    
    def __init__(self):
        """Initialize an empty constraint engine."""
        self.constraints: List[Constraint] = []
        
    def add_constraint(self, name: str, rule: Callable[..., bool], error_message: str):
        """Add a new constraint to the engine.
        
        Args:
            name: Name of the constraint
            rule: Function that takes (world, action) and returns bool
            error_message: Message to show when constraint is violated
        """
        constraint = Constraint(name, rule, error_message)
        self.constraints.append(constraint)
        
    def validate_action(self, world: Any, action: Any) -> Tuple[bool, List[str]]:
        """Validate an action against all constraints.
        
        Args:
            world: The world state to validate against
            action: The action to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list of error messages if invalid)
        """
        errors = []
        for constraint in self.constraints:
            is_valid, error = constraint.validate(world, action)
            if not is_valid and error:
                errors.append(error)
                
        return len(errors) == 0, errors
    
    def clear(self):
        """Remove all constraints."""
        self.constraints.clear()

# Common constraint rules
def cardinal_movement(world: Any, action: Tuple[str, Tuple[int, int]]) -> bool:
    """Ensure movement is only in cardinal directions (no diagonals)."""
    if action[0] != "move":
        return True
    dx, dy = action[1]
    return (abs(dx) + abs(dy) == 1)

def inventory_limit(max_items: int):
    """Create a constraint for maximum inventory size."""
    def check_inventory(world: Any, action: Any) -> bool:
        if action[0] != "pickup":
            return True
        return len(world.inventory) < max_items
    return check_inventory

def collision_check(world: Any, action: Tuple[str, Tuple[int, int]]) -> bool:
    """Ensure movement doesn't collide with walls."""
    if action[0] != "move":
        return True
    dx, dy = action[1]
    new_x = world.player_pos[0] + dx
    new_y = world.player_pos[1] + dy
    return world.grid.is_walkable(new_x, new_y)
