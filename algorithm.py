import heapq
import time


# ============================================================
# WAREHOUSE CONFIGURATION
# ============================================================
#
# 0 = free warehouse floor
# 1 = shelf / static obstacle
#
# S = START
# G = LOADING BAY / GOAL
#
# The layout is intentionally designed as a warehouse rather
# than using a completely open generic grid.
# ============================================================

GRID = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 1, 1, 1, 1, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
]

START = (0, 0)
GOAL = (9, 9)


# ============================================================
# MANHATTAN DISTANCE
# REQUIRED BY TRACK 1
# ============================================================

def manhattan_distance(a, b):
    """
    Manhattan distance between two grid cells.

    h(n) = |x1 - x2| + |y1 - y2|
    """

    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ============================================================
# POSITION VALIDATION
# ============================================================

def is_valid_position(position, grid):

    row, col = position

    # Outside warehouse
    if row < 0 or row >= len(grid):
        return False

    if col < 0 or col >= len(grid[0]):
        return False

    # Shelf
    if grid[row][col] == 1:
        return False

    return True


# ============================================================
# NEIGHBOUR GENERATION
# ============================================================

def get_neighbors(position, grid):

    row, col = position

    # Fixed order makes the demonstration reproducible.
    directions = [
        (-1, 0),   # UP
        (0, 1),    # RIGHT
        (1, 0),    # DOWN
        (0, -1)    # LEFT
    ]

    neighbors = []

    for dr, dc in directions:

        candidate = (
            row + dr,
            col + dc
        )

        if is_valid_position(candidate, grid):
            neighbors.append(candidate)

    return neighbors


# ============================================================
# WAREHOUSE-AWARE ANALYTICS
# ============================================================

def adjacent_obstacle_count(position, grid):

    """
    Counts shelves directly surrounding a cell.

    This does NOT change the A* cost or heuristic.

    It is used only for analysing the resulting route and
    making the agent's behaviour explainable.
    """

    row, col = position

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    count = 0

    for dr, dc in directions:

        neighbour = (
            row + dr,
            col + dc
        )

        neighbour_row, neighbour_col = neighbour

        if (
            0 <= neighbour_row < len(grid)
            and
            0 <= neighbour_col < len(grid[0])
        ):

            if grid[neighbour_row][neighbour_col] == 1:
                count += 1

    return count


# ============================================================
# PATH RECONSTRUCTION
# ============================================================

def reconstruct_path(came_from, current):

    path = [current]

    while current in came_from:

        current = came_from[current]

        path.append(current)

    path.reverse()

    return path


# ============================================================
# A* SEARCH
#
# Required formulation:
#
# f(n) = g(n) + h(n)
#
# h(n) = Manhattan Distance
#
# Novelty:
# We expose a detailed search trace without changing the
# required A* decision rule.
# ============================================================

def a_star(grid, start, goal):

    # --------------------------------------------------------
    # Priority queue
    #
    # (f-score, insertion-order, position)
    #
    # insertion-order makes tie handling deterministic.
    # --------------------------------------------------------

    open_set = []

    insertion_counter = 0

    start_h = manhattan_distance(
        start,
        goal
    )

    heapq.heappush(
        open_set,
        (
            start_h,
            insertion_counter,
            start
        )
    )

    # --------------------------------------------------------
    # Parent map
    # --------------------------------------------------------

    came_from = {}

    # --------------------------------------------------------
    # Cost from START to each node
    # --------------------------------------------------------

    g_score = {
        start: 0
    }

    # --------------------------------------------------------
    # Nodes already expanded
    # --------------------------------------------------------

    closed_set = set()

    # --------------------------------------------------------
    # NOVELTY:
    # Detailed search trace
    # --------------------------------------------------------

    search_trace = []

    # Number of nodes expanded
    expanded_nodes = 0

    # Number of candidate neighbours examined
    candidate_evaluations = 0

    # Start timing
    start_time = time.perf_counter()

    # ========================================================
    # MAIN A* LOOP
    # ========================================================

    while open_set:

        current_f, _, current = heapq.heappop(
            open_set
        )

        # Ignore duplicate queue entries
        if current in closed_set:
            continue

        # ----------------------------------------------------
        # Expand current node
        # ----------------------------------------------------

        closed_set.add(current)

        expanded_nodes += 1

        current_g = g_score[current]

        current_h = manhattan_distance(
            current,
            goal
        )

        # ----------------------------------------------------
        # Record expansion
        # ----------------------------------------------------

        expansion_record = {
            "step": expanded_nodes,
            "position": current,
            "g": current_g,
            "h": current_h,
            "f": current_g + current_h,
            "neighbors": []
        }

        # ----------------------------------------------------
        # Goal reached
        # ----------------------------------------------------

        if current == goal:

            path = reconstruct_path(
                came_from,
                current
            )

            path_cost = g_score[current]

            execution_time = (
                time.perf_counter() - start_time
            )

            return {
                "path": path,
                "path_cost": path_cost,
                "expanded_nodes": expanded_nodes,
                "candidate_evaluations": candidate_evaluations,
                "execution_time": execution_time,
                "search_trace": search_trace
            }

        # ----------------------------------------------------
        # Examine neighbours
        # ----------------------------------------------------

        for neighbor in get_neighbors(
            current,
            grid
        ):

            candidate_evaluations += 1

            tentative_g = current_g + 1

            neighbor_h = manhattan_distance(
                neighbor,
                goal
            )

            neighbor_f = (
                tentative_g +
                neighbor_h
            )

            # -----------------------------------------------
            # Record candidate information
            # -----------------------------------------------

            candidate_info = {
                "position": neighbor,
                "g": tentative_g,
                "h": neighbor_h,
                "f": neighbor_f
            }

            expansion_record[
                "neighbors"
            ].append(candidate_info)

            # -----------------------------------------------
            # Better route found
            # -----------------------------------------------

            if (
                neighbor not in g_score
                or
                tentative_g < g_score[neighbor]
            ):

                came_from[neighbor] = current

                g_score[neighbor] = tentative_g

                insertion_counter += 1

                heapq.heappush(
                    open_set,
                    (
                        neighbor_f,
                        insertion_counter,
                        neighbor
                    )
                )

        # Add completed expansion to trace
        search_trace.append(
            expansion_record
        )

    # ========================================================
    # NO PATH
    # ========================================================

    execution_time = (
        time.perf_counter() - start_time
    )

    return {
        "path": None,
        "path_cost": None,
        "expanded_nodes": expanded_nodes,
        "candidate_evaluations": candidate_evaluations,
        "execution_time": execution_time,
        "search_trace": search_trace
    }


