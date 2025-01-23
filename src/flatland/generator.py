from typing import Dict, Any, List, Optional
import json
from dataclasses import dataclass

@dataclass
class GeneratorResponse:
    """Container for the LLM generator response."""
    code: str
    metadata: Dict[str, Any]
    error: Optional[str] = None

class LLMEnvironmentGenerator:
    """Handles generation of environments using LLM APIs."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the generator.
        
        Args:
            api_key: Optional API key for the LLM service
        """
        self.api_key = api_key
        self._default_template = """
        Create a grid-based environment following these constraints:
        {constraints}
        
        Environment request: {prompt}
        
        Return only valid Python code that creates the environment.
        The code should:
        1. Create a World instance
        2. Add walls, items, and other entities
        3. Set the player's starting position
        4. Return the world object
        
        Example format:
        ```python
        def create_environment():
            world = World(10, 10)
            # Add walls
            for x in range(10):
                world.grid.set_cell(x, 0, 1)  # Top wall
            # Add items
            world.add_entity(5, 5, "key")
            # Set player position
            world.player_pos = (1, 1)
            return world
        ```
        """
    
    def generate(self, prompt: str, constraints: List[str]) -> GeneratorResponse:
        """Generate an environment based on the prompt and constraints.
        
        Args:
            prompt: Description of the desired environment
            constraints: List of constraints to apply
            
        Returns:
            GeneratorResponse containing the generated code
        """
        # For now, return a simple test environment
        # In practice, this would call an LLM API
        test_code = """
def create_environment():
    # Create a 10x10 world
    world = World(10, 10)
    
    # Add walls around the edges
    for x in range(10):
        world.grid.set_cell(x, 0, 1)  # Top wall
        world.grid.set_cell(x, 9, 1)  # Bottom wall
    for y in range(10):
        world.grid.set_cell(0, y, 1)  # Left wall
        world.grid.set_cell(9, y, 1)  # Right wall
    
    # Add a key and door
    world.add_entity(3, 3, "key")
    world.add_entity(7, 7, "door")
    
    # Set player starting position
    world.player_pos = (1, 1)
    world.grid.set_cell(1, 1, 2)  # Mark player position
    
    return world
"""
        return GeneratorResponse(
            code=test_code,
            metadata={
                "size": (10, 10),
                "entities": ["key", "door"],
                "constraints_applied": constraints
            }
        )
    
    def set_template(self, template: str):
        """Set a custom prompt template for generation.
        
        Args:
            template: The new template to use
        """
        self._default_template = template
    
    def validate_code(self, code: str) -> Optional[str]:
        """Basic validation of generated code.
        
        Args:
            code: The code to validate
            
        Returns:
            Error message if invalid, None if valid
        """
        try:
            # Basic syntax check
            compile(code, '<string>', 'exec')
            
            # Check for required elements
            required = ['World', 'create_environment', 'return world']
            for req in required:
                if req not in code:
                    return f"Missing required element: {req}"
            
            return None
        except Exception as e:
            return f"Code validation error: {str(e)}"
