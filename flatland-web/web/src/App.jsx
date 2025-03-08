import React, { useState, useEffect, useRef } from 'react';
import './App.css';

// API endpoint configuration
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  // State
  const [description, setDescription] = useState('');
  const [styleGuidance, setStyleGuidance] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [environment, setEnvironment] = useState(null);
  const [state, setState] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // WebSocket
  const ws = useRef(null);
  
  // Canvas ref
  const canvasRef = useRef(null);
  
  // Handle WebSocket messages
  useEffect(() => {
    if (sessionId) {
      ws.current = new WebSocket(`ws://${API_URL.replace('http://', '')}/ws/${sessionId}`);
      
      ws.current.onopen = () => {
        console.log('WebSocket connected');
      };
      
      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'state_update') {
          setState(data.state);
          renderGrid(data.state);
        }
      };
      
      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
      };
      
      // Clean up
      return () => {
        if (ws.current) {
          ws.current.close();
        }
      };
    }
  }, [sessionId]);
  
  // Render grid on state change
  useEffect(() => {
    if (state && canvasRef.current) {
      renderGrid(state);
    }
  }, [state]);
  
  // Render grid on canvas
  const renderGrid = (state) => {
    const canvas = canvasRef.current;
    if (!canvas || !state.grid) return;
    
    const ctx = canvas.getContext('2d');
    const grid = state.grid;
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
        
        // Map cell values to colors (this would be customized based on environment)
        let color = '#ffffff';  // default: white
        
        if (cellValue === 0) color = '#f0f0f0';  // empty
        if (cellValue === 1) color = '#333333';  // wall
        
        // Check for entities at this position
        const entities = state.entities || [];
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
  };
  
  // Get entity color based on type
  const getEntityColor = (type) => {
    const colors = {
      player: '#3498db',
      box: '#e67e22',
      goal: '#2ecc71',
      enemy: '#e74c3c',
      default: '#9b59b6'
    };
    
    return colors[type.toLowerCase()] || colors.default;
  };
  
  // Get entity symbol based on type
  const getEntitySymbol = (type) => {
    const symbols = {
      player: '😀',
      box: '📦',
      goal: '🎯',
      enemy: '👾',
      default: '❓'
    };
    
    return symbols[type.toLowerCase()] || symbols.default;
  };
  
  // Generate environment from description
  const generateEnvironment = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description,
          style_guidance: styleGuidance,
          model: 'gpt-4-turbo-preview'  // Use latest available model
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate environment');
      }
      
      const data = await response.json();
      
      setSessionId(data.session_id);
      setEnvironment(data.environment);
      setState(data.state);
      
    } catch (err) {
      setError(err.message);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Process user input
  const handleInput = async (input) => {
    if (!sessionId) return;
    
    try {
      const response = await fetch(`${API_URL}/input`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          input_command: input
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to process input');
      }
      
      const data = await response.json();
      setState(data.state);
      
    } catch (err) {
      console.error(err);
    }
  };
  
  // Step simulation
  const stepSimulation = async () => {
    if (!sessionId) return;
    
    try {
      const response = await fetch(`${API_URL}/step?session_id=${sessionId}`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to step simulation');
      }
      
      const data = await response.json();
      setState(data.state);
      
    } catch (err) {
      console.error(err);
    }
  };
  
  // Keyboard input handler
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (!sessionId) return;
      
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
      
      const command = keyMap[event.key];
      if (command) {
        handleInput(command);
        event.preventDefault();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [sessionId]);
  
  return (
    <div className="app">
      <header>
        <h1>FlatLand Simulations</h1>
        <p>Create grid-based simulations using natural language</p>
      </header>
      
      <main>
        {!sessionId ? (
          <div className="generation-form">
            <div className="form-group">
              <label htmlFor="description">Describe your simulation:</label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g., Create a Sokoban game with a player, boxes, and target positions"
                rows={5}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="style">Style guidance (optional):</label>
              <input
                type="text"
                id="style"
                value={styleGuidance}
                onChange={(e) => setStyleGuidance(e.target.value)}
                placeholder="e.g., space theme, forest setting, etc."
              />
            </div>
            
            <button 
              onClick={generateEnvironment} 
              disabled={isLoading || !description.trim()}
              className="primary-button"
            >
              {isLoading ? 'Generating...' : 'Generate Simulation'}
            </button>
            
            {error && <div className="error">{error}</div>}
          </div>
        ) : (
          <div className="simulation">
            <div className="simulation-header">
              <h2>{environment?.metadata?.name || 'Simulation'}</h2>
              <p>{environment?.metadata?.description || ''}</p>
            </div>
            
            <div className="canvas-container">
              <canvas ref={canvasRef} />
            </div>
            
            <div className="controls">
              <div className="control-buttons">
                <button onClick={() => handleInput('up')} className="control-button">
                  ↑
                </button>
                <div className="horizontal-controls">
                  <button onClick={() => handleInput('left')} className="control-button">
                    ←
                  </button>
                  <button onClick={stepSimulation} className="control-button">
                    Step
                  </button>
                  <button onClick={() => handleInput('right')} className="control-button">
                    →
                  </button>
                </div>
                <button onClick={() => handleInput('down')} className="control-button">
                  ↓
                </button>
              </div>
            </div>
            
            <button 
              onClick={() => setSessionId(null)} 
              className="secondary-button"
            >
              Create New Simulation
            </button>
          </div>
        )}
      </main>
      
      <footer>
        <p>Powered by FlatLand and GPT-4</p>
      </footer>
    </div>
  );
}

export default App;