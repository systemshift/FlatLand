import json
from flatland.logic_engine import LogicEngine

def main():
    # Load the Sokoban environment
    with open('examples/sokoban.json', 'r') as f:
        env_def = json.load(f)
    
    # Create and initialize the engine
    engine = LogicEngine()
    engine.load_environment(env_def)
    
    # Run a few simulation steps
    print("Initial state:")
    print_state(engine.state_manager.get_current_state())
    
    for i in range(5):
        print(f"\nStep {i + 1}:")
        result = engine.step()
        print("Changes:", result['changes'])
        print_state(result['state'])

def print_state(state):
    """Helper function to visualize the grid state."""
    grid = state['grid']
    cells = grid['cells']
    
    # Cell type mapping
    symbols = {
        0: '.',  # Empty
        1: '#',  # Wall
        2: '@',  # Player
        3: '$',  # Box
        4: '.',  # Goal
    }
    
    print("Grid:")
    for row in cells:
        print(''.join(symbols.get(cell, '?') for cell in row))
    
    print("\nEntities:")
    for entity in state['entities']:
        print(f"- {entity['type']} at position {entity['position']}")

if __name__ == '__main__':
    main()
