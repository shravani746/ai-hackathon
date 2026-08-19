"""Warehouse configuration for the visualizer.

The actual Track 1 A* implementation remains in algorithm.py.
This file re-exports the exact same configuration so the GUI and algorithm
cannot accidentally use different maps.
"""

from algorithm import GRID, START, GOAL
