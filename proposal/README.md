# FlatLand Web Application

A web application wrapper for the FlatLand library that allows users to create, visualize, and interact with grid-based simulations using natural language.

## Overview

This application extends the FlatLand library by providing:

1. A web-based interface for creating grid simulations through natural language
2. Real-time visualization and interaction with the simulations
3. Integration with GPT-4.5 for improved environment generation

## Architecture

The application consists of:

- **Backend API**: FastAPI service that wraps the FlatLand library
- **Frontend UI**: React application with canvas-based grid visualization
- **LLM Integration**: Enhanced client for GPT-4.5 API

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- OpenAI API key
- Docker and Docker Compose (optional for containerized deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/flatland-web.git
   cd flatland-web
   ```

2. Set up environment variables:
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

3. Install dependencies:
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   cd web
   npm install
   ```

### Running Locally

1. Start the backend server:
   ```bash
   uvicorn api.main:app --reload
   ```

2. Start the frontend development server:
   ```bash
   cd web
   npm start
   ```

3. Open your browser and navigate to http://localhost:3000

### Using Docker

1. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

2. Open your browser and navigate to http://localhost:3000

## Usage

1. Enter a natural language description of your desired simulation
2. Optionally provide style guidance
3. Click "Generate Simulation"
4. Interact with the simulation using keyboard arrows or on-screen controls

## Example Descriptions

Try these example descriptions:

- "Create a Sokoban puzzle where the player needs to push boxes onto target locations"
- "Design a Snake game where the snake grows when it eats food"
- "Make a simple maze where the player has to reach the exit while avoiding enemies"
- "Create a cellular automaton that follows Conway's Game of Life rules"

## Development

### Project Structure

```
flatland-web/
├── api/             # Backend FastAPI code
├── src/             # FlatLand library source
├── web/             # Frontend React application
├── Dockerfile.api   # Backend Docker config
├── Dockerfile.web   # Frontend Docker config
├── docker-compose.yml  # Docker Compose config
└── requirements.txt # Python dependencies
```

### Extending the Application

- **Adding new simulation features**: Extend the FlatLand library in the src directory
- **Improving visualization**: Modify the frontend canvas rendering
- **Enhancing LLM integration**: Update the GPT-4.5 client

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FlatLand library creators
- OpenAI for the GPT API