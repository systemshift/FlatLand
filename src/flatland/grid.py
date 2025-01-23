import numpy as np
from typing import Tuple

class Grid:
    """A 2D grid system that manages the game world's state."""
    
    def __init__(self, width: int, height: int):
        """Initialize a new grid with given dimensions.
        
        Args:
            width: The width of the grid
            height: The height of the grid
        """
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=np.int8)
        
    def in_bounds(self, x: int, y: int) -> bool:
        """Check if the given coordinates are within the grid bounds.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            bool: True if coordinates are within bounds, False otherwise
        """
        return 0 <= x < self.width and 0 <= y < self.height
        
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if the given position is walkable (empty).
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            bool: True if position is walkable, False otherwise
        """
        return self.in_bounds(x, y) and self.grid[y, x] == 0
        
    def set_cell(self, x: int, y: int, value: int) -> bool:
        """Set the value of a cell at the given coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            value: Integer value to set (0=empty, 1=wall, 2=player, 3=goal, etc.)
            
        Returns:
            bool: True if cell was set successfully, False if out of bounds
        """
        if self.in_bounds(x, y):
            self.grid[y, x] = value
            return True
        return False
        
    def get_cell(self, x: int, y: int) -> int:
        """Get the value of a cell at the given coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            int: Cell value, or -1 if out of bounds
        """
        if self.in_bounds(x, y):
            return self.grid[y, x]
        return -1
        
    def clear(self):
        """Clear the grid by setting all cells to empty (0)."""
        self.grid.fill(0)
        
    def get_size(self) -> Tuple[int, int]:
        """Get the dimensions of the grid.
        
        Returns:
            Tuple[int, int]: Width and height of the grid
        """
        return self.width, self.height
