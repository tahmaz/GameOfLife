import tkinter as tk
import random
import time

class GameOfLife:
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

        # FPS Label
        self.fps_label = tk.Label(root, text=f"FPS: {self.fps}")
        self.fps_label.pack()

        # Draw initial grid
        self.cells = {}
        self.draw_grid()

        # Buttons
        self.start_button = tk.Button(root, text="Start", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(root, text="Stop", command=self.stop, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.clear_button = tk.Button(root, text="Clear", command=self.clear)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        self.random_button = tk.Button(root, text="Generate", command=self.generate_random_gliders)
        self.random_button.pack(side=tk.LEFT, padx=5)

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

    def set_initial_glider(self):
        glider_positions = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
        for y, x in glider_positions:
            self.grid[y][x] = 1

    def generate_random_gliders(self):
        for _ in range(10):
            x, y = random.randint(0, self.cols - 3), random.randint(0, self.rows - 3)
            glider_positions = [(y, x+1), (y+1, x+2), (y+2, x), (y+2, x+1), (y+2, x+2)]
            for gy, gx in glider_positions:
                self.grid[gy][gx] = 1
        
        self.draw_grid()
        print("Generated 10 random gliders")

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

    def next_generation(self):
        new_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for i in range(self.rows):
            for j in range(self.cols):
                neighbors = self.count_neighbors(i, j)
                if self.grid[i][j] == 1:
                    new_grid[i][j] = 1 if neighbors in [2, 3] else 0
                else:
                    new_grid[i][j] = 1 if neighbors == 3 else 0
        self.grid = new_grid

    def update(self):
        if self.running:
            self.next_generation()
            self.draw_grid()
        
        # Calculate FPS
        current_time = time.time()
        self.fps = int(1 / (current_time - self.last_update_time))
        self.last_update_time = current_time
        self.fps_label.config(text=f"FPS: {self.fps}")
        
        self.root.after(1, self.update)


def main():
    root = tk.Tk()
    root.title("Game of Life - Glider")
    app = GameOfLife(root)
    root.mainloop()


if __name__ == "__main__":
    main()

