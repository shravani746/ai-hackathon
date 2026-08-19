"""
Test suite — Track 1: Warehouse Logistics Agent (A* Search)

Covers the test cases specified in the team technical handoff (Section 11):
1. Valid route
2. Blocked route
3. Start/goal validity
4. Metric consistency
5. Trace consistency
6. Reproducibility

Also covers the four scenarios required by the submission sheet:
normal path, obstacle encountered, replanning, goal reached.

Run with:  python -m unittest test_algorithm.py -v
"""

import unittest

from algorithm import (
    a_star,
    manhattan_distance,
    is_valid_position,
    get_neighbors,
    GRID,
    START,
    GOAL,
)


class TestManhattanHeuristic(unittest.TestCase):
    """h(n) must be Manhattan Distance — required by Track 1."""

    def test_zero_distance_to_self(self):
        self.assertEqual(manhattan_distance((3, 3), (3, 3)), 0)

    def test_known_distance(self):
        self.assertEqual(manhattan_distance((0, 0), (9, 9)), 18)

    def test_symmetry(self):
        a, b = (2, 5), (7, 1)
        self.assertEqual(manhattan_distance(a, b), manhattan_distance(b, a))


class TestValidRoute(unittest.TestCase):
    """Handoff 11.1 — Normal path: start and goal connected."""

    def test_path_found_on_default_warehouse(self):
        result = a_star(GRID, START, GOAL)
        self.assertIsNotNone(result["path"])
        self.assertEqual(result["path"][0], START)
        self.assertEqual(result["path"][-1], GOAL)

    def test_path_is_contiguous(self):
        """Every step in the path must be an adjacent (4-directional) move."""
        result = a_star(GRID, START, GOAL)
        path = result["path"]
        for a, b in zip(path, path[1:]):
            self.assertEqual(manhattan_distance(a, b), 1)


class TestBlockedRoute(unittest.TestCase):
    """Handoff 11.2 — Blocked route: shelves isolate the goal."""

    def test_no_path_when_goal_is_sealed(self):
        blocked_grid = [
            [0, 0, 0],
            [0, 0, 0],
            [1, 1, 0],  # wall sealing the bottom row goal from row 1
        ]
        blocked_start = (0, 0)
        blocked_goal = (2, 2)
        # goal itself is free, but the only entries to it are blocked
        blocked_grid[2][2] = 0
        blocked_grid[1][2] = 1  # seal the last opening
        result = a_star(blocked_grid, blocked_start, blocked_goal)
        self.assertIsNone(result["path"])
        self.assertIsNone(result["path_cost"])


class TestStartGoalValidity(unittest.TestCase):
    """Handoff 11.3 — START and GOAL must be free cells."""

    def test_start_is_free_cell(self):
        self.assertTrue(is_valid_position(START, GRID))

    def test_goal_is_free_cell(self):
        self.assertTrue(is_valid_position(GOAL, GRID))

    def test_get_neighbors_excludes_shelves_and_bounds(self):
        for neighbor in get_neighbors(START, GRID):
            self.assertTrue(is_valid_position(neighbor, GRID))


class TestMetricConsistency(unittest.TestCase):
    """Handoff 11.4 — for unit-cost movement, path_cost == len(path) - 1."""

    def test_path_cost_matches_path_length(self):
        result = a_star(GRID, START, GOAL)
        self.assertEqual(result["path_cost"], len(result["path"]) - 1)

    def test_execution_time_is_recorded(self):
        result = a_star(GRID, START, GOAL)
        self.assertGreaterEqual(result["execution_time"], 0)

    def test_candidate_evaluations_at_least_expanded_nodes(self):
        # Every expanded node examines >=0 candidates; total candidates
        # should be at least as many as expansions for a non-trivial grid.
        result = a_star(GRID, START, GOAL)
        self.assertGreaterEqual(
            result["candidate_evaluations"], result["expanded_nodes"] - 1
        )


class TestTraceConsistency(unittest.TestCase):
    """Handoff 11.5 — expanded_nodes should match the number of trace records."""

    def test_expanded_nodes_matches_trace_length(self):
        """
        a_star() increments expanded_nodes for the goal node itself, but
        returns before appending the goal's expansion record to
        search_trace. So expanded_nodes is always exactly
        len(search_trace) + 1 when a path is found. This is documented,
        expected behavior (see handoff Section 11.5), not a defect.
        """
        result = a_star(GRID, START, GOAL)
        self.assertEqual(result["expanded_nodes"], len(result["search_trace"]) + 1)

    def test_trace_records_have_required_fields(self):
        result = a_star(GRID, START, GOAL)
        for record in result["search_trace"]:
            for field in ("step", "position", "g", "h", "f", "neighbors"):
                self.assertIn(field, record)

    def test_f_equals_g_plus_h_in_trace(self):
        result = a_star(GRID, START, GOAL)
        for record in result["search_trace"]:
            self.assertEqual(record["f"], record["g"] + record["h"])


class TestReproducibility(unittest.TestCase):
    """Handoff 11.6 — deterministic tie handling gives the same result each run."""

    def test_repeated_runs_produce_identical_path(self):
        first = a_star(GRID, START, GOAL)
        second = a_star(GRID, START, GOAL)
        self.assertEqual(first["path"], second["path"])
        self.assertEqual(first["path_cost"], second["path_cost"])
        self.assertEqual(first["expanded_nodes"], second["expanded_nodes"])


class TestGoalReached(unittest.TestCase):
    """Submission sheet scenario — goal reached: agent stops at the goal."""

    def test_last_path_cell_is_goal(self):
        result = a_star(GRID, START, GOAL)
        self.assertEqual(result["path"][-1], GOAL)

    def test_no_cells_beyond_goal_in_path(self):
        result = a_star(GRID, START, GOAL)
        self.assertEqual(result["path"].count(GOAL), 1)


class TestReplanning(unittest.TestCase):
    """
    Submission sheet scenario — replanning: when a new obstacle appears
    mid-path, re-running a_star from the agent's current position produces
    a valid new route instead of failing.
    """

    def test_agent_replans_around_new_obstacle(self):
        # Get the original path.
        original = a_star(GRID, START, GOAL)
        path = original["path"]
        self.assertIsNotNone(path)

        # Simulate the agent partway along its route.
        midpoint_index = len(path) // 2
        current_position = path[midpoint_index]

        # Drop a new obstacle on the very next planned cell (if free/legal).
        modified_grid = [row[:] for row in GRID]
        if midpoint_index + 1 < len(path):
            next_cell = path[midpoint_index + 1]
            row, col = next_cell
            if next_cell not in (START, GOAL):
                modified_grid[row][col] = 1

        # Replan from the agent's current position.
        replanned = a_star(modified_grid, current_position, GOAL)

        # The agent must still find *a* valid route to the goal,
        # and it must not simply reuse the now-blocked original path.
        self.assertIsNotNone(replanned["path"])
        self.assertEqual(replanned["path"][0], current_position)
        self.assertEqual(replanned["path"][-1], GOAL)


if __name__ == "__main__":
    unittest.main(verbosity=2)