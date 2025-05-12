from typing import Dict, List, Any, Optional
from .game_elements import GameEntity

class GameState:
    """Manages the current state of the game."""
    def __init__(self, grid_width: int, grid_height: int, default_tile: Optional[str] = "."):
        self.grid_width: int = grid_width
        self.grid_height: int = grid_height
        self.default_tile: Optional[str] = default_tile
        self.entities: Dict[str, GameEntity] = {} # Entity ID to GameEntity object
        self.game_status: str = "initializing" # e.g., "running", "won", "lost", "paused"
        self.message: Optional[str] = None # For conveying messages to the player
        self.score: int = 0 # Example global property

        # For quick spatial lookups, maps (x,y) to a list of entity IDs at that location
        self.entity_grid: Dict[tuple[int, int], List[str]] = {} 

    def add_entity(self, entity: GameEntity):
        """Adds an entity to the game state."""
        if entity.id in self.entities:
            # Handle error or update logic if entity ID already exists
            print(f"Warning: Entity with ID '{entity.id}' already exists. Overwriting.")
        self.entities[entity.id] = entity
        self._update_entity_grid_add(entity)

    def remove_entity(self, entity_id: str) -> Optional[GameEntity]:
        """Removes an entity from the game state."""
        entity = self.entities.pop(entity_id, None)
        if entity:
            self._update_entity_grid_remove(entity)
        return entity

    def move_entity(self, entity_id: str, new_x: int, new_y: int):
        """Moves an entity to a new position."""
        entity = self.get_entity(entity_id)
        if entity:
            self._update_entity_grid_remove(entity)
            entity.x = new_x
            entity.y = new_y
            self._update_entity_grid_add(entity)
        else:
            print(f"Warning: Entity '{entity_id}' not found for moving.")

    def _update_entity_grid_add(self, entity: GameEntity):
        pos = (entity.x, entity.y)
        if pos not in self.entity_grid:
            self.entity_grid[pos] = []
        if entity.id not in self.entity_grid[pos]: # Avoid duplicates if logic error elsewhere
             self.entity_grid[pos].append(entity.id)

    def _update_entity_grid_remove(self, entity: GameEntity):
        old_pos = (entity.x, entity.y)
        if old_pos in self.entity_grid and entity.id in self.entity_grid[old_pos]:
            self.entity_grid[old_pos].remove(entity.id)
            if not self.entity_grid[old_pos]: # Clean up empty list
                del self.entity_grid[old_pos]
    
    def get_entity(self, entity_id: str) -> Optional[GameEntity]:
        """Retrieves an entity by its ID."""
        return self.entities.get(entity_id)

    def get_entities_at_position(self, x: int, y: int) -> List[GameEntity]:
        """Retrieves all entities at a given position."""
        entity_ids = self.entity_grid.get((x,y), [])
        return [self.entities[eid] for eid in entity_ids if eid in self.entities]

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the game state to a dictionary for transmission or display."""
        return {
            "grid_width": self.grid_width,
            "grid_height": self.grid_height,
            "default_tile": self.default_tile,
            "entities": [entity.to_dict() for entity in self.entities.values()],
            "game_status": self.game_status,
            "message": self.message,
            "score": self.score
            # entity_grid is internal and not typically serialized directly for clients
        }

    @classmethod
    def from_sgd(cls, sgd_data: Dict[str, Any]) -> 'GameState':
        """Initializes GameState from a Structured Game Definition."""
        grid_data = sgd_data['grid']
        state = cls(grid_data['width'], grid_data['height'], grid_data.get('default_tile'))
        
        for entity_data in sgd_data.get('entities', []):
            entity = GameEntity.from_dict(entity_data)
            state.add_entity(entity)
        
        state.game_status = "ready" # Initial status after loading
        return state

if __name__ == '__main__':
    # Example Usage
    sgd_example = {
        "grid": {"width": 10, "height": 8, "default_tile": "."},
        "entities": [
            {"id": "p1", "type": "player", "appearance": {"char": "@"}, "initial_position": {"x": 1, "y": 1}},
            {"id": "w1", "type": "wall", "appearance": {"char": "#"}, "initial_position": {"x": 2, "y": 1}}
        ]
    }
    game_state = GameState.from_sgd(sgd_example)
    print(f"Game status: {game_state.game_status}")
    print(f"Entities: {game_state.entities}")
    print(f"Entities at (2,1): {game_state.get_entities_at_position(2,1)}")
    
    game_state.move_entity("p1", 2, 1)
    print(f"Player moved. Entities at (2,1): {game_state.get_entities_at_position(2,1)}")
    
    print("\nSerialized state:")
    print(game_state.to_dict())
