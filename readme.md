# FlatLand 🗺️

**A Minimalist, Constraint-Driven 2D Framework for Testing LLM-Generated Environments**  
*"Can your LLM build NetHack?"*

[![PyPI Version](https://img.shields.io/pypi/v/flatland.svg)](https://pypi.org/project/flatland/)
[![Tests](https://github.com/systemshift/flatland/actions/workflows/tests.yml/badge.svg)](https://github.com/yourusername/flatland/actions)

![](docs/demo.gif)  
*Example: LLM-generated dungeon with physics constraints*

## Quick Example

```python
from flatland import FlatLand, tasks

# Ask an LLM to generate a dungeon
llm_response = tasks.generate(
    prompt="A maze with locked doors and keys",
    constraints={"inventory_size": 2, "movement": "cardinal"}
)

# Validate and run
world = FlatLand.from_code(llm_response.code)
world.simulate(steps=100)
print(world.evaluate())  # Metrics: constraints obeyed? goal achieved?
```

## Key Features

- 🧱 **Constraint-First Design**: Enforce physics, inventory limits, or movement rules to test LLM reasoning
- ⚡ **Blazing Fast**: NumPy-backed grid engine handles 10M+ cell updates/sec
- 🤖 **LLM-Friendly**: Tools for Gemini/GPT/Claude to generate valid environments via function calling
- 🧪 **Testing Suite**: Prebuilt evaluation metrics for LLM-generated environments (goal completion, rule violations)
- 🕹️ **NetHack-Inspired**: Built-in templates for roguelike dungeons, cellular automata, and grid-based games

## Installation

```bash
pip install flatland
```

## Basic Usage

### 1. Define Constraints

```python
from flatland import ConstraintEngine

engine = ConstraintEngine(
    movement="cardinal",  # Disallow diagonal movement
    inventory_size=3,     # Max 3 items
    max_agents=1          # Single-agent environments only
)
```

### 2. Generate Environments

```python
from flatland import tasks

# Let an LLM create a dungeon
response = tasks.generate(
    prompt="A lava puzzle where agents must push blocks to cross",
    constraints=engine,
    llm="gemini-pro"  # or "gpt-4", "claude-3"
)

# Run the generated environment
world = response.to_world()
world.step()  # Advance simulation
```

### 3. Evaluate LLM Performance

```python
metrics = world.evaluate(
    success_conditions=["player reached exit", "no lava damage"],
    failure_conditions=["agent died", "constraint_violations > 0"]
)
print(metrics.success)  # True/False
```

## LLM Integration

### With LangChain

```python
from langchain_flatland import FlatLandToolkit

tools = FlatLandToolkit(constraints=engine).get_tools()
agent = initialize_llm_agent(tools, llm=ChatOpenAI())
agent.run("Create a dungeon where water freezes enemies on contact")
```

### With OpenAI Function Calling

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Build a zombie survival game..."}],
    tools=flatland_tools  # Predefined schema for FlatLand actions
)
```

## Advanced Usage

### Custom Constraints

```python
# Add a "no flying" rule
engine.add_constraint(
    name="anti_gravity",
    validator=lambda world, agent: agent.y_velocity <= 0,
    error="Agents cannot fly!"
)
```

### Multi-Agent Testing

```python
world = FlatLand(grid_size=(50, 50))
world.add_agent(Agent(strategy="llm-generated"))  # LLM-controlled
world.add_agent(Agent(strategy="random"))         # Baseline opponent
world.simulate(steps=1000)  # Battle royale!
```

## Evaluation Metrics

| Metric | Description |
|--------|-------------|
| constraint_violations | Times LLM broke rules (e.g., moved through walls) |
| goal_completion | % of requested features implemented |
| step_efficiency | Actions taken vs optimal solution |
| playability | FPS/stability under load (stress test) |

## Contributing

1. Clone: `git clone https://github.com/systemshift/flatland.git`
2. Install dev deps: `pip install -e .[dev]`
3. Run tests: `pytest tests/`

See CONTRIBUTING.md for details.

## Roadmap

- Visual Editor: GUI for designing constraint templates
- Benchmarks: LLM leaderboards for environment generation
- Gym Integration: RL-ready environments via flatland-gym

## Inspired By

- NetHack (Complexity within constraints)
- Griddly (Grid-based RL)
- LangChain (LLM tooling)

