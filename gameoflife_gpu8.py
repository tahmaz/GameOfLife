import tkinter as tk
import torch
import numpy as np
import time
from tkinter import ttk

class CellularAutomaton:
    def __init__(self, root, rows=16, cols=100):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_size = 10
        self.running = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Initialize grid
        self.grid = torch.zeros((rows, cols), dtype=torch.float32, device=self.device)
        self.set_initial_state()
        
        # Canvas setup
        self.canvas = tk.Canvas(root, width=cols * self.cell_size, height=rows * self.cell_size, bg='white')
        self.canvas.pack(pady=10)
        self.image = None
        
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
        self.reset_button = ttk.Button(control_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # FPS panel
        self.fps_var = tk.StringVar(value="FPS: 0.00")
        self.fps_label = ttk.Label(control_frame, textvariable=self.fps_var)
        self.fps_label.pack(side=tk.LEFT, padx=5)
        
        # FPS tracking
        self.frame_count = 0
        self.last_time = time.time()
        
        self.draw_grid()
        self.update()

    def draw_grid(self):
        grid_np = (self.grid.cpu().numpy() * 255).astype(np.uint8)
        img_array = np.repeat(np.repeat(grid_np, self.cell_size, axis=0), self.cell_size, axis=1)
        self.rgb_array[..., 0] = img_array
        self.rgb_array[..., 1] = img_array
        self.rgb_array[..., 2] = img_array
        ppm_data = self.ppm_header + self.rgb_array.tobytes()
        self.photo = tk.PhotoImage(data=ppm_data, format='PPM')
        if self.image is None:
            self.image = self.canvas.create_image(0, 0, image=self.photo, anchor='nw')
        else:
            self.canvas.itemconfig(self.image, image=self.photo)

    def set_initial_state(self):
        # Set first column: "0001001101"
        initial_state = [0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0]
        for row in range(self.rows):
            self.grid[row, 0] = initial_state[row]  # 0.0 or 1.0

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

    def reset(self):
        self.running = False
        self.grid.zero_()
        self.set_initial_state()
        self.draw_grid()
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        print("Reset pressed")

    def next_generation(self):
        # Reset first column to default "0001001101"
        #initial_state = torch.tensor([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 
        #                           dtype=torch.float32, device=self.device)
        initial_state = torch.tensor([0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                                   dtype=torch.float32, device=self.device)
        self.grid[:, 0] = initial_state

        new_grid = self.grid.clone()
        changes = torch.zeros_like(self.grid, device=self.device)
        
        # Process all cells
        for col in range(self.cols):
            for row in range(self.rows):
                current_val = self.grid[row, col]
                # Push if >= 0.5 to specific neighbors
                if current_val >= 0.5:
                    adjustment = 0.1
                    
                    # Right neighbor (col+1, row)
                    if col < self.cols - 1:
                        changes[row, col + 1] += adjustment
                    
                    # Top-right diagonal (col+1, row-1)
                    if col < self.cols - 1 and row > 0:
                        changes[row - 1, col + 1] += adjustment
                    
                    # Bottom-right diagonal (col+1, row+1)
                    if col < self.cols - 1 and row < self.rows - 1:
                        changes[row + 1, col + 1] += adjustment
                    
                    # Decrease own value by 0.1 after pushing
                    new_grid[row, col] = max(0.0, current_val - 0.1)
        
        # Apply changes from pushes
        new_grid = new_grid + changes
        # If value > 1.0, set to 0.0
        #new_grid = torch.where(new_grid > 1.0, torch.tensor(0.0, device=self.device), new_grid)
        # Decrease all cells by 0.1, floor at 0.0
        new_grid = torch.maximum(new_grid - 0.1, torch.tensor(0.0, device=self.device))
        # Round to nearest 0.1 for 10-state precision
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
        
        self.root.after(100, self.update)  # 100ms delay for visibility

def main():
    root = tk.Tk()
    root.title("Cellular Automaton - Left Neighbor")
    app = CellularAutomaton(root)
    root.mainloop()

if __name__ == "__main__":
    main()
