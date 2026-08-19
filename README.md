# AI Express Hackathon - Track 1

## Warehouse Logistics Agent

A Python implementation of A* Search using Manhattan Distance for a warehouse forklift navigating around static shelf obstacles.

### Files

- `algorithm.py` - A* Search, Manhattan heuristic, path reconstruction, metrics, search trace.
- `environment.py` - Warehouse grid, start and goal.
- `main.py` - Tkinter visualization, forklift animation, and metrics display.

### Requirements

- Python 3.x
- Tkinter (normally included with the standard Windows Python installation)

No third-party packages are required.

### Run

Open Command Prompt in this folder:

```bash
python main.py
```

### Demonstration

The application:
1. Runs A* using Manhattan Distance.
2. Records expanded nodes and path cost.
3. Displays the warehouse grid.
4. Shows the optimal route.
5. Animates the forklift step-by-step to the loading bay.
6. Displays path cost, expanded nodes, and execution time.

Track 1 requirement: A* Search with Manhattan Distance.
