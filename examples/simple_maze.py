from flatland import World, ConstraintEngine
from flatland.constraints import cardinal_movement, collision_check, inventory_limit

def main():
    # Create a new world (10x10 grid)
    world = World(10, 10)
    
    # Add constraints
    world.constraint_engine.add_constraint(
        "cardinal_movement",
        cardinal_movement,
        "Can only move in cardinal directions (no diagonals)"
    )
    world.constraint_engine.add_constraint(
        "collision",
        collision_check,
        "Cannot walk through walls"
    )
    world.constraint_engine.add_constraint(
        "inventory",
        inventory_limit(2),
        "Cannot carry more than 2 items"
    )
    
    # Create a simple maze with walls
    for x in range(10):
        world.grid.set_cell(x, 0, 1)  # Top wall
        world.grid.set_cell(x, 9, 1)  # Bottom wall
    for y in range(10):
        world.grid.set_cell(0, y, 1)  # Left wall
        world.grid.set_cell(9, y, 1)  # Right wall
    
    # Add some internal walls
    for x in range(5):
        world.grid.set_cell(x, 5, 1)
    for y in range(5, 9):
        world.grid.set_cell(5, y, 1)
    
    # Add items
    world.add_entity(3, 3, "key")
    world.add_entity(7, 7, "door")
    
    # Set player starting position
    world.player_pos = (1, 1)
    world.grid.set_cell(1, 1, 2)
    
    # Game loop
    print("Welcome to FlatLand!")
    print("Use WASD to move, Q to quit")
    print("Find the key and reach the door")
    
    while True:
        # Render current state
        render_world(world)
        print(f"Inventory: {world.inventory}")
        
        # Get input
        action = input("> ").lower()
        if action == 'q':
            break
            
        # Handle movement
        if action in ['w', 'a', 's', 'd']:
            dx, dy = {
                'w': (0, -1),
                's': (0, 1),
                'a': (-1, 0),
                'd': (1, 0)
            }[action]
            
            success, error = world.move_player(dx, dy)
            if not success:
                print(f"Cannot move: {error}")
                continue
        
        # Auto-pickup items
        px, py = world.player_pos
        if (px, py) in world.entities:
            success, error = world.pickup_item(px, py)
            if success:
                print(f"Picked up: {world.inventory[-1]}")
        
        # Auto-use key on door
        if "key" in world.inventory:
            # Check adjacent cells for door
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                check_x = px + dx
                check_y = py + dy
                if (check_x, check_y) in world.entities:
                    entity_type, _ = world.entities[(check_x, check_y)]
                    if entity_type == "door":
                        success, _ = world.use_item("key", check_x, check_y)
                        if success:
                            print("Door unlocked!")
                            if check_win(world):
                                print("Congratulations! You've won!")
                                return

def render_world(world):
    """Simple ASCII rendering of the world."""
    for y in range(world.grid.height):
        for x in range(world.grid.width):
            if (x, y) == world.player_pos:
                print("@", end="")
            elif (x, y) in world.entities:
                entity_type, _ = world.entities[(x, y)]
                symbol = {"key": "k", "door": "D"}[entity_type]
                print(symbol, end="")
            elif world.grid.get_cell(x, y) == 1:
                print("#", end="")
            else:
                print(".", end="")
        print()

def check_win(world):
    """Check if the player has won (reached the exit after unlocking door)."""
    return len([e for e in world.entities.values() if e[0] == "door"]) == 0

if __name__ == "__main__":
    main()
