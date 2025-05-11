document.addEventListener('DOMContentLoaded', () => {
    const envSelect = document.getElementById('env-select');
    const loadEnvBtn = document.getElementById('load-env-btn');
    const commandInputField = document.getElementById('command-input-field');
    const submitCommandBtn = document.getElementById('submit-command-btn');
    const stateDisplay = document.getElementById('state-display');
    const resultDisplay = document.getElementById('result-display');
    const logMessages = document.getElementById('log-messages');
    const currentEnvNameDisplay = document.getElementById('current-env-name');

    function logMessage(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        logMessages.textContent = `[${timestamp}] [${type.toUpperCase()}] ${message}\n` + logMessages.textContent;
    }

    function displayState(state) {
        if (state && state.grid && state.grid.cells) {
            let gridStr = "Grid:\n";
            state.grid.cells.forEach(row => {
                gridStr += row.map(cell => {
                    // Simple representation, can be enhanced
                    if (cell === 0) return "."; // Empty
                    if (cell === 1) return "#"; // Wall
                    if (cell === 2) return "P"; // Player (example)
                    if (cell === 3) return "B"; // Box (example)
                    if (cell === 4) return "G"; // Goal (example)
                    return String(cell);
                }).join(" ") + "\n";
            });
            gridStr += "\nEntities:\n";
            if (state.entities) {
                state.entities.forEach(entity => {
                    gridStr += `- ID: ${entity.id}, Type: ${entity.type}, Pos: [${entity.position.join(', ')}]\n`;
                });
            }
            stateDisplay.textContent = gridStr;
        } else {
            stateDisplay.textContent = JSON.stringify(state, null, 2);
        }
    }

    async function loadEnvironment(envName) {
        logMessage(`Loading environment: ${envName}...`);
        try {
            const response = await fetch('/api/load_environment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ environment_name: envName }),
            });
            const data = await response.json();
            if (data.success) {
                logMessage(`Environment '${data.environment_name}' loaded successfully.`);
                currentEnvNameDisplay.textContent = data.environment_name;
                displayState(data.initial_state);
                resultDisplay.textContent = "Environment loaded. Ready for commands.";
            } else {
                logMessage(`Error loading environment: ${data.message}`, 'error');
                currentEnvNameDisplay.textContent = "Error";
                resultDisplay.textContent = `Error: ${data.message}`;
            }
        } catch (error) {
            logMessage(`Network or server error: ${error.message}`, 'error');
            resultDisplay.textContent = `Error: ${error.message}`;
        }
    }

    async function submitCommand() {
        const command = commandInputField.value.trim();
        if (!command) {
            logMessage('Command cannot be empty.', 'warn');
            return;
        }
        logMessage(`Submitting command: ${command}`);
        try {
            const response = await fetch('/api/process_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command: command }),
            });
            const data = await response.json();
            if (data.success && data.result) {
                logMessage(`Command '${command}' processed.`);
                displayState(data.result.state); // Assuming result contains the new state
                resultDisplay.textContent = "Changes:\n" + JSON.stringify(data.result.changes, null, 2) +
                                           "\nMessage: " + (data.result.message || "None");
            } else {
                logMessage(`Error processing command: ${data.message}`, 'error');
                resultDisplay.textContent = `Error: ${data.message}`;
            }
        } catch (error) {
            logMessage(`Network or server error: ${error.message}`, 'error');
            resultDisplay.textContent = `Error: ${error.message}`;
        }
        commandInputField.value = ''; // Clear input field
    }

    loadEnvBtn.addEventListener('click', () => {
        const selectedEnv = envSelect.value;
        loadEnvironment(selectedEnv);
    });

    submitCommandBtn.addEventListener('click', submitCommand);
    commandInputField.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            submitCommand();
        }
    });

    // Automatically load the default environment on page load
    logMessage("Page loaded. Attempting to load default environment...");
    loadEnvironment(envSelect.value); // Load the initially selected environment
});
