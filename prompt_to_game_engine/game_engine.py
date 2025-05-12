from typing import Dict, Any, Optional, List
import json # For loading schema if needed, and parsing SGD
from .game_state import GameState
from .game_elements import GameEntity
# We might need a JSON schema validator later, e.g., jsonschema
# import jsonschema

class GameEngine:
    """
    Manages the game logic, state, and rules execution based on an SGD.
    """
    def __init__(self):
        self.game_state: Optional[GameState] = None
        self.sgd_data: Optional[Dict[str, Any]] = None
        self.player_entity_id: Optional[str] = None
        self.player_controls: Dict[str, str] = {}
        self.game_rules: List[Dict[str, Any]] = []
        self.win_conditions: List[Dict[str, Any]] = []
        self.loss_conditions: List[Dict[str, Any]] = []

    def load_game_from_sgd(self, sgd_json_string: str) -> bool:
        """
        Loads and initializes a game from a Structured Game Definition JSON string.
        """
        try:
            self.sgd_data = json.loads(sgd_json_string)
            # TODO: Validate sgd_data against sgd_schema_v0.1.json
            # For now, we assume it's valid.
            # Example: jsonschema.validate(instance=self.sgd_data, schema=loaded_schema)
        except json.JSONDecodeError as e:
            print(f"Error decoding SGD JSON: {e}")
            return False
        
        if not self.sgd_data:
            return False

        self.game_state = GameState.from_sgd(self.sgd_data)
        
        player_controls_data = self.sgd_data.get('player_controls', {})
        self.player_entity_id = player_controls_data.get('default_player_id')
        self.player_controls = {k: v for k, v in player_controls_data.items() if k != 'default_player_id'}

        self.game_rules = self.sgd_data.get('rules', [])
        self.win_conditions = self.sgd_data.get('win_conditions', [])
        self.loss_conditions = self.sgd_data.get('loss_conditions', [])
        
        self.game_state.game_status = "running"
        self.game_state.message = f"Game '{self.sgd_data.get('metadata',{}).get('name','Unnamed Game')}' loaded."
        return True

    def get_current_state_dict(self) -> Optional[Dict[str, Any]]:
        """Returns the current game state as a dictionary."""
        if self.game_state:
            return self.game_state.to_dict()
        return None

    def process_player_input(self, input_key: str) -> Optional[Dict[str, Any]]:
        """
        Processes a player input (e.g., 'ArrowUp', 'action1').
        Returns the updated game state dictionary or None if error.
        """
        if not self.game_state or self.game_state.game_status != "running":
            self.game_state.message = "Game not running or not loaded."
            return self.get_current_state_dict()

        if not self.player_entity_id:
            self.game_state.message = "No player entity defined."
            return self.get_current_state_dict()

        player = self.game_state.get_entity(self.player_entity_id)
        if not player:
            self.game_state.message = f"Player entity '{self.player_entity_id}' not found."
            return self.get_current_state_dict()

        action_string = self.player_controls.get(input_key)
        if not action_string:
            self.game_state.message = f"No action defined for input '{input_key}'."
            return self.get_current_state_dict()

        # Rudimentary action parsing: "move_x(1)", "move_y(-1)"
        # This will need to be significantly more robust.
        original_x, original_y = player.x, player.y
        action_processed_message = f"Processed '{input_key}' -> '{action_string}'."

        if action_string.startswith("move_x("):
            try:
                delta_x = int(action_string[len("move_x("):-1])
                target_x, target_y = player.x + delta_x, player.y
                self._attempt_move(player, target_x, target_y)
            except ValueError:
                action_processed_message = f"Invalid move_x parameter in '{action_string}'."
        elif action_string.startswith("move_y("):
            try:
                delta_y = int(action_string[len("move_y("):-1])
                target_x, target_y = player.x, player.y + delta_y
                self._attempt_move(player, target_x, target_y)
            except ValueError:
                 action_processed_message = f"Invalid move_y parameter in '{action_string}'."
        else:
            action_processed_message = f"Unknown action type: '{action_string}'."
            # TODO: Implement more actions and rule processing here

        self.game_state.message = action_processed_message
        
        # TODO: After action, evaluate rules (self.game_rules)
        self._evaluate_rules(event_type="on_player_action", player_action=action_string)

        # Check win/loss conditions
        self._check_game_over_conditions()

        return self.get_current_state_dict()

    def _attempt_move(self, entity: GameEntity, target_x: int, target_y: int):
        """Helper to attempt moving an entity, checking for boundaries and collisions."""
        if not self.game_state: return

        # Boundary checks
        if not (0 <= target_x < self.game_state.grid_width and \
                0 <= target_y < self.game_state.grid_height):
            self.game_state.message = f"{entity.id} tried to move out of bounds."
            return

        # Collision checks (very basic: assumes any other entity with 'is_solid' is a blocker)
        entities_at_target = self.game_state.get_entities_at_position(target_x, target_y)
        collided_with_solid = False
        for other_entity in entities_at_target:
            if other_entity.id != entity.id and other_entity.properties.get("is_solid", False):
                collided_with_solid = True
                self.game_state.message = f"{entity.id} collided with solid {other_entity.id}."
                # TODO: Trigger 'on_collision' event for rules
                self._evaluate_rules(event_type="on_collision", entity_a=entity, entity_b=other_entity)
                break
        
        if not collided_with_solid:
            self.game_state.move_entity(entity.id, target_x, target_y)
            self.game_state.message = f"{entity.id} moved to ({target_x},{target_y})."
            # TODO: Trigger 'on_entity_move' event for rules
            self._evaluate_rules(event_type="on_entity_move", entity=entity)


    def _evaluate_rules(self, event_type: str, **kwargs):
        """
        Rudimentary rule evaluation.
        This needs to be fleshed out with a proper condition parser and action executor.
        """
        if not self.game_state: return

        applicable_rules = [rule for rule in self.game_rules if rule.get("event") == event_type]
        for rule in applicable_rules:
            # print(f"Considering rule '{rule.get('name')}' for event '{event_type}'")
            # TODO: Implement condition checking (rule.get("conditions"))
            #       This would involve parsing condition strings and evaluating them against game_state.
            #       Example: "player.properties.health > 0", "entity_collided_with.type == 'wall'"
            
            # For now, assume conditions are met if specified, or if no conditions.
            conditions_met = True # Placeholder
            if "conditions" in rule and rule["conditions"]:
                # Placeholder for actual condition evaluation logic
                # print(f"  Rule conditions: {rule['conditions']} - SKIPPING EVALUATION FOR NOW")
                pass # Actual logic would go here

            if conditions_met:
                # print(f"  Executing actions for rule '{rule.get('name')}'")
                # TODO: Implement action execution (rule.get("actions"))
                #       This would involve parsing action strings and modifying game_state.
                #       Example: "game_state.get_entity('player').properties.score += 10"
                #                "game_state.remove_entity('collided_enemy')"
                #                "game_state.game_status = 'won'"
                for action_str in rule.get("actions", []):
                    # print(f"    Action: {action_str} - SKIPPING EXECUTION FOR NOW")
                    # Example: if action_str == "increment_score(10)": self.game_state.score += 10
                    pass # Actual logic would go here
    
    def _check_game_over_conditions(self):
        """Checks win and loss conditions."""
        if not self.game_state or self.game_state.game_status != "running":
            return

        # Check Win Conditions
        for wc_group in self.win_conditions:
            # TODO: Implement actual condition evaluation based on wc_group["conditions"]
            #       and wc_group["condition_group_logic"] (AND/OR)
            # Placeholder: if any win condition group is met (needs real logic)
            # Example: if self.game_state.get_entity(self.player_entity_id).x == target_goal.x ...
            pass # Real logic needed

        # Check Loss Conditions
        for lc_group in self.loss_conditions:
            # TODO: Implement actual condition evaluation
            # Placeholder: if any loss condition group is met (needs real logic)
            # Example: if self.game_state.get_entity(self.player_entity_id).properties.get('health', 0) <= 0:
            #    self.game_state.game_status = "lost"
            #    self.game_state.message = lc_group.get("description", "You lost!")
            #    return
            pass # Real logic needed


