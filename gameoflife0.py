import tkinter as tk

class GameOfLife:
    def __init__(self, root, rows=10, cols=10):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_size = 30
        self.running = False

        # Initialize grid (0 = white/dead, 1 = black/alive)
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.set_initial_glider()  # Place glider at start

        # Canvas setup
        self.canvas = tk.Canvas(root, width=cols * self.cell_size, height=rows * self.cell_size, bg='white')
        self.canvas.pack(pady=10)

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
        # Place a glider at the top-left (rows 0-2, cols 0-2)
        # Pattern:
        #   O
        #     O
        # O O O
        glider_positions = [
            (0, 1),  # Row 0, col 1
            (1, 2),  # Row 1, col 2
            (2, 0),  # Row 2, col 0
            (2, 1),  # Row 2, col 1
            (2, 2)   # Row 2, col 2
        ]
        for y, x in glider_positions:
            self.grid[y][x] = 1

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
        self.set_initial_glider()  # Reset to initial glider
        self.draw_grid()
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        print("Clear pressed: Grid reset with glider")

    def count_neighbors(self, row, col):
        total = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:  # Skip the cell itself
                    continue
                r = (row + i) % self.rows  # Wrap around edges
                c = (col + j) % self.cols
                total += self.grid[r][c]
        return total

    def next_generation(self):
        new_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for i in range(self.rows):
            for j in range(self.cols):
                neighbors = self.count_neighbors(i, j)
                if self.grid[i][j] == 1:  # Live cell
                    new_grid[i][j] = 1 if neighbors in [2, 3] else 0
                else:  # Dead cell
                    new_grid[i][j] = 1 if neighbors == 3 else 0
        self.grid = new_grid

    def update(self):
        if self.running:
            self.next_generation()
            self.draw_grid()
        self.root.after(200, self.update)  # Update every 200ms

def main():
    root = tk.Tk()
    root.title("Game of Life - Glider")
    app = GameOfLife(root)
    root.mainloop()

if __name__ == "__main__":
    main()
