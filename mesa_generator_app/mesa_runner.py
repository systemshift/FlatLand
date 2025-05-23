import sys
import io
import contextlib

# !!! SECURITY WARNING !!!
# Executing arbitrary code from an LLM using exec() is highly insecure.
# This is a placeholder for an MVP and should be replaced with a
# sandboxed execution environment for any production or shared use.
# Consider Docker containers, RestrictedPython, or other isolation mechanisms.

def run_mesa_code(mesa_code_str: str, model_params=None, steps_to_run: int = 1):
    """
    Executes the provided Mesa Python code string and attempts to run the model.
    Captures stdout from the execution.

    Args:
        mesa_code_str (str): A string containing the Python Mesa code.
        model_params (dict, optional): Parameters to pass to the Mesa model constructor.
                                       Defaults to {"N": 5} if not provided or if None.
        steps_to_run (int, optional): Number of steps to run the simulation. Defaults to 1.

    Returns:
        dict: A dictionary containing:
            - "success": True if execution seemed to complete, False otherwise.
            - "output": Captured stdout from the execution.
            - "error": Error message if an exception occurred.
    """
    if model_params is None:
        model_params = {"N": 5} # Default params for placeholder

    output_buffer = io.StringIO()
    error_message = None
    success = False

    # Create a global scope for exec to run in
    exec_globals = {}

    # Try to pre-populate with mesa, in case exec has trouble finding submodules
    # This is a bit of a defensive measure.
    try:
        import mesa # This 'mesa' is the one from the runner's environment
        exec_globals['mesa'] = mesa 
        # The LLM code will also do 'import mesa', which should resolve to this 'mesa'
        # object within the exec_globals scope.

        # --- REMOVE OLD DEBUGGING LINES or keep them if still useful ---
        # print(f"DEBUG: mesa_runner.py: 'mesa' imported successfully. Path: {getattr(mesa, '__file__', 'N/A')}")
        # print(f"DEBUG: mesa_runner.py: dir(mesa) contains 'time'? {'time' in dir(mesa)}")
        # if 'time' in dir(mesa):
        #     print(f"DEBUG: mesa_runner.py: type(mesa.time): {type(mesa.time)}")
        #     print(f"DEBUG: mesa_runner.py: mesa.time path: {getattr(mesa.time, '__file__', 'N/A')}")
    except ImportError:
        # This case should ideally be caught by the venv setup,
        # but if 'import mesa' fails here, it's a fundamental issue.
        return {
            "success": False,
            "output": "Runner Error: Could not import 'mesa' module directly in runner.",
            "error": "ModuleNotFoundError: No module named 'mesa' (runner pre-import)"
        }

    try:
        # Redirect stdout to capture print statements from the Mesa code
        with contextlib.redirect_stdout(output_buffer):
            # Execute the Mesa code string. This defines classes and functions in exec_globals
            exec(mesa_code_str, exec_globals)

            # Attempt to find and instantiate the Mesa model class.
            # This assumes the LLM names the main model class 'MyModel' or similar.
            # A more robust solution would be to parse the code or have the LLM
            # specify the main model class name.
            ModelClass = None
            # Ensure 'mesa' (the module object) is available for issubclass check
            # It should be in exec_globals from the pre-import or from 'import mesa' in LLM code.
            mesa_module_in_scope = exec_globals.get('mesa')

            if mesa_module_in_scope and hasattr(mesa_module_in_scope, 'Model'):
                for name, obj in exec_globals.items():
                    # Check if obj is a class, is a subclass of mesa.Model, and is not mesa.Model itself
                    if isinstance(obj, type) and \
                       issubclass(obj, mesa_module_in_scope.Model) and \
                       obj is not mesa_module_in_scope.Model:
                        if ModelClass is not None:
                            # More than one model class found, this is ambiguous for now.
                            # Could be handled by asking LLM to name the main one "MainModel" or similar.
                            print(f"Warning: Multiple Mesa model classes found. Using the first one: {ModelClass.__name__}. Found another: {name}")
                        else:
                            ModelClass = obj
                            # print(f"DEBUG: Found Mesa model class: {name}") # Removed for cleanup
                            # We'll take the first one we find.
                            # If multiple are defined by LLM, this might need refinement.
            else:
                print("Warning: mesa or mesa.Model not found in exec_globals. Cannot identify model class.")

            if ModelClass:
                # Instantiate the model
                # This needs to be flexible based on what parameters the LLM-generated model expects.
                # For the placeholder, it expects 'N'.
                try:
                    # Try to instantiate with known placeholder params
                    model_instance = ModelClass(**model_params)
                except TypeError as te:
                    # Fallback if N is not expected or other params are missing
                    print(f"Warning: Could not instantiate model with default params {model_params}. Error: {te}")
                    print("Attempting to instantiate without params (this might fail).")
                    try:
                        model_instance = ModelClass()
                    except Exception as e_fallback:
                        raise Exception(f"Failed to instantiate model with default or no params: {e_fallback}")


                # Run the specified number of steps for the model
                # This assumes the model has a 'step()' method.
                if hasattr(model_instance, 'step') and callable(model_instance.step):
                    print(f"Attempting to run model for {steps_to_run} step(s)...")
                    for i in range(steps_to_run):
                        print(f"--- Runner: Model Step {i + 1}/{steps_to_run} ---")
                        model_instance.step()
                    success = True
                    print("Model simulation steps completed by runner.")
                else:
                    raise AttributeError("Generated model class does not have a callable 'step' method.")
            else:
                raise NameError("Could not find a suitable Mesa model class (e.g., 'MyModel') in the generated code.")

    except Exception as e:
        error_message = f"Error during Mesa code execution: {type(e).__name__}: {e}"
        print(error_message, file=sys.stderr) # Also print to actual stderr for Flask logs
        success = False
    
    captured_output = output_buffer.getvalue()
    return {
        "success": success,
        "output": captured_output,
        "error": error_message
    }

