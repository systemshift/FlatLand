from typing import Dict, Any, Tuple, Optional

class GameEntity:
    """Represents a single entity in the game."""
    def __init__(self, entity_id: str, entity_type: str, appearance: Dict[str, str], 
                 initial_position: Tuple[int, int], properties: Optional[Dict[str, Any]] = None):
        self.id: str = entity_id
        self.type: str = entity_type
        self.appearance: Dict[str, str] = appearance # e.g., {"char": "P", "color": "red"}
        self.x: int = initial_position[0]
        self.y: int = initial_position[1]
        self.properties: Dict[str, Any] = properties if properties is not None else {}

    def __repr__(self) -> str:
        return f"GameEntity(id='{self.id}', type='{self.type}', pos=({self.x},{self.y}))"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the entity to a dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "appearance": self.appearance,
            "position": {"x": self.x, "y": self.y},
            "properties": self.properties
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameEntity':
        """Creates an entity from a dictionary (e.g., from SGD)."""
        return cls(
            entity_id=data['id'],
            entity_type=data['type'],
            appearance=data['appearance'],
            initial_position=(data['initial_position']['x'], data['initial_position']['y']),
            properties=data.get('properties')
        )

if __name__ == '__main__':
    # Example Usage
    player_data = {
        "id": "player1",
        "type": "player",
        "appearance": {"char": "P", "color": "blue"},
        "initial_position": {"x": 1, "y": 1},
        "properties": {"health": 100, "is_movable": True}
    }
    player = GameEntity.from_dict(player_data)
    print(player)
    print(player.to_dict())

    wall = GameEntity("wall1", "wall", {"char": "#"}, (0,0), {"is_solid": True})
    print(wall)
