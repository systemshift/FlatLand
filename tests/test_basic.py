import pytest
from flatland import World, ConstraintEngine
from flatland.constraints import cardinal_movement, collision_check, inventory_limit

def test_grid_operations():
    """Test basic grid operations."""
    world = World(5, 5)
    
    # Test setting and getting cells
    assert world.grid.set_cell(0, 0, 1) == True
    assert world.grid.get_cell(0, 0) == 1
    
    # Test bounds checking
    assert world.grid.set_cell(5, 5, 1) == False
    assert world.grid.get_cell(5, 5) == -1
    
    # Test walkable checks
    assert world.grid.is_walkable(1, 1) == True
    assert world.grid.is_walkable(0, 0) == False

def test_player_movement():
    """Test player movement and collision."""
    world = World(5, 5)
    
    # Add movement constraint
    world.constraint_engine.add_constraint(
        "cardinal_movement",
        cardinal_movement,
        "Only cardinal movement allowed"
    )
    
    # Test valid movement
    success, error = world.move_player(1, 0)
    assert success == True
    assert world.player_pos == (1, 0)
    
    # Test diagonal movement (should fail)
    success, error = world.move_player(1, 1)
    assert success == False
    assert "cardinal_movement" in error.lower()
    
    # Test wall collision
    world.grid.set_cell(2, 0, 1)  # Add wall
    success, error = world.move_player(1, 0)
    assert success == False
    assert "not walkable" in error.lower()

def test_inventory_system():
    """Test inventory management."""
    world = World(5, 5)
    
    # Add inventory constraint
    world.constraint_engine.add_constraint(
        "inventory_limit",
        inventory_limit(2),
        "Max 2 items"
    )
    
    # Add items
    world.add_entity(1, 0, "key")
    world.add_entity(2, 0, "key")
    world.add_entity(3, 0, "key")
    
    # Move to first key
    world.move_player(1, 0)
    success, _ = world.pickup_item(1, 0)
    assert success == True
    assert len(world.inventory) == 1
    
    # Move to second key
    world.move_player(1, 0)
    success, _ = world.pickup_item(2, 0)
    assert success == True
    assert len(world.inventory) == 2
    
    # Try to pick up third key (should fail)
    world.move_player(1, 0)
    success, error = world.pickup_item(3, 0)
    assert success == False
    assert len(world.inventory) == 2

def test_key_door_interaction():
    """Test using items with entities."""
    world = World(5, 5)
    
    # Add key and door
    world.add_entity(1, 0, "key")
    world.add_entity(2, 0, "door")
    
    # Pick up key
    world.move_player(1, 0)
    world.pickup_item(1, 0)
    assert "key" in world.inventory
    
    # Use key on door
    success, _ = world.use_item("key", 2, 0)
    assert success == True
    assert "key" not in world.inventory
    assert (2, 0) not in world.entities

def test_world_reset():
    """Test world reset functionality."""
    world = World(5, 5)
    
    # Make some changes
    world.grid.set_cell(1, 1, 1)
    world.add_entity(2, 2, "key")
    world.move_player(1, 0)
    
    # Reset world
    world.reset()
    
    # Verify reset
    assert world.player_pos == (0, 0)
    assert len(world.inventory) == 0
    assert len(world.entities) == 0
    assert world.grid.get_cell(1, 1) == 0

if __name__ == "__main__":
    pytest.main([__file__])
