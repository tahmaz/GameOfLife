import pygame
import torch
import numpy as np
import time

class GameOfLife:
    def __init__(self, rows=100, cols=100, cell_size=5):
        pygame.init()
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.width = cols * cell_size
        self.height = rows * cell_size + 50  # Extra space for buttons
        self.running = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        self.grid = torch.zeros((rows, cols), dtype=torch.float32, device=self.device)
        self.set_initial_glider()
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Game of Life - GPU Optimized")
        self.clock = pygame.time.Clock()
        
        self.kernel = torch.ones(1, 1, 3, 3, device=self.device)
        self.kernel[0, 0, 1, 1] = 0
        
        self.font = pygame.font.SysFont(None, 30)
    
    def set_initial_glider(self):
        glider_positions = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
        for y, x in glider_positions:
            self.grid[y, x] = 1
    
    def draw_grid(self):
        grid_np = (self.grid.cpu().numpy() * 255).astype(np.uint8)
        surface = pygame.surfarray.make_surface(np.stack([grid_np]*3, axis=-1))
        surface = pygame.transform.scale(surface, (self.width, self.height - 50))
        self.screen.blit(surface, (0, 0))
        
    def draw_buttons(self):
        pygame.draw.rect(self.screen, (200, 200, 200), (10, self.height - 40, 100, 30))
        pygame.draw.rect(self.screen, (200, 200, 200), (120, self.height - 40, 100, 30))
        
        start_text = self.font.render("Start/Pause", True, (0, 0, 0))
        clear_text = self.font.render("Clear", True, (0, 0, 0))
        
        self.screen.blit(start_text, (15, self.height - 35))
        self.screen.blit(clear_text, (135, self.height - 35))
    
    def next_generation(self):
        grid = self.grid.unsqueeze(0).unsqueeze(0)
        neighbors = torch.nn.functional.conv2d(grid, self.kernel, padding=1).squeeze(0).squeeze(0)
        self.grid = torch.where(self.grid == 1, (neighbors == 2) | (neighbors == 3), (neighbors == 3)).float()
    
    def run(self):
        running = True
        while running:
            self.screen.fill((255, 255, 255))
            self.draw_grid()
            self.draw_buttons()
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if 10 <= x <= 110 and self.height - 40 <= y <= self.height - 10:
                        self.running = not self.running
                    elif 120 <= x <= 220 and self.height - 40 <= y <= self.height - 10:
                        self.grid.zero_()
                        self.set_initial_glider()
                
            if self.running:
                self.next_generation()
                
            self.clock.tick(20)  # 20 FPS
        
        pygame.quit()
        
if __name__ == "__main__":
    game = GameOfLife()
    game.run()

