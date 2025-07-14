import tkinter as tk
import random
import time
from tkinter import messagebox

class GameOfLife3D:
    # Game rules as configurable variables
    SURVIVAL_RULE = [4, 5, 6]  # Cells with this many neighbors survive
    BIRTH_RULE = [5]           # Dead cells with this many neighbors become alive
    UPDATE_INTERVAL = 100      # Milliseconds between updates

    def __init__(self, root, depth=20, rows=20, cols=20):
        self.root = root
        self.depth = depth  # z dimension
        self.rows = rows    # y dimension
        self.cols = cols    # x dimension
        self.cell_size = 15 # Larger cell size for visibility
        self.running = False
        self.last_update_time = time.time()
        self.fps = 0
        self.current_z = 0  # Current z-layer to display

        # Initialize 3D grid (0 = dead, 1 = alive)
        self.grid = [[[0 for _ in range(cols)] for _ in range(rows)] for _ in range(depth)]
        self.set_initial_3d_glider()  # Place 3D glider at start

        # Canvas setup
        self.canvas = tk.Canvas(root, width=cols * self.cell_size, height=rows * self.cell_size, bg='white')
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # FPS Label
        self.fps_label = tk.Label(root, text=f"FPS: {self.fps}")
        self.fps_label.pack()

        # Z-layer slider
        self.z_label = tk.Label(root, text=f"Z-Layer: {self.current_z}")
        self.z_label.pack()
        self.z_slider = tk.Scale(root, from_=0, to=depth-1, orient=tk.HORIZONTAL, command=self.update_z_layer)
        self.z_slider.pack()

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
        self.random_button = tk.Button(self.control_frame, text="Generate", command=self.generate_random_3d_gliders)
        self.random_button.pack(side=tk.LEFT, padx=5)

        # Input for number of gliders
        self.glider_input = tk.Entry(self.control_frame, width=5)
        self.glider_input.pack(side=tk.LEFT, padx=5)
        self.glider_input.insert(0, "5")  # Default value, reduced for 3D

        # Rules panel
        self.rules_frame = tk.Frame(root)
        self.rules_frame.pack(pady=10)

        # Survival rule input
        tk.Label(self.rules_frame, text="Survival Rule (e.g., 4,5,6 or []):").pack(side=tk.LEFT)
        self.survival_input = tk.Entry(self.rules_frame, width=10)
        self.survival_input.pack(side=tk.LEFT, padx=5)
        self.survival_input.insert(0, "4,5,6")

        # Birth rule input
        tk.Label(self.rules_frame, text="Birth Rule (e.g., 5 or []):").pack(side=tk.LEFT)
        self.birth_input = tk.Entry(self.rules_frame, width=10)
        self.birth_input.pack(side=tk.LEFT, padx=5)
        self.birth_input.insert(0, "5")

        # Update interval input
        tk.Label(self.rules_frame, text="Update Interval (ms):").pack(side=tk.LEFT)
        self.update_interval_input = tk.Entry(self.rules_frame, width=5)
        self.update_interval_input.pack(side=tk.LEFT, padx=5)
        self.update_interval_input.insert(0, "100")

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
                color = "black" if self.grid[self.current_z][i][j] == 1 else "white"
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
                self.cells[(i, j)] = rect

    def update_z_layer(self, value):
        self.current_z = int(value)
        self.z_label.config(text=f"Z-Layer: {self.current_z}")
        self.draw_grid()

    def on_canvas_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[self.current_z][row][col] = 1
            self.draw_grid()

    def set_initial_3d_glider(self):
        # Simple 3D glider-like pattern
        glider_positions = [
            (1, 0, 1), (1, 1, 2), (1, 2, 0), (1, 2, 1), (1, 2, 2),
            (2, 1, 1), (2, 2, 2), (3, 1, 2), (3, 2, 1)
        ]
        for z, y, x in glider_positions:
            if 0 <= z < self.depth and 0 <= y < self.rows and 0 <= x < self.cols:
                self.grid[z][y][x] = 1

    def generate_random_3d_gliders(self):
        try:
            num_gliders = int(self.glider_input.get())
        except ValueError:
            num_gliders = 5  # Default to 5 if invalid input

        num_gliders = max(1, min(num_gliders, 100))
        
        for _ in range(num_gliders):
            z = random.randint(0, self.depth - 3)
            y = random.randint(0, self.rows - 3)
            x = random.randint(0, self.cols - 3)
            glider_positions = [
                (z, y, x+1), (z, y+1, x+2), (z, y+2, x), (z, y+2, x+1), (z, y+2, x+2),
                (z+1, y+1, x+1), (z+1, y+2, x+2), (z+2, y+1, x+2), (z+2, y+2, x+1)
            ]
            for gz, gy, gx in glider_positions:
                if 0 <= gz < self.depth and 0 <= gy < self.rows and 0 <= gx < self.cols:
                    self.grid[gz][gy][gx] = 1
        
        self.draw_grid()
        print(f"Generated {num_gliders} random 3D gliders")

    def start(self):
        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        print("Start pressed: 3D Game of Life running")

    def stop(self):
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        print("Stop pressed")

    def clear(self):
        self.running = False
        self.grid = [[[0 for _ in range(self.cols)] for _ in range(self.rows)] for _ in range(self.depth)]
        self.set_initial_3d_glider()
        self.draw_grid()
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        print("Clear pressed: 3D Grid reset with glider")

    def count_neighbors(self, z, row, col):
        total = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    if i == 0 and j == 0 and k == 0:
                        continue
                    dz = (z + i) % self.depth
                    dr = (row + j) % self.rows
                    dc = (col + k) % self.cols
                    total += self.grid[dz][dr][dc]
        return total

    def apply_rules(self):
        try:
            # Parse survival rule
            survival_str = self.survival_input.get().strip()
            if survival_str in ["", "[]"]:
                self.SURVIVAL_RULE = []
            else:
                self.SURVIVAL_RULE = [int(x) for x in survival_str.split(",") if x.strip().isdigit()]
                if not self.SURVIVAL_RULE:
                    raise ValueError("Survival rule must contain valid numbers or be empty ([])")

                # Validate survival rule values
                for num in self.SURVIVAL_RULE:
                    if num < 0 or num > 26:
                        raise ValueError("Survival rule numbers must be between 0 and 26")

            # Parse birth rule
            birth_str = self.birth_input.get().strip()
            if birth_str in ["", "[]"]:
                self.BIRTH_RULE = []
            else:
                self.BIRTH_RULE = [int(x) for x in birth_str.split(",") if x.strip().isdigit()]
                if not self.BIRTH_RULE:
                    raise ValueError("Birth rule must contain valid numbers or be empty ([])")

                # Validate birth rule values
                for num in self.BIRTH_RULE:
                    if num < 0 or num > 26:
                        raise ValueError("Birth rule numbers must be between 0 and 26")

            # Parse update interval
            interval = self.update_interval_input.get().strip()
            if not interval.isdigit():
                raise ValueError("Update interval must be a positive integer")
            self.UPDATE_INTERVAL = int(interval)
            if self.UPDATE_INTERVAL < 1:
                raise ValueError("Update interval must be at least 1 ms")

            print(f"Applied rules: Survival={self.SURVIVAL_RULE}, Birth={self.BIRTH_RULE}, Interval={self.UPDATE_INTERVAL}ms")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            print(f"Error applying rules: {e}")

    def next_generation(self):
        new_grid = [[[0 for _ in range(self.cols)] for _ in range(self.rows)] for _ in range(self.depth)]
        for z in range(self.depth):
            for i in range(self.rows):
                for j in range(self.cols):
                    neighbors = self.count_neighbors(z, i, j)
                    if self.grid[z][i][j] == 1:
                        new_grid[z][i][j] = 1 if self.SURVIVAL_RULE and neighbors in self.SURVIVAL_RULE else 0
                    else:
                        new_grid[z][i][j] = 1 if self.BIRTH_RULE and neighbors in self.BIRTH_RULE else 0
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
    root.title("3D Game of Life")
    app = GameOfLife3D(root)
    root.mainloop()

if __name__ == "__main__":
    main()
