// FlatLand Web Application

// Global state
let state = {
    sessionId: null,
    environment: null,
    currentState: null,
};

// DOM Elements
const elements = {
    generationForm: document.getElementById('generation-form'),
    description: document.getElementById('description'),
    style: document.getElementById('style'),
    generateBtn: document.getElementById('generate-btn'),
    error: document.getElementById('error'),
    loading: document.getElementById('loading'),
    simulation: document.getElementById('simulation'),
    simulationName: document.getElementById('simulation-name'),
    simulationDescription: document.getElementById('simulation-description'),
    canvas: document.getElementById('grid-canvas'),
    stepBtn: document.getElementById('step-btn'),
    newSimulationBtn: document.getElementById('new-simulation-btn'),
    controlButtons: document.querySelectorAll('[data-direction]'),
};

// Initialize the application
function init() {
    // Set up event listeners
    elements.generateBtn.addEventListener('click', generateEnvironment);
    elements.stepBtn.addEventListener('click', stepSimulation);
    elements.newSimulationBtn.addEventListener('click', resetSimulation);
    
    // Set up control buttons
    elements.controlButtons.forEach(button => {
        button.addEventListener('click', () => {
            const direction = button.getAttribute('data-direction');
            handleInput(direction);
        });
    });
    
    // Set up keyboard controls
    document.addEventListener('keydown', handleKeyDown);
}

// Generate environment from description
async function generateEnvironment() {
    const description = elements.description.value.trim();
    const style = elements.style.value.trim();
    
    if (!description) {
        showError('Please enter a description');
        return;
    }
    
    try {
        showLoading(true);
        hideError();
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                description,
                style_guidance: style,
                model: 'gpt-4-turbo-preview' // Use latest available model
            }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to generate environment');
        }
        
        const data = await response.json();
        
        // Update state
        state.sessionId = data.session_id;
        state.environment = data.environment;
        state.currentState = data.state;
        
        // Update UI
        showSimulation();
        renderGrid();
        
    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

// Process user input
async function handleInput(direction) {
    if (!state.sessionId) return;
    
    try {
        const response = await fetch('/api/input', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: state.sessionId,
                input_command: direction
            }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to process input');
        }
        
        const data = await response.json();
        
        // Update state
        state.currentState = data.state;
        
        // Update UI
        renderGrid();
        
    } catch (error) {
        console.error(error);
    }
}

// Step simulation
async function stepSimulation() {
    if (!state.sessionId) return;
    
    try {
        const response = await fetch('/api/step', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: state.sessionId
            }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to step simulation');
        }
        
        const data = await response.json();
        
        // Update state
        state.currentState = data.state;
        
        // Update UI
        renderGrid();
        
    } catch (error) {
        console.error(error);
    }
}

// Render grid on canvas
function renderGrid() {
    const canvas = elements.canvas;
    const ctx = canvas.getContext('2d');
    const grid = state.currentState.grid;
    const cellSize = 30;
    
    // Set canvas size
    canvas.width = grid[0].length * cellSize;
    canvas.height = grid.length * cellSize;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid cells
    for (let y = 0; y < grid.length; y++) {
        for (let x = 0; x < grid[y].length; x++) {
            const cellValue = grid[y][x];
            
            // Map cell values to colors
            let color = '#ffffff';  // default: white
            
            if (cellValue === 0) color = '#f0f0f0';  // empty
            if (cellValue === 1) color = '#333333';  // wall
            
            // Check for entities at this position
            const entities = state.currentState.entities || [];
            const entity = entities.find(e => e.position[0] === y && e.position[1] === x);
            
            if (entity) {
                // Use entity color or default
                color = entity.color || getEntityColor(entity.type);
            }
            
            // Draw cell
            ctx.fillStyle = color;
            ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
            
            // Draw border
            ctx.strokeStyle = '#cccccc';
            ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
            
            // If there's an entity, draw a symbol
            if (entity) {
                ctx.fillStyle = '#000000';
                ctx.font = '20px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(getEntitySymbol(entity.type), 
                           x * cellSize + cellSize/2, 
                           y * cellSize + cellSize/2);
            }
        }
    }
}

// Get entity color based on type
function getEntityColor(type) {
    type = type.toLowerCase();
    const colors = {
        player: '#3498db',
        box: '#e67e22',
        goal: '#2ecc71',
        enemy: '#e74c3c',
        default: '#9b59b6'
    };
    
    return colors[type] || colors.default;
}

// Get entity symbol based on type
function getEntitySymbol(type) {
    type = type.toLowerCase();
    const symbols = {
        player: '😀',
        box: '📦',
        goal: '🎯',
        enemy: '👾',
        default: '❓'
    };
    
    return symbols[type] || symbols.default;
}

// Handle keyboard input
function handleKeyDown(event) {
    if (!state.sessionId) return;
    
    const keyMap = {
        'ArrowUp': 'up',
        'ArrowDown': 'down',
        'ArrowLeft': 'left',
        'ArrowRight': 'right',
        'w': 'up',
        's': 'down',
        'a': 'left',
        'd': 'right',
        ' ': 'space'
    };
    
    const direction = keyMap[event.key];
    if (direction) {
        handleInput(direction);
        event.preventDefault();
    }
}

// Reset to create a new simulation
function resetSimulation() {
    state = {
        sessionId: null,
        environment: null,
        currentState: null,
    };
    
    hideSimulation();
}

// UI Helper Functions
function showError(message) {
    elements.error.textContent = message;
    elements.error.style.display = 'block';
}

function hideError() {
    elements.error.style.display = 'none';
}

function showLoading(isLoading) {
    elements.loading.style.display = isLoading ? 'block' : 'none';
    elements.generateBtn.disabled = isLoading;
}

function showSimulation() {
    elements.generationForm.style.display = 'none';
    elements.simulation.style.display = 'block';
    
    // Update simulation metadata
    if (state.environment && state.environment.metadata) {
        elements.simulationName.textContent = state.environment.metadata.name || 'Simulation';
        elements.simulationDescription.textContent = state.environment.metadata.description || '';
    }
}

function hideSimulation() {
    elements.simulation.style.display = 'none';
    elements.generationForm.style.display = 'block';
}

// Initialize the application when the DOM is ready
document.addEventListener('DOMContentLoaded', init);