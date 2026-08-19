# main.py
# AI Express Hackathon - Track 1
# Sudhir's visual integration layer.
#
# Uses the supplied algorithm.py as the A* service.
# It does not reimplement or modify A*.

import tkinter as tk
from algorithm import a_star
from environment import GRID, START, GOAL

CELL = 58
MOVE_DELAY = 220

FREE = "#F7F7F7"
SHELF = "#444444"
GRID_LINE = "#B8B8B8"
START_FILL = "#2E8B57"
GOAL_FILL = "#D9534F"
PATH_FILL = "#9BDCF5"
EXPANDED_FILL = "#E9E9E9"
AGENT_FILL = "#1557A6"
TEXT = "#202020"


class WarehouseApp:
    def __init__(self, root, result):
        self.root = root
        self.result = result
        self.path = result["path"] or []
        self.agent_item = None
        self.agent_text = None

        rows = len(GRID)
        cols = len(GRID[0])

        root.title("AI Express - Track 1 Warehouse Logistics Agent")
        root.resizable(False, False)

        tk.Label(
            root,
            text="WAREHOUSE LOGISTICS AGENT",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(10, 0))

        tk.Label(
            root,
            text="A* Search + Manhattan Distance",
            font=("Segoe UI", 11),
        ).pack(pady=(0, 8))

        self.canvas = tk.Canvas(
            root,
            width=cols * CELL,
            height=rows * CELL,
            bg="white",
            highlightthickness=0,
        )
        self.canvas.pack(padx=12)

        legend = tk.Frame(root)
        legend.pack(pady=7)

        for label, fill in [
            ("Shelf", SHELF),
            ("Expanded", EXPANDED_FILL),
            ("Optimal Path", PATH_FILL),
            ("Forklift", AGENT_FILL),
        ]:
            tk.Label(
                legend,
                text=f"  {label}  ",
                bg=fill,
                fg="white" if fill == SHELF or fill == AGENT_FILL else TEXT,
                padx=4,
                pady=2,
            ).pack(side="left", padx=3)

        self.metrics = tk.Label(
            root,
            text="",
            font=("Consolas", 10),
            justify="left",
            anchor="w",
        )
        self.metrics.pack(fill="x", padx=12, pady=(0, 10))

        self.draw_warehouse()
        self.draw_search_result()

        if self.path:
            self.root.after(900, lambda: self.animate(0))
        else:
            self.metrics.config(text="NO ROUTE FOUND")

    def center(self, pos):
        r, c = pos
        return c * CELL + CELL // 2, r * CELL + CELL // 2

    def draw_warehouse(self):
        for r in range(len(GRID)):
            for c in range(len(GRID[0])):
                fill = SHELF if GRID[r][c] == 1 else FREE
                self.canvas.create_rectangle(
                    c * CELL,
                    r * CELL,
                    (c + 1) * CELL,
                    (r + 1) * CELL,
                    fill=fill,
                    outline=GRID_LINE,
                )

        self.mark(self.result_start, "S", START_FILL)
        self.mark(self.result_goal, "G", GOAL_FILL)

    @property
    def result_start(self):
        return START

    @property
    def result_goal(self):
        return GOAL

    def mark(self, pos, label, fill):
        r, c = pos
        self.canvas.create_rectangle(
            c * CELL + 4,
            r * CELL + 4,
            (c + 1) * CELL - 4,
            (r + 1) * CELL - 4,
            fill=fill,
            outline=fill,
        )
        x, y = self.center(pos)
        self.canvas.create_text(
            x, y, text=label, fill="white",
            font=("Segoe UI", 15, "bold"),
        )

    def draw_search_result(self):
        # Expanded nodes: shown underneath the final path.
        for record in self.result.get("search_trace", []):
            pos = record["position"]
            if pos in (START, GOAL):
                continue
            r, c = pos
            if GRID[r][c] == 1:
                continue
            self.canvas.create_rectangle(
                c * CELL + 7,
                r * CELL + 7,
                (c + 1) * CELL - 7,
                (r + 1) * CELL - 7,
                fill=EXPANDED_FILL,
                outline=EXPANDED_FILL,
            )

        # Final optimal route.
        for pos in self.path:
            if pos in (START, GOAL):
                continue
            r, c = pos
            self.canvas.create_rectangle(
                c * CELL + 10,
                r * CELL + 10,
                (c + 1) * CELL - 10,
                (r + 1) * CELL - 10,
                fill=PATH_FILL,
                outline=PATH_FILL,
            )

        # Keep S/G visible above overlays.
        self.mark(START, "S", START_FILL)
        self.mark(GOAL, "G", GOAL_FILL)

    def update_metrics(self, current=None, done=False):
        position = current if current is not None else START
        status = "GOAL REACHED" if done else "FORKLIFT MOVING"
        self.metrics.config(
            text=(
                f"Status            : {status}\n"
                f"Current Position  : {position}\n"
                f"Path Cost         : {self.result['path_cost']}\n"
                f"Expanded Nodes    : {self.result['expanded_nodes']}\n"
                f"Execution Time    : {self.result['execution_time']:.6f} seconds"
            )
        )

    def animate(self, index):
        if index >= len(self.path):
            final = self.path[-1]
            self.update_metrics(final, done=True)
            print(f"[AGENT] Goal reached at {final}")
            print(f"[AI] Path Cost: {self.result['path_cost']}")
            print(f"[AI] Expanded Nodes: {self.result['expanded_nodes']}")
            print(f"[AI] Execution Time: {self.result['execution_time']:.6f} seconds")
            return

        pos = self.path[index]
        self.update_metrics(pos)

        if self.agent_item is not None:
            self.canvas.delete(self.agent_item)
        if self.agent_text is not None:
            self.canvas.delete(self.agent_text)

        r, c = pos
        self.agent_item = self.canvas.create_oval(
            c * CELL + 10,
            r * CELL + 10,
            (c + 1) * CELL - 10,
            (r + 1) * CELL - 10,
            fill=AGENT_FILL,
            outline=AGENT_FILL,
        )
        x, y = self.center(pos)
        self.agent_text = self.canvas.create_text(
            x, y, text="F", fill="white",
            font=("Segoe UI", 14, "bold"),
        )

        print(f"[AGENT] Step {index:02d} -> {pos}")
        self.root.after(MOVE_DELAY, lambda: self.animate(index + 1))


def print_search_summary(result):
    print("=" * 65)
    print("WAREHOUSE LOGISTICS AGENT")
    print("TRACK 1: A* SEARCH + MANHATTAN DISTANCE")
    print("=" * 65)
    print(f"[ENV] Start: {START}")
    print(f"[ENV] Goal : {GOAL}")
    print("[AI] Heuristic: Manhattan Distance")
    print("[AI] Running A*...")
    print()

    if result["path"] is None:
        print("[AI] No route found.")
        return

    # Show a compact, useful search trace for the recording.
    for record in result["search_trace"]:
        print(
            f"[AI] Expanded {record['position']} | "
            f"g={record['g']} h={record['h']} f={record['f']}"
        )

    print()
    print("[AI] Search complete")
    print(f"[AI] Path Cost      : {result['path_cost']}")
    print(f"[AI] Expanded Nodes : {result['expanded_nodes']}")
    print(f"[AI] Execution Time : {result['execution_time']:.6f} seconds")
    print()


def main():
    result = a_star(GRID, START, GOAL)
    print_search_summary(result)

    root = tk.Tk()
    WarehouseApp(root, result)
    root.mainloop()


if __name__ == "__main__":
    main()
