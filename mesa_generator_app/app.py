from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

# Import custom modules
import openai_interface
import mesa_runner

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)

@app.route('/')
def index():
    # Later, this will render an HTML page from templates/index.html
    return "Mesa Generator App - Backend is running. UI Coming Soon!"

@app.route('/generate_mesa', methods=['POST'])
def generate_mesa_endpoint():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Request body must be JSON and contain a 'prompt' field."}), 400

    user_prompt = data['prompt']
    model_params = data.get('model_params', None) # Optional model parameters

    # 1. Call OpenAI Interface
    # Note: Actual OpenAI API call is still placeholder in openai_interface.py
    # You'll need to set your OPENAI_API_KEY in a .env file for the real calls.
    print(f"Received prompt: {user_prompt}")
    mesa_code_str = openai_interface.get_mesa_code(user_prompt)
    
    if mesa_code_str.startswith("# Error") or mesa_code_str.startswith("# No prompt"):
        return jsonify({"error": "Failed to generate Mesa code from prompt.", "details": mesa_code_str}), 500

    print("--- Generated Mesa Code (Placeholder) ---")
    print(mesa_code_str)
    print("--------------------------------------")

    # 2. Call Mesa Runner
    # WARNING: This uses exec() and is insecure. For development/MVP only.
    print("Attempting to run Mesa code...")
    simulation_result = mesa_runner.run_mesa_code(mesa_code_str, model_params=model_params)
    print("--- Simulation Result ---")
    print(simulation_result)
    print("-------------------------")

    return jsonify({
        "message": "Mesa code generation and execution attempt complete.",
        "user_prompt": user_prompt,
        "generated_code_preview": mesa_code_str.splitlines()[:15], # Preview first 15 lines
        "simulation_output": simulation_result.get("output"),
        "simulation_success": simulation_result.get("success"),
        "simulation_error": simulation_result.get("error")
    })

if __name__ == '__main__':
    # Ensure OPENAI_API_KEY is loaded if you uncomment the actual API calls
    # For now, it works with placeholders.
    # if not os.getenv("OPENAI_API_KEY"):
    #     print("CRITICAL: OPENAI_API_KEY is not set in the environment variables.")
    #     print("Please create a .env file with your OPENAI_API_KEY.")
        # exit(1) # Or handle more gracefully

    app.run(debug=True, port=5001)
