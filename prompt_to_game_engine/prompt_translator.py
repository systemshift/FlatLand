import os
import json
import requests # To call our Game MCP Server
from openai import OpenAI
import jsonschema # For validating the LLM's output

# Configuration
GAME_MCP_SERVER_URL = "http://127.0.0.1:5002" # Make sure this matches your game_mcp_server.py port
LLM_MODEL_NAME = "gpt-3.5-turbo" # Or "gpt-4" or other compatible model

class PromptTranslatorService:
    def __init__(self):
        self.game_mcp_server_url = GAME_MCP_SERVER_URL
        try:
            self.openai_client = OpenAI() # API key is read from OPENAI_API_KEY env var
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            print("Please ensure your OPENAI_API_KEY environment variable is set correctly.")
            self.openai_client = None
        
        self.sgd_schema = None

    def _fetch_sgd_schema(self) -> bool:
        """Fetches the SGD schema from the Game MCP Server."""
        if self.sgd_schema and "error" not in self.sgd_schema : # Cache schema if already fetched
            return True
        try:
            response = requests.post(f"{self.game_mcp_server_url}/mcp/get_sgd_schema")
            response.raise_for_status() # Raise an exception for HTTP errors
            data = response.json()
            if data.get("success"):
                self.sgd_schema = data.get("schema")
                print("Successfully fetched SGD schema.")
                return True
            else:
                print(f"Failed to fetch SGD schema: {data.get('message')}")
                self.sgd_schema = {"error": data.get('message', "Unknown error fetching schema")}
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Game MCP Server to fetch schema: {e}")
            self.sgd_schema = {"error": str(e)}
            return False

    def translate_prompt_to_sgd(self, user_prompt: str) -> tuple[Optional[str], Optional[str]]:
        """
        Translates a user's natural language prompt into an SGD JSON string.
        Returns a tuple: (sgd_json_string, error_message).
        sgd_json_string is None if an error occurred.
        """
        if not self.openai_client:
            return None, "OpenAI client not initialized. Check API key."

        if not self._fetch_sgd_schema() or "error" in self.sgd_schema:
            return None, f"Could not retrieve SGD schema: {self.sgd_schema.get('error', 'Unknown schema error')}"

        system_prompt_content = f"""
You are an expert game designer. Your task is to translate a user's natural language description 
of a 2D grid-based game into a structured JSON format. This JSON format MUST strictly adhere 
to the following JSON schema:

```json
{json.dumps(self.sgd_schema, indent=2)}
```

Key considerations:
- Ensure all required fields in the schema are present in your generated JSON.
- Entity IDs must be unique.
- Positions (x, y) must be within the defined grid dimensions (0-indexed).
- Player controls should map common inputs (like "ArrowUp") to actions (like "move_y(-1)").
- Rules should be simple and clearly defined based on the user's intent.
- If the user's prompt is ambiguous, make reasonable assumptions to create a playable simple game.
- Output ONLY the JSON string. Do not include any other text, explanations, or markdown formatting.
"""

        try:
            print(f"Sending prompt to LLM (model: {LLM_MODEL_NAME})...")
            completion = self.openai_client.chat.completions.create(
                model=LLM_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt_content},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"} # Request JSON output if model supports it
            )
            
            generated_json_string = completion.choices[0].message.content
            if not generated_json_string:
                return None, "LLM returned an empty response."

            print("LLM response received. Validating JSON...")
            # Validate the generated JSON against the schema
            try:
                generated_sgd = json.loads(generated_json_string)
                jsonschema.validate(instance=generated_sgd, schema=self.sgd_schema)
                print("Generated SGD JSON is valid against the schema.")
                return json.dumps(generated_sgd, indent=2), None # Return formatted JSON string
            except json.JSONDecodeError as e:
                error_msg = f"LLM output was not valid JSON: {e}. Output: {generated_json_string[:500]}"
                print(error_msg)
                return None, error_msg
            except jsonschema.exceptions.ValidationError as e:
                error_msg = f"LLM output did not conform to SGD schema: {e.message}. Output: {generated_json_string[:500]}"
                print(error_msg)
                return None, error_msg

        except Exception as e:
            error_msg = f"Error during LLM API call or processing: {e}"
            print(error_msg)
            return None, error_msg


if __name__ == '__main__':
    print("Testing PromptTranslatorService...")
    print("Ensure your Game MCP Server (game_mcp_server.py) is running on " + GAME_MCP_SERVER_URL)
    print("Ensure your OPENAI_API_KEY environment variable is set.\n")

    translator = PromptTranslatorService()

    # Test 1: Fetch schema (implicitly called by translate)
    # translator._fetch_sgd_schema() # Can test this separately if needed

    # Test 2: Translate a prompt
    # Note: This test will make a real call to the OpenAI API and Game MCP Server.
    # example_user_prompt = "Create a very simple 3x3 grid game. A player 'P' starts at 0,0. An exit 'E' is at 2,2. Player moves with Arrow keys. Reaching E wins."
    example_user_prompt = "A 5x5 grid. Player 'P' at (1,1). A wall '#' at (2,1). A goal 'G' at (3,3). Player moves with ArrowUp, ArrowDown, ArrowLeft, ArrowRight. If player touches goal, player wins."
    
    print(f"Attempting to translate prompt: \"{example_user_prompt}\"")
    sgd_json, error = translator.translate_prompt_to_sgd(example_user_prompt)

    if error:
        print(f"\nTranslation Error: {error}")
    elif sgd_json:
        print("\nSuccessfully translated prompt to SGD JSON:")
        print(sgd_json)
        
        # You could potentially try to load this SGD into the GameEngine here for a full loop test
        # from .game_engine import GameEngine
        # engine = GameEngine()
        # if engine.load_game_from_sgd(sgd_json):
        #     print("\nTest: SGD successfully loaded into GameEngine.")
        # else:
        #     print("\nTest: Failed to load generated SGD into GameEngine.")
    else:
        print("\nTranslation failed with no specific error message, but no SGD JSON was returned.")
