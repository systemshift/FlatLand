import os
# from openai import OpenAI # Uncomment when OpenAI library is added to requirements

# Placeholder for API key, ideally loaded from .env
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
#     print("Warning: OPENAI_API_KEY not found in environment variables.")
# client = OpenAI(api_key=OPENAI_API_KEY)

def get_mesa_code(user_prompt: str) -> str:
    """
    Takes a user's natural language prompt and returns Mesa Python code.
    This is a placeholder and will need to be implemented with actual OpenAI API calls.
    """
    if not user_prompt:
        return "# No prompt provided to generate Mesa code."

    # --- Prompt Engineering Section ---
    # This system prompt needs to be carefully designed to guide the LLM
    # to produce valid and runnable Mesa code.
    system_prompt = """You are an expert Python programmer specializing in the Mesa agent-based modeling framework.
Your task is to take a user's description of a simulation and generate a complete, runnable Mesa Python script.

The script should include:
1.  Relevant agent class(es) inheriting from `mesa.Agent`.
2.  A model class inheriting from `mesa.Model`.
3.  The model class should have an `__init__` method to set up agents, a scheduler (e.g., `mesa.time.RandomActivation`), and any necessary parameters.
4.  The model class must have a `step()` method that advances the simulation by one step, including agent steps and model-level actions.
5.  If the simulation involves a grid, use `mesa.space.MultiGrid` or `mesa.space.SingleGrid`.
6.  Consider including `mesa.DataCollector` if the user's prompt implies data collection needs.
7.  The generated code should be a single Python script that can be executed directly.
8.  Ensure all necessary Mesa imports are included (e.g., `import mesa`).

User's simulation description:
---
{user_prompt}
---

Generated Mesa Python Code:
"""

    full_prompt = system_prompt.format(user_prompt=user_prompt)

    # --- OpenAI API Call (Placeholder) ---
    # try:
    #     response = client.chat.completions.create(
    #         model="gpt-4",  # Or your preferred model
    #         messages=[
    #             {"role": "system", "content": "You are an expert Python programmer specializing in the Mesa agent-based modeling framework."},
    #             {"role": "user", "content": full_prompt} # Or structure messages more granularly
    #         ]
    #     )
    #     generated_code = response.choices[0].message.content
    #     return generated_code
    # except Exception as e:
    #     print(f"Error calling OpenAI API: {e}")
    #     return f"# Error generating code: {e}"

    # Placeholder response for now
    placeholder_code = f"""import mesa

# Placeholder Mesa code generated for prompt: "{user_prompt}"

class MyAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # Agent initialization

    def step(self):
        # Agent's step logic
        print(f"Agent {{self.unique_id}} is stepping.")

class MyModel(mesa.Model):
    def __init__(self, N):
        self.num_agents = N
        self.schedule = mesa.time.RandomActivation(self)
        # Create agents
        for i in range(self.num_agents):
            a = MyAgent(i, self)
            self.schedule.add(a)

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        print("Model stepped.")

if __name__ == '__main__':
    # Example of how to run the model
    model = MyModel(N=10)
    for i in range(5):
        print(f"--- Iteration {i+1} ---")
        model.step()
"""
    return placeholder_code

if __name__ == '__main__':
    # Example usage (for testing this module directly)
    test_prompt = "Create a simple simulation of 5 agents moving randomly."
    code = get_mesa_code(test_prompt)
    print("--- Generated Code ---")
    print(code)
    print("----------------------")
