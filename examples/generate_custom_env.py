"""
Example script demonstrating how to use FlatLand's LLM integration to generate custom environments.
"""

import os
import json
from flatland.llm import generate_environment
from flatland.logic_engine import LogicEngine

def save_environment(env_def, filename):
    """Save the environment definition to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(env_def.to_dict(), f, indent=2)

def main():
    # Ensure API key is set
    if not os.getenv("FLATLAND_OPENAI_KEY"):
        print("Please set the FLATLAND_OPENAI_KEY environment variable")
        print("Example: export FLATLAND_OPENAI_KEY='your-api-key'")
        return

    print("\nFlatLand Environment Generator")
    print("=============================")
    print("\nThis tool uses OpenAI to generate custom game environments.")
    print("You can describe any type of grid-based game or simulation.")
    
    # Get user's environment description
    print("\nDescribe your desired environment/game:")
    print("(Example: A maze where the player must collect keys to unlock doors,")
    print(" with enemies that follow fixed patrol routes)")
    description = input("\nYour description: ")
    
    # Optional style guidance
    print("\nAny specific style or theme? (optional)")
    print("(Example: cyberpunk, medieval, minimalist, etc.)")
    style = input("Style guidance (press Enter to skip): ")
    
    print("\nGenerating environment...")
    try:
        # Generate the environment
        env_def = generate_environment(
            description=description,
            style_guidance=style if style else None
        )
        
        # Save to file
        filename = input("\nEnter filename to save (e.g., custom_maze.json): ")
        save_environment(env_def, filename)
        print(f"\nEnvironment saved to {filename}")
        
        # Ask if user wants to test it
        test = input("\nWould you like to test the environment? (y/n): ")
        if test.lower() == 'y':
            # Initialize the engine with generated environment
            engine = LogicEngine()
            engine.load_environment(env_def.to_dict())
            
            print("\nInitial state:")
            print_state(engine.state_manager.get_current_state())
            
            # Game loop
            while True:
                command = input("\nEnter move (up/down/left/right) or 'q' to quit: ").lower()
                if command == 'q':
                    break
                    
                if command not in ['up', 'down', 'left', 'right']:
                    print("Invalid command!")
                    continue
                    
                result = engine.process_input(command)
                
                if "error" in result:
                    print("Error:", result["error"])
                    continue
                    
                print("\nChanges:", result['changes'])
                print_state(result['state'])
                
                if result['victory']:
                    print("\nVictory! You've completed the game!")
                    break
                elif result['failure']:
                    print("\nGame Over!")
                    break
                
    except Exception as e:
        print(f"\nError: {str(e)}")

def print_state(state):
    """Helper function to visualize the grid state."""
    grid = state['grid']
    cells = grid['cells']
    
    print("\nGrid (Raw Values):")
    for row in cells:
        print(' '.join(str(cell) for cell in row))
        
    print("\nGrid (Symbols):")
    symbols = {
        0: '.',  # Empty
        1: '#',  # Wall
        2: '@',  # Player
        3: '*',  # Interactive (keys, doors, etc)
        4: 'o',  # Goal/special
    }
    
    for row in cells:
        print(''.join(symbols.get(cell, '?') for cell in row))
    
    print("\nEntities:")
    for entity in state['entities']:
        print(f"- {entity['type']} at position {entity['position']}")
        if 'properties' in entity:
            print(f"  Properties: {entity['properties']}")

if __name__ == '__main__':
    main()