# ============================================================
# ROUTE ANALYSIS
#
# This is an additional explainability layer.
# It does NOT modify A*.
# ============================================================

def analyse_route(path, grid):

    if not path:
        return {}

    obstacle_exposure = []

    for position in path:

        nearby_shelves = adjacent_obstacle_count(
            position,
            grid
        )

        obstacle_exposure.append(
            nearby_shelves
        )

    return {
        "route_length": len(path) - 1,
        "maximum_adjacent_shelves": max(
            obstacle_exposure
        ),
        "average_adjacent_shelves": (
            sum(obstacle_exposure)
            / len(obstacle_exposure)
        ),
        "high_exposure_cells": sum(
            1
            for value in obstacle_exposure
            if value >= 2
        )
    }


# ============================================================
# DISPLAY WAREHOUSE
# ============================================================

def display_grid(
    grid,
    path,
    start,
    goal,
    expanded_nodes=None
):

    path_set = set(path) if path else set()

    expanded_set = set()

    if expanded_nodes:

        for record in expanded_nodes:

            expanded_set.add(
                record["position"]
            )

    print("\nWAREHOUSE MAP")
    print()

    for row in range(len(grid)):

        line = ""

        for col in range(len(grid[0])):

            position = (row, col)

            if position == start:

                line += " S "

            elif position == goal:

                line += " G "

            elif position in path_set:

                line += " * "

            elif position in expanded_set:

                line += " + "

            elif grid[row][col] == 1:

                line += " # "

            else:

                line += " . "

        print(line)

    print()

    print("Legend:")
    print("S = Forklift start")
    print("G = Loading bay")
    print("# = Shelf")
    print("* = Optimal route")
    print("+ = Expanded by A*")


# ============================================================
# PRINT SEARCH TRACE
# ============================================================

def print_search_trace(search_trace):

    print("\nA* SEARCH TRACE")
    print("-" * 60)

    for record in search_trace:

        print(
            f"Step {record['step']:02d} | "
            f"Node {record['position']} | "
            f"g={record['g']} | "
            f"h={record['h']} | "
            f"f={record['f']}"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("WAREHOUSE LOGISTICS AGENT")
    print("EXPLAINABLE A* SEARCH")
    print("=" * 65)

    print("\nStart       :", START)
    print("Loading Bay :", GOAL)
    print("Heuristic   : Manhattan Distance")

    print("\nRunning A*...")

    result = a_star(
        GRID,
        START,
        GOAL
    )

    path = result["path"]

    if path is None:

        print("\nNo route to loading bay was found.")

    else:

        # ----------------------------------------------------
        # BASIC REQUIRED METRICS
        # ----------------------------------------------------

        print("\nROUTE FOUND")
        print("-" * 40)

        print(
            "Path Cost            :",
            result["path_cost"]
        )

        print(
            "Expanded Nodes        :",
            result["expanded_nodes"]
        )

        print(
            "Candidate Evaluations:",
            result["candidate_evaluations"]
        )

        print(
            "Execution Time       :",
            f"{result['execution_time']:.6f}",
            "seconds"
        )

        # ----------------------------------------------------
        # ROUTE ANALYSIS
        # ----------------------------------------------------

        analysis = analyse_route(
            path,
            GRID
        )

        print("\nROUTE ANALYSIS")
        print("-" * 40)

        print(
            "Route Length          :",
            analysis["route_length"]
        )

        print(
            "Maximum Shelf Exposure:",
            analysis["maximum_adjacent_shelves"]
        )

        print(
            "Average Shelf Exposure:",
            f"{analysis['average_adjacent_shelves']:.2f}"
        )

        print(
            "High-Exposure Cells   :",
            analysis["high_exposure_cells"]
        )

        # ----------------------------------------------------
        # PATH
        # ----------------------------------------------------

        print("\nOPTIMAL PATH")
        print("-" * 40)

        print(
            " -> ".join(
                str(position)
                for position in path
            )
        )

        # ----------------------------------------------------
        # SEARCH TRACE
        # ----------------------------------------------------

        print_search_trace(
            result["search_trace"]
        )

        # ----------------------------------------------------
        # WAREHOUSE VISUALIZATION
        # ----------------------------------------------------

        display_grid(
            GRID,
            path,
            START,
            GOAL,
            result["search_trace"]
        )