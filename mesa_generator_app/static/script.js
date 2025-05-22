document.addEventListener('DOMContentLoaded', () => {
    const mesaForm = document.getElementById('mesa-form');
    const promptInput = document.getElementById('prompt-input');
    const stepsInput = document.getElementById('steps-input');
    const agentsInput = document.getElementById('agents-input');
    const submitButton = document.getElementById('submit-button');
    
    const statusMessageEl = document.getElementById('status-message');
    const errorOutputEl = document.getElementById('error-output');
    const codePreviewEl = document.getElementById('code-preview');
    const resultsOutputEl = document.getElementById('results-output');

    mesaForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        const userPrompt = promptInput.value.trim();
        const stepsToRun = parseInt(stepsInput.value, 10);
        const numAgentsN = parseInt(agentsInput.value, 10);

        if (!userPrompt) {
            errorOutputEl.textContent = 'Please enter a simulation prompt.';
            errorOutputEl.style.display = 'block';
            return;
        }

        // Clear previous results and errors
        statusMessageEl.textContent = 'Processing... Please wait.';
        statusMessageEl.style.display = 'block';
        errorOutputEl.textContent = '';
        errorOutputEl.style.display = 'none';
        codePreviewEl.textContent = '';
        resultsOutputEl.textContent = '';
        submitButton.disabled = true;

        const payload = {
            prompt: userPrompt,
            steps_to_run: stepsToRun,
            model_params: { N: numAgentsN }
            // We can extend model_params if more are added to the UI
        };

        try {
            const response = await fetch('/generate_mesa', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            statusMessageEl.textContent = 'Request complete. Processing response...';
            const data = await response.json();

            if (!response.ok) {
                // Handle HTTP errors (e.g., 400, 500)
                let errorMessage = `Error: ${response.status} ${response.statusText}`;
                if (data && data.error) {
                    errorMessage += ` - ${data.error}`;
                    if (data.details) {
                        errorMessage += `\nDetails: ${data.details}`;
                    }
                }
                throw new Error(errorMessage);
            }
            
            // Display results
            if (data.generated_code_preview) {
                codePreviewEl.textContent = data.generated_code_preview.join('\n');
            }
            if (data.simulation_output) {
                resultsOutputEl.textContent = data.simulation_output;
            }
            if (data.simulation_error) {
                errorOutputEl.textContent = `Simulation Error: ${data.simulation_error}`;
                errorOutputEl.style.display = 'block';
            } else if (!data.simulation_success) {
                errorOutputEl.textContent = 'Simulation did not complete successfully (no specific error provided).';
                errorOutputEl.style.display = 'block';
            }

            statusMessageEl.textContent = data.message || 'Done.';
            // Keep status message visible for a bit or hide it
            // setTimeout(() => { statusMessageEl.style.display = 'none'; }, 5000);


        } catch (error) {
            console.error('Fetch error:', error);
            errorOutputEl.textContent = `Failed to communicate with the server: ${error.message}`;
            errorOutputEl.style.display = 'block';
            statusMessageEl.textContent = 'Error occurred.';
        } finally {
            submitButton.disabled = false;
        }
    });
});
