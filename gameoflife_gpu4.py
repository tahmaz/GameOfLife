import tkinter as tk
import torch
import numpy as np
import time
from tkinter import ttk

class GameOfLife:
    def __init__(self, root, rows=100, cols=100):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_size = 8 
        self.running = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        self.grid = torch.zeros((rows, cols), dtype=torch.float32, device=self.device)
        self.set_initial_glider()
        
        # Canvas setup
        self.canvas = tk.Canvas(root, width=cols * self.cell_size, height=rows * self.cell_size, bg='white')
        self.canvas.pack(pady=10)
        self.image = None
        self.canvas.bind("<Button-1>", self.add_pixel)
        
        # Precompute PPM header
        self.display_width = cols * self.cell_size
        self.display_height = rows * self.cell_size
        self.ppm_header = f'P6\n{self.display_width} {self.display_height}\n255\n'.encode()
        
        # Preallocate RGB buffer
        self.rgb_array = np.zeros((self.display_height, self.display_width, 3), dtype=np.uint8)
        
        # Control frame
        control_frame = ttk.Frame(root)
        control_frame.pack(pady=5)
        
        # Buttons
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.clear_button = ttk.Button(control_frame, text="Clear", command=self.clear)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Generate random gliders
        self.generate_button = ttk.Button(control_frame, text="Generate", command=self.generate_random_gliders)
        self.generate_button.pack(side=tk.LEFT, padx=5)
        ttk.Label(control_frame, text="Glider Count:").pack(side=tk.LEFT, padx=5)
        self.glider_count_var = tk.StringVar(value="1")
        self.glider_count_entry = ttk.Entry(control_frame, textvariable=self.glider_count_var, width=5)
        self.glider_count_entry.pack(side=tk.LEFT, padx=5)
        
        # FPS panel
        self.fps_var = tk.StringVar(value="FPS: 0.00")
        self.fps_label = ttk.Label(control_frame, textvariable=self.fps_var)
        self.fps_label.pack(side=tk.LEFT, padx=5)
        
        # Convolution kernel for neighbor counting
        self.kernel = torch.ones(1, 1, 3, 3, device=self.device)
        self.kernel[0, 0, 1, 1] = 0
        
        # FPS tracking
        self.frame_count = 0
        self.last_time = time.time()
        
        self.draw_grid()
        self.update()

    def draw_grid(self):
        # Scale grid values (0.0-1.0) to 0-255 for display
        grid_np = (self.grid.cpu().numpy() * 255).astype(np.uint8)
        img_array = np.repeat(np.repeat(grid_np, self.cell_size, axis=0), self.cell_size, axis=1)
        self.rgb_array[..., 0] = img_array  # R
        self.rgb_array[..., 1] = img_array  # G
        self.rgb_array[..., 2] = img_array  # B
        ppm_data = self.ppm_header + self.rgb_array.tobytes()
        self.photo = tk.PhotoImage(data=ppm_data, format='PPM')
        if self.image is None:
            self.image = self.canvas.create_image(0, 0, image=self.photo, anchor='nw')
        else:
            self.canvas.itemconfig(self.image, image=self.photo)

    def set_initial_glider(self):
        glider_positions = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
        for y, x in glider_positions:
            self.grid[y, x] = 0.1  # Starting state for alive cells

    def generate_random_gliders(self):
        try:
            count = int(self.glider_count_var.get())
            if count < 1:
                count = 1
        except ValueError:
            count = 1
            
        glider_pattern = torch.tensor([[0.0, 0.1, 0.0],
                                     [0.0, 0.0, 0.1],
                                     [0.1, 0.1, 0.1]], dtype=torch.float32, device=self.device)
        
        for _ in range(count):
            y = np.random.randint(0, self.rows - 3)
            x = np.random.randint(0, self.cols - 3)
            self.grid[y:y+3, x:x+3] = glider_pattern
            
        self.draw_grid()

    def add_pixel(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        if 0 <= x < self.cols and 0 <= y < self.rows:
            if self.grid[y, x] == 0.0:
                self.grid[y, x] = 0.1  # New cell starts at 0.5
            else:
                self.grid[y, x] = max(0.0, self.grid[y, x] - 0.1)  # Decrease by 0.1
            self.draw_grid()

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
        # Count neighbors (cells > 0)
        grid = (self.grid > 0).float().unsqueeze(0).unsqueeze(0)
        neighbor_count = torch.nn.functional.conv2d(grid, self.kernel, padding=1).squeeze(0).squeeze(0)
        
        # Sum of neighbor states
        grid_values = self.grid.unsqueeze(0).unsqueeze(0)
        neighbor_sum = torch.nn.functional.conv2d(grid_values, self.kernel, padding=1).squeeze(0).squeeze(0)
        
        # Calculate average neighbor state
        neighbor_avg = torch.where(neighbor_count > 0, neighbor_sum / neighbor_count, torch.zeros_like(neighbor_sum))
        
        # Update rules
        new_grid = self.grid.clone()
        
        # Increase existing cells by 0.1
        alive_mask = self.grid > 0
        new_grid = torch.where(alive_mask, self.grid + 0.1, new_grid)
        
        # Create new cells at 0.1 where dead with 3 neighbors
        dead_mask = self.grid == 0
        birth_mask = (neighbor_count == 3) & dead_mask
        new_grid = torch.where(birth_mask, torch.tensor(0.1, device=self.device), new_grid)
        
        # Remove cells > 1.0 or < 0.0
        new_grid = torch.where((new_grid > 1.0) | (new_grid < 0.0), torch.tensor(0.0, device=self.device), new_grid)
        
        # Round to nearest 0.1
        new_grid = torch.round(new_grid * 10) / 10
        
        self.grid = new_grid
    def update(self):
        if self.running:
            self.next_generation()
            self.draw_grid()
            self.frame_count += 1
            
            current_time = time.time()
            elapsed = current_time - self.last_time
            if elapsed >= 0.5:
                fps = self.frame_count / elapsed
                self.fps_var.set(f"FPS: {fps:.2f}")
                self.frame_count = 0
                self.last_time = current_time
        
        self.root.after(50, self.update)

def main():
    root = tk.Tk()
    root.title("Game of Life - GPU Optimized")
    app = GameOfLife(root)
    root.mainloop()

if __name__ == "__main__":
    main()
