import tkinter as tk
import torch
import numpy as np

class GameOfLife:
    def __init__(self, root, rows=100, cols=100):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_size = 5
        self.running = False

        # Device setup
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        # Initialize grid
        self.grid = torch.zeros((rows, cols), dtype=torch.float32, device=self.device)
        self.set_initial_glider()

        # Canvas setup
        self.canvas = tk.Canvas(root, width=cols * self.cell_size, height=rows * self.cell_size, bg='white')
        self.canvas.pack(pady=10)
        self.image = None

        # Buttons
        self.start_button = tk.Button(root, text="Start", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(root, text="Stop", command=self.stop, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.clear_button = tk.Button(root, text="Clear", command=self.clear)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Convolution kernel
        self.kernel = torch.ones(1, 1, 3, 3, device=self.device)
        self.kernel[0, 0, 1, 1] = 0

        # Initial draw
        self.draw_grid()
        self.update()

    def draw_grid(self):
        # Convert grid to numpy (0 or 255)
        grid_np = (self.grid.cpu().numpy() * 255).astype(np.uint8)
        # Upscale to match cell_size
        img_array = np.repeat(np.repeat(grid_np, self.cell_size, axis=0), self.cell_size, axis=1)
        
        # Convert to RGB (3 channels: 0 for black, 255 for white)
        rgb_array = np.stack([img_array] * 3, axis=2)  # Shape: (height, width, 3)
        
        # Create PPM header
        height, width = rgb_array.shape[0], rgb_array.shape[1]
        ppm_header = f'P6\n{width} {height}\n255\n'.encode()
        
        # Combine header with RGB data
        ppm_data = ppm_header + rgb_array.tobytes()
        
        # Create PhotoImage
        self.photo = tk.PhotoImage(data=ppm_data, format='PPM')
        if self.image is None:
            self.image = self.canvas.create_image(0, 0, image=self.photo, anchor='nw')
        else:
            self.canvas.itemconfig(self.image, image=self.photo)

    def set_initial_glider(self):
        glider_positions = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
        for y, x in glider_positions:
            self.grid[y, x] = 1

    def start(self):
        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        print("Start pressed")

    def stop(self):
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        print("Stop pressed")

    def clear(self):
        self.running = False
        self.grid.zero_()
        self.set_initial_glider()
        self.draw_grid()
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        print("Clear pressed")

    def next_generation(self):
        grid = self.grid.unsqueeze(0).unsqueeze(0)
        neighbors = torch.nn.functional.conv2d(grid, self.kernel, padding=1).squeeze(0).squeeze(0)
        self.grid = torch.where(self.grid == 1, (neighbors == 2) | (neighbors == 3), (neighbors == 3)).float()

    def update(self):
        if self.running:
            self.next_generation()
            self.draw_grid()
        self.root.after(50, self.update)

def main():
    root = tk.Tk()
    root.title("Game of Life - GPU Optimized")
    app = GameOfLife(root)
    root.mainloop()

if __name__ == "__main__":
    main()
