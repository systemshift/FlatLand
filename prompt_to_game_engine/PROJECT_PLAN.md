# Project Plan: Prompt-to-2D Game Engine

**Overall Goal:** Create a system where a user can type a natural language prompt (e.g., "a simple maze game"), have it translated into a 2D grid-based game's Structured Game Definition (SGD), and then play that game in a web UI. The system will use an MCP-like interface for its core game engine.

---

## Phase 1: Core Game Engine & MCP Server Foundation

**Status:** ✅ COMPLETED

**Goal:** Create a simple game engine that can run games defined by a structured format, and expose this engine via an MCP-like server.

**Steps:**

1.  **Define the Structured Game Definition (SGD) v0.1 Schema:**
    *   **Status:** ✅ DONE
    *   **Deliverable:** `prompt_to_game_engine/sgd_schema_v0.1.json` - A JSON schema for defining 2D grid games.

2.  **Implement Core Game Logic (Python):**
    *   **Status:** ✅ DONE
    *   **Deliverables:**
        *   `prompt_to_game_engine/game_elements.py` (contains `GameEntity`)
        *   `prompt_to_game_engine/game_state.py` (contains `GameState`)
        *   `prompt_to_game_engine/game_engine.py` (contains `GameEngine`)

3.  **Define MCP Tools for the Game Engine (Conceptual):**
    *   **Status:** ✅ DONE
    *   **Deliverable:** Conceptual definition of tools:
        *   `get_sgd_schema()`
        *   `create_game(sgd_json_string)`
        *   `submit_player_action(game_id, action_key)`
        *   `get_game_state(game_id)`

4.  **Implement the Game Engine MCP-like Server (Python):**
    *   **Status:** ✅ DONE
    *   **Deliverable:** `prompt_to_game_engine/game_mcp_server.py` - A Flask-based server exposing the MCP tools as HTTP endpoints.

5.  **Update Project Dependencies:**
    *   **Status:** ✅ DONE
    *   **Deliverable:** Updated `pyproject.toml` with necessary dependencies (Flask, requests, openai, jsonschema). User to run `pip install -e .`.

---

## Phase 2: LLM-Powered Prompt-to-SGD Service

**Status:** 🟡 IN PROGRESS (Core logic implemented, testing pending by user)

**Goal:** Create a service that can take a user's natural language prompt and, using an LLM, convert it into a valid SGD JSON instance.

**Steps:**

1.  **Design and Implement `prompt_translator.py`:**
    *   **Status:** ✅ DONE (Initial version created)
    *   **Deliverable:** `prompt_to_game_engine/prompt_translator.py` - Module to:
        *   Fetch SGD schema from the Game MCP Server.
        *   Construct a prompt for an external LLM (e.g., OpenAI API) using the user's text and the SGD schema.
        *   Call the LLM API.
        *   Validate the LLM's JSON output against the SGD schema.
    *   **Note:** Requires `OPENAI_API_KEY` environment variable to be set by the user for testing.

2.  **Testing `prompt_translator.py`:**
    *   **Status:** ⏳ PENDING (User to test)
    *   **Action:** User needs to:
        1. Set `OPENAI_API_KEY`.
        2. Run `game_mcp_server.py`.
        3. Run `prompt_translator.py` to see if it successfully translates a sample prompt.

---

## Phase 3: Web UI for Interaction

**Status:** ⚪ NOT STARTED

**Goal:** Build a web interface where users can type prompts, see the generated game, and play it.

**Steps:**

1.  **Design Web UI Backend (Python Flask app):**
    *   **Status:** ⚪ NOT STARTED
    *   **Deliverable:** `prompt_to_game_engine/web_app.py` (or similar name).
    *   **Functionality:**
        *   Serve frontend static files.
        *   API Endpoint `/api/generate_and_load_game`:
            *   Accepts user's natural language prompt.
            *   Calls `PromptTranslatorService.translate_prompt_to_sgd()`.
            *   If successful, calls `create_game` MCP tool on the Game MCP Server.
            *   Returns `game_id` and initial game state to the frontend.
        *   API Endpoint `/api/game/<game_id>/action`:
            *   Accepts player action from frontend.
            *   Calls `submit_player_action` MCP tool.
            *   Returns new game state.
        *   API Endpoint `/api/game/<game_id>/state`: (Potentially for polling or refreshing state)
            *   Calls `get_game_state` MCP tool.
            *   Returns current game state.

2.  **Design Web UI Frontend (HTML, CSS, JavaScript):**
    *   **Status:** ⚪ NOT STARTED
    *   **Deliverables:** HTML, CSS, JS files within a `static` and `templates` structure for the `web_app.py`.
    *   **Functionality:**
        *   Text area for user to input game prompt.
        *   Button to submit prompt to `/api/generate_and_load_game`.
        *   Area to display the 2D game grid (e.g., using HTML table, Canvas, or divs).
        *   Input field/buttons for player to submit actions (e.g., text input for commands, or mapping keyboard events).
        *   Display area for game messages, score, status.

---

## Phase 4: Integration, Testing, and Iteration

**Status:** ⚪ NOT STARTED

**Goal:** Connect all pieces, test thoroughly, and plan for improvements.

**Steps:**

1.  **Integrate all components:** Ensure the Web UI, Prompt Translator, and Game MCP Server work together seamlessly.
2.  **End-to-end testing:** Test the full flow from a user typing a prompt to playing the generated game.
3.  **Refine and Iterate:**
    *   Improve SGD schema based on LLM generation capabilities and game complexity needs.
    *   Enhance LLM prompting techniques for better SGD generation.
    *   Add more features to the `GameEngine` (e.g., more complex rule evaluation, more entity properties).
    *   Improve the Web UI for better visualization and interaction.
    *   Add error handling and user feedback mechanisms.

---
Key:
- ✅ COMPLETED
- 🟡 IN PROGRESS
- ⏳ PENDING
- ⚪ NOT STARTED