if __name__ == '__main__':
    # Example usage for testing this module directly
    test_code = """
import mesa

class MyAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.val = 0

    def step(self):
        self.val += 1
        print(f"Agent {self.unique_id} stepped. Value: {self.val}")

class MyModel(mesa.Model):
    def __init__(self, N=3): # Default N to 3
        self.num_agents = N
        self.schedule = mesa.time.RandomActivation(self)
        for i in range(self.num_agents):
            a = MyAgent(i, self)
            self.schedule.add(a)
        print(f"MyModel initialized with {N} agents.")

    def step(self):
        self.schedule.step()
        print(f"MyModel stepped. Current schedule time: {self.schedule.time}")

# No if __name__ == '__main__' block needed here for the runner
"""
    print("--- Testing mesa_runner.py ---")
    result = run_mesa_code(test_code, model_params={"N": 2}) # Test with N=2
    print("\n--- Execution Result ---")
    print(f"Success: {result['success']}")
    print("Output:")
    print(result['output'])
    if result['error']:
        print(f"Error: {result['error']}")
    print("------------------------")

    result_no_params = run_mesa_code(test_code) # Test with default N=3 in class
    print("\n--- Execution Result (No Params to runner, class default N=3) ---")
    print(f"Success: {result_no_params['success']}")
    print("Output:")
    print(result_no_params['output'])
    if result_no_params['error']:
        print(f"Error: {result_no_params['error']}")
    print("------------------------")

    error_code = "import mesa\n\ndef some_func():\n print('hello')\n\nMyModel = 1/0" # Code that will raise an error
    result_error = run_mesa_code(error_code)
    print("\n--- Execution Result (Error Code) ---")
    print(f"Success: {result_error['success']}")
    print("Output:")
    print(result_error['output'])
    if result_error['error']:
        print(f"Error: {result_error['error']}")
    print("------------------------")
