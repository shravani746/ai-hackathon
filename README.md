# AI Express Hackathon - Track 1 FINAL

## Warehouse Logistics Agent

**Algorithm:** A* Search  
**Heuristic:** Manhattan Distance  
**Environment:** 10x10 warehouse with static shelf obstacles  
**GUI:** Python Tkinter

### Files

- `algorithm.py` — supplied Track 1 A* implementation.
- `environment.py` — re-exports the exact grid/start/goal used by the algorithm.
- `main.py` — interactive Tkinter visualizer and forklift animation.
- `run.bat` — one-click Windows launcher.

### How to run

1. Extract this folder.
2. Keep all Python files together.
3. Double-click `run.bat`.

Or open Command Prompt in the folder and run:

```text
python main.py
```

No third-party Python packages are required.

### Controls

- **RUN A*** — calculate the path and start the demonstration.
- **PAUSE** — pause the forklift.
- **RESUME** — continue.
- **RESET** — return to the starting state.
- **Animation speed** — control how quickly the forklift moves.

### What the demo shows

- Start and goal
- Static shelves
- A* expanded nodes
- Optimal path
- Autonomous forklift movement
- Path cost
- Expanded-node count
- Execution time
