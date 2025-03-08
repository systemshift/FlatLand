"""
FlatLand Web API Backend

This module implements a FastAPI backend for the FlatLand library.
"""
from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json
import asyncio
import uuid

# FlatLand imports
from api.gpt_client import EnhancedEnvironmentGenerator
from flatland.logic_engine import LogicEngine
from flatland.state_manager import StateManager

# Models
class GenerationRequest(BaseModel):
    description: str
    style_guidance: Optional[str] = None
    model: str = "gpt-4-turbo-preview"  # Default to available model, will update to gpt-4.5 when available

class InputRequest(BaseModel):
    session_id: str
    input_command: str

class SessionState(BaseModel):
    session_id: str
    state: Dict
    history_index: int

# API app
app = FastAPI(title="FlatLand Web API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session storage
sessions = {}
active_connections = {}

# Dependencies
def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

@app.post("/generate")
async def generate_environment(request: GenerationRequest):
    """Generate a new environment from a text description using LLM"""
    try:
        # Initialize enhanced environment generator with the specified model
        generator = EnhancedEnvironmentGenerator()
        
        # Generate environment from description
        environment = generator.generate(
            description=request.description,
            style_guidance=request.style_guidance,
            model=request.model
        )
        
        # Create a new session
        session_id = str(uuid.uuid4())
        
        # Initialize LogicEngine and StateManager
        logic_engine = LogicEngine(environment)
        state_manager = StateManager(environment)
        
        # Store session data
        sessions[session_id] = {
            "environment": environment,
            "logic_engine": logic_engine,
            "state_manager": state_manager
        }
        
        # Return initial state and session ID
        return {
            "session_id": session_id,
            "environment": environment,
            "state": state_manager.current_state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/input")
async def process_input(request: InputRequest, session=Depends(get_session)):
    """Process user input for a simulation"""
    try:
        logic_engine = session["logic_engine"]
        state_manager = session["state_manager"]
        
        # Process input
        result = logic_engine.process_input(request.input_command)
        
        # Update connected clients
        if request.session_id in active_connections:
            await active_connections[request.session_id].send_json({
                "type": "state_update",
                "state": state_manager.current_state
            })
        
        return {
            "success": True,
            "state": state_manager.current_state,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step")
async def step_simulation(session_id: str, session=Depends(get_session)):
    """Process a single step in the simulation"""
    try:
        logic_engine = session["logic_engine"]
        state_manager = session["state_manager"]
        
        # Process step
        result = logic_engine.step()
        
        # Update connected clients
        if session_id in active_connections:
            await active_connections[session_id].send_json({
                "type": "state_update",
                "state": state_manager.current_state
            })
            
        return {
            "success": True,
            "state": state_manager.current_state,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state/{session_id}")
async def get_state(session_id: str, session=Depends(get_session)):
    """Get the current state of a simulation"""
    state_manager = session["state_manager"]
    return {
        "state": state_manager.current_state,
        "environment": session["environment"]
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    
    # Register connection
    active_connections[session_id] = websocket
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # Process commands sent via WebSocket
            if data.startswith("input:"):
                command = data[6:]
                session = sessions.get(session_id)
                if session:
                    result = session["logic_engine"].process_input(command)
                    await websocket.send_json({
                        "type": "state_update",
                        "state": session["state_manager"].current_state,
                        "result": result
                    })
    except Exception:
        # Remove connection on disconnect
        if session_id in active_connections:
            del active_connections[session_id]