if __name__ == '__main__':
    # Example SGD JSON string
    example_sgd_str = """
    {
      "metadata": {"name": "Simple Maze", "version": "0.1.0"},
      "grid": {"width": 5, "height": 5, "default_tile": "."},
      "entities": [
        {"id": "player", "type": "player", "appearance": {"char": "P"}, "initial_position": {"x": 0, "y": 0}, "properties": {"is_movable": true}},
        {"id": "wall1", "type": "wall", "appearance": {"char": "#"}, "initial_position": {"x": 1, "y": 0}, "properties": {"is_solid": true}},
        {"id": "goal", "type": "goal", "appearance": {"char": "G"}, "initial_position": {"x": 4, "y": 4}}
      ],
      "player_controls": {
        "default_player_id": "player",
        "ArrowUp": "move_y(-1)",
        "ArrowDown": "move_y(1)",
        "ArrowLeft": "move_x(-1)",
        "ArrowRight": "move_x(1)"
      },
      "rules": [
        {
            "name": "reach_goal",
            "event": "on_collision", 
            "conditions": ["entity_a.type == 'player'", "entity_b.type == 'goal'"],
            "actions": ["game.set_status('won')", "game.set_message('You reached the goal!')"]
        }
      ],
      "win_conditions": [
        {"description": "Player reaches goal", "conditions": ["player.position == goal.position"]} 
      ]
    }
    """
    engine = GameEngine()
    if engine.load_game_from_sgd(example_sgd_str):
        print("Game loaded successfully.")
        print(f"Initial state: {json.dumps(engine.get_current_state_dict(), indent=2)}")

        # Simulate some inputs
        inputs = ["ArrowRight", "ArrowRight", "ArrowDown", "ArrowDown", "ArrowDown", "ArrowDown", "ArrowRight", "ArrowRight"]
        for inp in inputs:
            print(f"\nProcessing input: {inp}")
            updated_state = engine.process_player_input(inp)
            if updated_state:
                print(f"Message: {updated_state.get('message')}")
                # print(f"State: {json.dumps(updated_state, indent=2)}")
                if updated_state.get("game_status") != "running":
                    print(f"Game Over! Status: {updated_state.get('game_status')}")
                    break
    else:
        print("Failed to load game.")
