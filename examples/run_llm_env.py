import json
import sys
from flatland.logic_engine import LogicEngine

def load_prompt_template():
    """Load the base prompt template."""
    with open('src/flatland/prompt_template.txt', 'r') as f:
        return f.read()

def create_game_prompt(game_type):
    """Create a complete prompt for the specified game type."""
    template = load_prompt_template()
    return template.replace('[GAME_TYPE]', game_type)

def save_environment(env_json, filename):
    """Save the environment JSON to a file."""
    with open(filename, 'w') as f:
        json.dump(env_json, f, indent=2)

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_llm_env.py <game_type>")
        print("Example: python run_llm_env.py Snake")
        sys.exit(1)

    game_type = sys.argv[1]
    
    # Create the complete prompt
    prompt = create_game_prompt(game_type)
    
    print(f"\nPrompt ready for {game_type} environment generation.")
    print("Steps to use this prompt:")
    print("1. Copy the following prompt and feed it to your LLM (e.g., GPT-4)")
    print("2. Save the LLM's JSON output to a file (e.g., 'generated_env.json')")
    print("3. Run this script again with the environment file to test it")
    print("\n=== PROMPT BEGIN ===")
    print(prompt)
    print("=== PROMPT END ===\n")

    # Ask user if they want to test an existing environment
    response = input("Do you have a generated environment to test? (y/n): ")
    if response.lower() != 'y':
        return

    # Get the environment file path
    env_file = input("Enter the path to your environment JSON file: ")
    
    try:
        # Load the environment
        with open(env_file, 'r') as f:
            env_def = json.load(f)
        
        # Create and initialize the engine
        engine = LogicEngine()
        engine.load_environment(env_def)
        
        # Print initial state
        print("\nInitial state:")
        print_state(engine.state_manager.get_current_state())
        
        # Game loop
        while True:
            # Get player input
            command = input("\nEnter move (up/down/left/right) or 'q' to quit: ").lower()
            if command == 'q':
                break
                
            if command not in ['up', 'down', 'left', 'right']:
                print("Invalid command!")
                continue
                
            # Process move
            result = engine.process_input(command)
            
            if "error" in result:
                print("Error:", result["error"])
                continue
                
            # Print results
            print("\nChanges:", result['changes'])
            print_state(result['state'])
            
            # Check victory/failure conditions
            if result['victory']:
                print("\nVictory! You've completed the game!")
                break
            elif result['failure']:
                print("\nGame Over!")
                break

    except FileNotFoundError:
        print(f"Error: Could not find file {env_file}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file {env_file}")
    except Exception as e:
        print(f"Error: {str(e)}")

def print_state(state):
    """Helper function to visualize the grid state."""
    grid = state['grid']
    cells = grid['cells']
    
    print("\nGrid (Raw Values):")
    for row in cells:
        print(' '.join(str(cell) for cell in row))
        
    print("\nGrid (Symbols):")
    # Cell type mapping (customizable based on game type)
    symbols = {
        0: '.',  # Empty
        1: '#',  # Wall
        2: '@',  # Player/Head
        3: '*',  # Food/Goal
        4: 'o',  # Body/Trail
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
