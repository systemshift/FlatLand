import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file at the module level
# This ensures OPENAI_API_KEY is available when the client is initialized.
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("CRITICAL: OPENAI_API_KEY not found in environment variables.")
    print("Please ensure a .env file exists in the 'mesa_generator_app' directory and contains your OPENAI_API_KEY.")
    # In a real app, you might raise an exception or have a fallback.
    # For now, the client initialization will fail if the key is missing.
    client = None 
else:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        client = None


def get_mesa_code(user_prompt: str, model_name: str = "o4-mini-2025-04-16") -> str:
    """
    Takes a user's natural language prompt and returns Mesa Python code
    by calling the OpenAI API.
    """
    if not client:
        return "# Error: OpenAI client not initialized. Check API key."
    if not OPENAI_API_KEY: # Double check, though client init should catch it
        return "# Error: OPENAI_API_KEY is not set."
    if not user_prompt:
        return "# No prompt provided to generate Mesa code."

    # --- Prompt Engineering Section ---
    system_message_content = """You are an expert Python programmer specializing in the Mesa agent-based modeling framework.
Your task is to take a user's description of a simulation and generate a complete, runnable Mesa Python script.

The script should include:
1.  All necessary imports, primarily `import mesa` and potentially `mesa.time`, `mesa.space`, `mesa.DataCollector`.
2.  Relevant agent class(es) inheriting from `mesa.Agent`. Agents should have an `__init__` method and a `step()` method.
3.  A model class inheriting from `mesa.Model`.
4.  The model class should have an `__init__` method to set up agents, a scheduler (e.g., `mesa.time.RandomActivation(self)`), and any necessary parameters (e.g., number of agents, width, height for a grid).
5.  The model class must have a `step()` method that advances the simulation by one step. This typically involves calling `self.schedule.step()`.
6.  If the simulation involves a grid, use `mesa.space.MultiGrid` or `mesa.space.SingleGrid`. Initialize it in the model's `__init__` and place agents on it.
7.  Consider including `mesa.DataCollector` if the user's prompt implies data collection needs (e.g., "track the number of happy agents").
8.  The generated code should be a single Python script. Do NOT include any example run block like `if __name__ == '__main__':`. The runner script will handle instantiation and execution.
9.  Do NOT use any markdown formatting (e.g., ```python ... ```) in your response. Return only the raw Python code.
10. Ensure the model's `__init__` method can be called with keyword arguments if it takes parameters (e.g. `def __init__(self, N=10, width=10, height=10):`).
"""

    user_message_content = f"""User's simulation description:
---
{user_prompt}
---

Please generate the Mesa Python code based on this description. Remember to only output the raw Python code.
"""

    try:
        print(f"Sending prompt to OpenAI API (model: {model_name})...")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_message_content},
                {"role": "user", "content": user_message_content}
            ]
            # temperature=0.2 # Removed as it's not supported by the user's new model
            # If a specific temperature is needed and supported, it can be re-added.
            # For models that only support default temperature, omitting it is best.
        )
        generated_code = response.choices[0].message.content

        # Clean up potential markdown code fences if the LLM ignores the instruction
        if generated_code.strip().startswith("```python"):
            generated_code = generated_code.split("```python\n", 1)[-1]
            if generated_code.strip().endswith("```"):
                generated_code = generated_code.rsplit("\n```", 1)[0]
        
        print("Successfully received code from OpenAI API.")
        return generated_code.strip()
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return f"# Error generating code from OpenAI: {e}"

if __name__ == '__main__':
    # Example usage (for testing this module directly)
    # Ensure your .env file is in the mesa_generator_app directory and has OPENAI_API_KEY
    if not OPENAI_API_KEY or not client:
        print("Skipping direct test of openai_interface.py: OPENAI_API_KEY not set or client failed to initialize.")
    else:
        print("Testing openai_interface.py directly...")
        # test_prompt = "Create a simple simulation of 3 agents. Each agent has a counter that increments by 1 at each step. The model runs for 2 steps."
        test_prompt = "A model with 5 agents on a 10x10 grid. Agents move randomly one cell at each step. Run for 3 steps."
        # test_prompt = "Schelling model with 100 agents, 20x20 grid, homophily threshold of 3, 2 agent types. Run for 10 steps."

        print(f"Test prompt: {test_prompt}")
        code = get_mesa_code(test_prompt)
        print("\n--- Generated Code ---")
        print(code)
        print("----------------------\n")

        # Test with a different model if desired
        # code_gpt4 = get_mesa_code(test_prompt, model_name="gpt-4") # Or "gpt-4-turbo" etc.
        # print("\n--- Generated Code (GPT-4) ---")
        # print(code_gpt4)
        # print("----------------------------\n")
