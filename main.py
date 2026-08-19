import tkinter as tk
from tkinter import messagebox
from algorithm import a_star
from environment import GRID, START, GOAL

# -----------------------------
# Simple settings
# -----------------------------
CELL = 58
ANIMATION_MS = 300

# -----------------------------
# Colors
# -----------------------------
BG = "#F4F6F8"
PANEL = "#FFFFFF"
TEXT = "#1F2937"
MUTED = "#667085"
GRID_LINE = "#CBD5E1"
SHELF = "#475467"
FREE = "#F8FAFC"
START_COLOR = "#16A34A"
GOAL_COLOR = "#DC2626"
PATH_COLOR = "#7DD3FC"
EXPANDED_COLOR = "#E2E8F0"
FORKLIFT_COLOR = "#2563EB"


class WarehouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Express | Track 1 - Warehouse Logistics Agent")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.result = None
        self.path = []
        self.step = 0
        self.running = False
        self.paused = False
        self.after_id = None
        self.agent_item = None
        self.agent_text = None

        self.status_var = tk.StringVar(value="Ready — click RUN A*")
        self.position_var = tk.StringVar(value=f"Start: {START}   →   Goal: {GOAL}")
        self.path_cost_var = tk.StringVar(value="—")
        self.expanded_var = tk.StringVar(value="—")
        self.time_var = tk.StringVar(value="—")
        self.step_var = tk.StringVar(value="0 / 0")
        self.speed_var = tk.IntVar(value=300)

        self.build_ui()
        self.draw_base()

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=18, pady=(14, 6))

        tk.Label(
            header,
            text="WAREHOUSE LOGISTICS AGENT",
            bg=BG, fg=TEXT,
            font=("Segoe UI", 17, "bold")
        ).pack()

        tk.Label(
            header,
            text="Track 1  •  A* Search  •  Manhattan Distance",
            bg=BG, fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(pady=(2, 0))

        # Main area
        body = tk.Frame(self.root, bg=BG)
        body.pack(padx=18, pady=6)

        # Grid panel
        grid_panel = tk.Frame(body, bg=PANEL, bd=0, highlightthickness=1,
                              highlightbackground="#D0D5DD")
        grid_panel.grid(row=0, column=0, sticky="n")

        self.canvas = tk.Canvas(
            grid_panel,
            width=len(GRID[0]) * CELL,
            height=len(GRID) * CELL,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(padx=8, pady=8)

        # Right panel
        side = tk.Frame(body, bg=BG)
        side.grid(row=0, column=1, padx=(12, 0), sticky="ns")

        # Status card
        status_card = tk.Frame(side, bg=PANEL, highlightthickness=1,
                               highlightbackground="#D0D5DD")
        status_card.pack(fill="x")

        tk.Label(
            status_card, text="DEMO STATUS",
            bg=PANEL, fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=14, pady=(12, 3))

        self.status_label = tk.Label(
            status_card, textvariable=self.status_var,
            bg=PANEL, fg=TEXT,
            font=("Segoe UI", 12, "bold"),
            wraplength=250, justify="left"
        )
        self.status_label.pack(anchor="w", padx=14, pady=(0, 6))

        tk.Label(
            status_card, textvariable=self.position_var,
            bg=PANEL, fg=MUTED,
            font=("Consolas", 9),
            wraplength=250, justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 12))

        # Metrics
        metrics = tk.Frame(side, bg=PANEL, highlightthickness=1,
                           highlightbackground="#D0D5DD")
        metrics.pack(fill="x", pady=(10, 0))

        tk.Label(metrics, text="RESULTS", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(12, 8))

        self.metric(metrics, "Path Cost", self.path_cost_var)
        self.metric(metrics, "Expanded Nodes", self.expanded_var)
        self.metric(metrics, "Execution Time", self.time_var)
        self.metric(metrics, "Animation Step", self.step_var)

        # Controls
        controls = tk.Frame(side, bg=PANEL, highlightthickness=1,
                            highlightbackground="#D0D5DD")
        controls.pack(fill="x", pady=(10, 0))

        tk.Label(controls, text="CONTROLS", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(12, 8))

        button_row = tk.Frame(controls, bg=PANEL)
        button_row.pack(fill="x", padx=12)

        self.run_btn = tk.Button(
            button_row, text="▶ RUN A*", command=self.run_search,
            bg=FORKLIFT_COLOR, fg="white", activebackground="#1D4ED8",
            activeforeground="white", relief="flat",
            font=("Segoe UI", 10, "bold"), padx=8, pady=7, cursor="hand2"
        )
        self.run_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.pause_btn = tk.Button(
            button_row, text="Ⅱ PAUSE", command=self.toggle_pause,
            bg="#E2E8F0", fg=TEXT, relief="flat",
            font=("Segoe UI", 10, "bold"), padx=8, pady=7,
            state="disabled", cursor="hand2"
        )
        self.pause_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))

        tk.Button(
            controls, text="↻ RESET",
            command=self.reset,
            bg="#F1F5F9", fg=TEXT, relief="flat",
            font=("Segoe UI", 10, "bold"), pady=7, cursor="hand2"
        ).pack(fill="x", padx=12, pady=(8, 8))

        tk.Label(
            controls, text="Animation speed (lower = faster)",
            bg=PANEL, fg=MUTED, font=("Segoe UI", 8)
        ).pack(anchor="w", padx=14)

        self.speed = tk.Scale(
            controls, from_=80, to=700, orient="horizontal",
            variable=self.speed_var, showvalue=True,
            bg=PANEL, fg=TEXT, highlightthickness=0,
            troughcolor="#E2E8F0", length=245,
            command=self.speed_changed
        )
        self.speed.pack(padx=8, pady=(0, 8))

        # Explanation
        explain = tk.Frame(side, bg=PANEL, highlightthickness=1,
                           highlightbackground="#D0D5DD")
        explain.pack(fill="x", pady=(10, 0))

        tk.Label(explain, text="HOW IT WORKS", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(12, 5))

        text = (
            "1. A* calculates the route.\n"
            "2. Manhattan Distance guides the search.\n"
            "3. Shelves are obstacles.\n"
            "4. The forklift follows the calculated path.\n"
            "5. Metrics are shown after the search."
        )
        tk.Label(
            explain, text=text, bg=PANEL, fg=TEXT,
            font=("Segoe UI", 9), justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 12))

        # Legend
        legend = tk.Frame(self.root, bg=BG)
        legend.pack(pady=(2, 12))

        self.legend_item(legend, SHELF, "Shelf")
        self.legend_item(legend, EXPANDED_COLOR, "Expanded")
        self.legend_item(legend, PATH_COLOR, "Optimal Path")
        self.legend_item(legend, FORKLIFT_COLOR, "Forklift")

    def metric(self, parent, label, variable):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", padx=14, pady=3)
        tk.Label(row, text=label, bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left")
        tk.Label(row, textvariable=variable, bg=PANEL, fg=TEXT,
                 font=("Consolas", 9, "bold")).pack(side="right")
        return row

    def legend_item(self, parent, color, label):
        item = tk.Frame(parent, bg=BG)
        item.pack(side="left", padx=6)
        tk.Label(item, text="  ", bg=color, width=2).pack(side="left")
        tk.Label(item, text=label, bg=BG, fg=MUTED,
                 font=("Segoe UI", 8)).pack(side="left", padx=(3, 0))

    def speed_changed(self, value):
        # The scale is intentionally simple; no extra action is needed.
        pass

    def draw_base(self):
        self.canvas.delete("all")

        for r in range(len(GRID)):
            for c in range(len(GRID[0])):
                fill = SHELF if GRID[r][c] == 1 else FREE
                self.canvas.create_rectangle(
                    c * CELL, r * CELL,
                    (c + 1) * CELL, (r + 1) * CELL,
                    fill=fill, outline=GRID_LINE
                )

        self.mark_cell(START, "S", START_COLOR)
        self.mark_cell(GOAL, "G", GOAL_COLOR)

    def mark_cell(self, pos, text, fill):
        r, c = pos
        self.canvas.create_rectangle(
            c * CELL + 4, r * CELL + 4,
            (c + 1) * CELL - 4, (r + 1) * CELL - 4,
            fill=fill, outline=fill
        )
        self.canvas.create_text(
            c * CELL + CELL // 2,
            r * CELL + CELL // 2,
            text=text, fill="white",
            font=("Segoe UI", 15, "bold")
        )

    def draw_result(self):
        # Expanded nodes
        for record in self.result.get("search_trace", []):
            pos = record["position"]
            if pos in (START, GOAL):
                continue
            r, c = pos
            if GRID[r][c] == 1:
                continue
            self.canvas.create_rectangle(
                c * CELL + 8, r * CELL + 8,
                (c + 1) * CELL - 8, (r + 1) * CELL - 8,
                fill=EXPANDED_COLOR, outline=EXPANDED_COLOR
            )

        # Optimal path
        for pos in self.path:
            if pos in (START, GOAL):
                continue
            r, c = pos
            self.canvas.create_rectangle(
                c * CELL + 11, r * CELL + 11,
                (c + 1) * CELL - 11, (r + 1) * CELL - 11,
                fill=PATH_COLOR, outline=PATH_COLOR
            )

        self.mark_cell(START, "S", START_COLOR)
        self.mark_cell(GOAL, "G", GOAL_COLOR)

    def run_search(self):
        self.cancel_animation()

        self.status_var.set("Thinking — A* is calculating...")
        self.position_var.set(f"Start: {START}   →   Goal: {GOAL}")
        self.path_cost_var.set("—")
        self.expanded_var.set("—")
        self.time_var.set("—")
        self.step_var.set("0 / 0")
        self.run_btn.config(state="disabled")
        self.pause_btn.config(state="disabled")

        self.root.update_idletasks()

        print("\n" + "=" * 65)
        print("WAREHOUSE LOGISTICS AGENT")
        print("TRACK 1: A* SEARCH + MANHATTAN DISTANCE")
        print("=" * 65)
        print(f"[ENV] Start: {START}")
        print(f"[ENV] Goal : {GOAL}")
        print("[AI] Heuristic: Manhattan Distance")
        print("[AI] Running A*...")

        self.result = a_star(GRID, START, GOAL)

        if not self.result["path"]:
            self.status_var.set("No route found")
            self.run_btn.config(state="normal")
            return

        self.path = self.result["path"]
        self.step = 0

        print(f"[AI] Search complete")
        print(f"[AI] Path Cost      : {self.result['path_cost']}")
        print(f"[AI] Expanded Nodes : {self.result['expanded_nodes']}")
        print(f"[AI] Execution Time : {self.result['execution_time']:.6f} seconds")

        self.draw_base()
        self.draw_result()

        self.path_cost_var.set(str(self.result["path_cost"]))
        self.expanded_var.set(str(self.result["expanded_nodes"]))
        self.time_var.set(f"{self.result['execution_time']:.6f}s")
        self.step_var.set(f"0 / {len(self.path) - 1}")
        self.status_var.set("Path found — forklift ready")
        self.position_var.set(f"Start: {START}   →   Goal: {GOAL}")

        self.running = True
        self.paused = False
        self.pause_btn.config(state="normal", text="Ⅱ PAUSE")
        self.root.after(700, self.animate_step)

    def animate_step(self):
        if not self.running or self.paused:
            return

        if self.step >= len(self.path):
            self.finish_animation()
            return

        pos = self.path[self.step]

        if self.agent_item is not None:
            self.canvas.delete(self.agent_item)
        if self.agent_text is not None:
            self.canvas.delete(self.agent_text)

        r, c = pos

        self.agent_item = self.canvas.create_oval(
            c * CELL + 10, r * CELL + 10,
            (c + 1) * CELL - 10, (r + 1) * CELL - 10,
            fill=FORKLIFT_COLOR, outline=FORKLIFT_COLOR
        )
        self.agent_text = self.canvas.create_text(
            c * CELL + CELL // 2,
            r * CELL + CELL // 2,
            text="F", fill="white",
            font=("Segoe UI", 14, "bold")
        )

        self.position_var.set(f"Forklift: {pos}   →   Goal: {GOAL}")
        self.step_var.set(f"{self.step} / {len(self.path) - 1}")
        self.status_var.set(
            "Forklift moving..." if pos != GOAL else "Goal reached!"
        )

        print(f"[AGENT] Step {self.step:02d} -> {pos}")

        if pos == GOAL:
            self.finish_animation()
            return

        self.step += 1
        self.after_id = self.root.after(self.speed_var.get(), self.animate_step)

    def finish_animation(self):
        self.running = False
        self.paused = False
        self.step = len(self.path) - 1
        self.step_var.set(f"{self.step} / {self.step}")
        self.status_var.set("GOAL REACHED ✓")
        self.position_var.set(f"Forklift: {GOAL}   ✓ Loading bay reached")
        self.pause_btn.config(state="disabled", text="Ⅱ PAUSE")
        self.run_btn.config(state="normal")

        print(f"[AGENT] Goal reached at {GOAL}")
        print(f"[AI] Final Path Cost      : {self.result['path_cost']}")
        print(f"[AI] Final Expanded Nodes : {self.result['expanded_nodes']}")
        print(f"[AI] Final Execution Time : {self.result['execution_time']:.6f} seconds")

    def toggle_pause(self):
        if not self.running:
            return

        self.paused = not self.paused

        if self.paused:
            self.pause_btn.config(text="▶ RESUME")
            self.status_var.set("Paused — click RESUME to continue")
            self.cancel_after_only()
        else:
            self.pause_btn.config(text="Ⅱ PAUSE")
            self.status_var.set("Forklift moving...")
            self.root.after(100, self.animate_step)

    def reset(self):
        self.cancel_animation()
        self.result = None
        self.path = []
        self.step = 0
        self.status_var.set("Ready — click RUN A*")
        self.position_var.set(f"Start: {START}   →   Goal: {GOAL}")
        self.path_cost_var.set("—")
        self.expanded_var.set("—")
        self.time_var.set("—")
        self.step_var.set("0 / 0")
        self.run_btn.config(state="normal")
        self.pause_btn.config(state="disabled", text="Ⅱ PAUSE")
        self.draw_base()

    def cancel_after_only(self):
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None

    def cancel_animation(self):
        self.running = False
        self.paused = False
        self.cancel_after_only()


def main():
    root = tk.Tk()
    WarehouseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
