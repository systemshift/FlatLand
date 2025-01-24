from flatland.generator import EnvironmentGenerator
from flatland.templates import get_template, list_templates
import json

def main():
    # Show available templates
    print("Available Templates:")
    templates = list_templates()
    for name, schema in templates.items():
        print(f"\n{name}:")
        print(json.dumps(schema, indent=2))
    
    # Create a maze environment
    print("\nGenerating maze environment...")
    maze_template = get_template("maze")
    maze_json = maze_template.generate({
        "width": 15,
        "height": 15,
        "difficulty": "hard",
        "keys_required": 2
    })
    
    # Parse and validate the environment
    generator = EnvironmentGenerator()
    response = generator.from_json(maze_json)
    
    if response.error:
        print(f"Error: {response.error}")
        return
    
    # Create world from definition
    world = generator.to_world(response.definition)
    
    print("\nEnvironment created successfully!")
    print(f"Size: {response.metadata['size']}")
    print(f"Entities: {response.metadata['entity_count']}")
    print(f"Rules: {response.metadata['rule_count']}")
    
    # Render the environment
    print("\nEnvironment Layout:")
    render_world(world)
    
    # Export back to JSON
    exported = generator.to_json(world)
    print("\nExported Environment:")
    print(exported)

def render_world(world):
    """Simple ASCII rendering of the world."""
    for y in range(world.grid.height):
        for x in range(world.grid.width):
            if (x, y) == world.player_pos:
                print("@", end="")
            elif (x, y) in world.entities:
                entity_type, _ = world.entities[(x, y)]
                symbol = {
                    "key": "k",
                    "door": "D",
                    "block": "b",
                    "target": "x",
                    "switch": "s",
                    "tile": "t"
                }.get(entity_type, "?")
                print(symbol, end="")
            elif world.grid.get_cell(x, y) == 1:
                print("#", end="")
            else:
                print(".", end="")
        print()

if __name__ == "__main__":
    main()
