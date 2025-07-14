import tkinter as tk
import random
import time
from tkinter import messagebox

class GameOfLife:
    # Game rules as configurable variables
    SURVIVAL_RULE = [2, 3]  # Cells with this many neighbors survive
    BIRTH_RULE = [3]        # Dead cells with this many neighbors become alive
    UPDATE_INTERVAL = 1     # Milliseconds between updates

    def __init__(self, root, rows=100, cols=100):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_size = 8 
        self.running = False
        self.last_update_time = time.time()
        self.fps = 0

        # Initialize grid (0 = white/dead, 1 = black/alive)
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.set_initial_glider()  # Place glider at start

        # Canvas setup
        self.canvas = tk.Canvas(root, width=cols * self.cell_size, height=rows * self.cell_size, bg='white')
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # FPS Label
        self.fps_label = tk.Label(root, text=f"FPS: {self.fps}")
        self.fps_label.pack()

        # Control panel for buttons
        self.control_frame = tk.Frame(root)
        self.control_frame.pack()

        # Buttons
        self.start_button = tk.Button(self.control_frame, text="Start", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(self.control_frame, text="Stop", command=self.stop, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.clear_button = tk.Button(self.control_frame, text="Clear", command=self.clear)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        self.random_button = tk.Button(self.control_frame, text="Generate", command=self.generate_random_gliders)
        self.random_button.pack(side=tk.LEFT, padx=5)

        # Input for number of gliders
        self.glider_input = tk.Entry(self.control_frame, width=5)
        self.glider_input.pack(side=tk.LEFT, padx=5)
        self.glider_input.insert(0, "10")  # Default value

        # Rules panel
        self.rules_frame = tk.Frame(root)
        self.rules_frame.pack(pady=10)

        # Survival rule input
        tk.Label(self.rules_frame, text="Survival Rule (e.g., 2,3):").pack(side=tk.LEFT)
        self.survival_input = tk.Entry(self.rules_frame, width=10)
        self.survival_input.pack(side=tk.LEFT, padx=5)
        self.survival_input.insert(0, "2,3")

        # Birth rule input
        tk.Label(self.rules_frame, text="Birth Rule (e.g., 3):").pack(side=tk.LEFT)
        self.birth_input = tk.Entry(self.rules_frame, width=10)
        self.birth_input.pack(side=tk.LEFT, padx=5)
        self.birth_input.insert(0, "3")

        # Update interval input
        tk.Label(self.rules_frame, text="Update Interval (ms):").pack(side=tk.LEFT)
        self.update_interval_input = tk.Entry(self.rules_frame, width=5)
        self.update_interval_input.pack(side=tk.LEFT, padx=5)
        self.update_interval_input.insert(0, "1")

        # Apply button for rules
        self.apply_button = tk.Button(self.rules_frame, text="Apply Rules", command=self.apply_rules)
        self.apply_button.pack(side=tk.LEFT, padx=5)

        # Draw initial grid
        self.cells = {}
        self.draw_grid()

        # Start the update loop
        self.update()

    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                color = "black" if self.grid[i][j] == 1 else "white"
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
                self.cells[(i, j)] = rect

    def on_canvas_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = 1
            self.draw_grid()

    def set_initial_glider(self):
        glider_positions = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
        for y, x in glider_positions:
            self.grid[y][x] = 1

    def generate_random_gliders(self):
        try:
            num_gliders = int(self.glider_input.get())
        except ValueError:
            num_gliders = 10  # Default to 10 if invalid input

        num_gliders = max(1, min(num_gliders, 1000))
        
        for _ in range(num_gliders):
            x, y = random.randint(0, self.cols - 3), random.randint(0, self.rows - 3)
            glider_positions = [(y, x+1), (y+1, x+2), (y+2, x), (y+2, x+1), (y+2, x+2)]
            for gy, gx in glider_positions:
                self.grid[gy][gx] = 1
        
        self.draw_grid()
        print(f"Generated {num_gliders} random gliders")

    def start(self):
        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        print("Start pressed: Game of Life running")

    def stop(self):
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        print("Stop pressed")

    def clear(self):
        self.running = False
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.set_initial_glider()
        self.draw_grid()
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        print("Clear pressed: Grid reset with glider")

    def count_neighbors(self, row, col):
        total = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                r = (row + i) % self.rows
                c = (col + j) % self.cols
                total += self.grid[r][c]
        return total

    def apply_rules(self):
        try:
            # Parse survival rule
            survival_str = self.survival_input.get()
            self.SURVIVAL_RULE = [int(x) for x in survival_str.split(",") if x.strip().isdigit()]
            if not self.SURVIVAL_RULE:
                raise ValueError("Survival rule must contain at least one valid number")

            # Parse birth rule
            birth_str = self.birth_input.get()
            self.BIRTH_RULE = [int(x) for x in birth_str.split(",") if x.strip().isdigit()]
            if not self.BIRTH_RULE:
                raise ValueError("Birth rule must contain at least one valid number")

            # Parse update interval
            interval = self.update_interval_input.get()
            if not interval.strip().isdigit():
                raise ValueError("Update interval must be a positive integer")
            self.UPDATE_INTERVAL = int(interval)
            if self.UPDATE_INTERVAL < 1:
                raise ValueError("Update interval must be at least 1 ms")

            print(f"Applied rules: Survival={self.SURVIVAL_RULE}, Birth={self.BIRTH_RULE}, Interval={self.UPDATE_INTERVAL}ms")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            print(f"Error applying rules: {e}")

    def next_generation(self):
        new_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for i in range(self.rows):
            for j in range(self.cols):
                neighbors = self.count_neighbors(i, j)
                if self.grid[i][j] == 1:
                    new_grid[i][j] = 1 if neighbors in self.SURVIVAL_RULE else 0
                else:
                    new_grid[i][j] = 1 if neighbors in self.BIRTH_RULE else 0
        self.grid = new_grid

    def update(self):
        if self.running:
            self.next_generation()
            self.draw_grid()
        
        # Calculate FPS
        current_time = time.time()
        self.fps = int(1 / (current_time - self.last_update_time)) if (current_time - self.last_update_time) > 0 else 0
        self.last_update_time = current_time
        self.fps_label.config(text=f"FPS: {self.fps}")
        
        self.root.after(self.UPDATE_INTERVAL, self.update)

def main():
    root = tk.Tk()
    root.title("Game of Life - Glider")
    app = GameOfLife(root)
    root.mainloop()

if __name__ == "__main__":
    main()
