import json
from flatland.logic_engine import LogicEngine

def main():
    # Load the Sokoban environment
    with open('examples/sokoban.json', 'r') as f:
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
            print("\nVictory! You've completed the puzzle!")
            break
        elif result['failure']:
            print("\nGame Over!")
            break

def print_state(state):
    """Helper function to visualize the grid state."""
    grid = state['grid']
    cells = grid['cells']
    
    print("Grid (Raw Values):")
    for row in cells:
        print(' '.join(str(cell) for cell in row))
        
    print("\nGrid (Symbols):")
    # Cell type mapping
    symbols = {
        0: '.',  # Empty
        1: '#',  # Wall
        2: '@',  # Player
        3: '$',  # Box
        4: '.',  # Goal
    }
    
    for row in cells:
        print(''.join(symbols.get(cell, '?') for cell in row))
    
    print("\nEntities:")
    for entity in state['entities']:
        print(f"- {entity['type']} at position {entity['position']}")

if __name__ == '__main__':
    main()
