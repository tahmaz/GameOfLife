import pygame
import numpy as np
import platform
import asyncio
import random

# Constants
GRID_SIZE = 20  # 20x20x20 grid
CELL_SIZE = 50  # Pixel size of each cell
WINDOW_SIZE = 500  # Window size in pixels
BUTTON_HEIGHT = 80  # Space for buttons
FPS = 10  # Frames per second for animation

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WHITE_TRANSPARENT = (255, 255, 255, 128)  # Semi-transparent white for cell borders
DARK_GRAY = (50, 50, 50)  # Button background
PASTEL_BLUE = (150, 200, 255)  # Start, Zoom In
PASTEL_GREEN = (150, 255, 150)  # Stop, Zoom Out
PASTEL_PINK = (255, 150, 200)  # Next, Left
PASTEL_PURPLE = (200, 150, 255)  # Back, Right, Up, Down
PASTEL_YELLOW = (255, 255, 150)  # Generate, Clear
HOVER_BLUE = (180, 220, 255)
HOVER_GREEN = (180, 255, 180)
HOVER_PINK = (255, 180, 220)
HOVER_PURPLE = (220, 180, 255)
HOVER_YELLOW = (255, 255, 180)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + BUTTON_HEIGHT))
pygame.display.set_caption("3D Game of Life")
clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 14)  # Smaller font for more buttons

# Enable alpha blending
screen.set_alpha(None)

# Initialize grid with a single glider in the center
grid = np.zeros((GRID_SIZE, GRID_SIZE, GRID_SIZE), dtype=int)
# 3D glider pattern (5 cells, placed at ~center, e.g., (10,10,10))
glider = [
    (0, 1, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1), (2, 1, 0)
]
center = GRID_SIZE // 2
for dx, dy, dz in glider:
    grid[center + dx, center + dy, center + dz] = 1
previous_grid = np.copy(grid)  # Store initial state
is_running = True  # Simulation state

# Camera parameters for 3D projection
angle_x = 0
angle_y = 0
zoom = 0.5  # Adjusted for smaller cube

# Button rectangles (two rows, 5 per row, smaller size)
button_start = pygame.Rect(20, WINDOW_SIZE + 10, 80, 25)
button_stop = pygame.Rect(110, WINDOW_SIZE + 10, 80, 25)
button_next = pygame.Rect(200, WINDOW_SIZE + 10, 80, 25)
button_back = pygame.Rect(290, WINDOW_SIZE + 10, 80, 25)
button_generate = pygame.Rect(380, WINDOW_SIZE + 10, 80, 25)
button_clear = pygame.Rect(380, WINDOW_SIZE + 45, 80, 25)
button_zoom_in = pygame.Rect(110, WINDOW_SIZE + 45, 80, 25)
button_zoom_out = pygame.Rect(20, WINDOW_SIZE + 45, 80, 25)
button_left = pygame.Rect(290, WINDOW_SIZE + 45, 80, 25)
button_right = pygame.Rect(380, WINDOW_SIZE + 45, 80, 25)
button_up = pygame.Rect(200, WINDOW_SIZE + 45, 80, 25)
button_down = pygame.Rect(110, WINDOW_SIZE + 45, 80, 25)

def count_neighbors(grid, x, y, z):
    """Count live neighbors in 3x3x3 grid around (x, y, z)."""
    count = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            for k in range(-1, 2):
                if i == 0 and j == 0 and k == 0:
                    continue
                nx, ny, nz = x + i, y + j, z + k
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and 0 <= nz < GRID_SIZE:
                    count += grid[nx, ny, nz]
    return count

def update_grid(grid):
    """Apply 3D Game of Life rules."""
    new_grid = np.copy(grid)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            for z in range(GRID_SIZE):
                neighbors = count_neighbors(grid, x, y, z)
                if grid[x, y, z] == 1:
                    if neighbors < 4 or neighbors > 6:
                        new_grid[x, y, z] = 0
                else:
                    if neighbors == 5:
                        new_grid[x, y, z] = 1
    return new_grid

def place_glider(grid, x, y, z):
    """Place a 3D glider at position (x, y, z)."""
    glider = [
        (0, 1, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1), (2, 1, 0)
    ]
    for dx, dy, dz in glider:
        nx, ny, nz = x + dx, y + dy, z + dz
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and 0 <= nz < GRID_SIZE:
            grid[nx, ny, nz] = 1

def generate_random_gliders(grid, num_gliders=10):
    """Place 10 random gliders in the grid."""
    for _ in range(num_gliders):
        x = random.randint(2, GRID_SIZE - 3)  # Avoid edges
        y = random.randint(2, GRID_SIZE - 3)
        z = random.randint(2, GRID_SIZE - 3)
        place_glider(grid, x, y, z)

def reset_to_single_glider():
    """Reset grid to a single glider in the center."""
    grid = np.zeros((GRID_SIZE, GRID_SIZE, GRID_SIZE), dtype=int)
    center = GRID_SIZE // 2
    for dx, dy, dz in glider:
        grid[center + dx, center + dy, center + dz] = 1
    return grid

def project_3d_to_2d(x, y, z, angle_x, angle_y, zoom):
    """Simple 3D to 2D projection with rotation and zoom."""
    x, y, z = x - GRID_SIZE / 2, y - GRID_SIZE / 2, z - GRID_SIZE / 2
    x1 = x * np.cos(angle_y) - z * np.sin(angle_y)
    z1 = x * np.sin(angle_y) + z * np.cos(angle_y)
    y1 = y * np.cos(angle_x) - z1 * np.sin(angle_x)
    z2 = y * np.sin(angle_x) + z1 * np.cos(angle_x)
    px = x1 * zoom * (WINDOW_SIZE / 10) + WINDOW_SIZE / 2
    py = y1 * zoom * (WINDOW_SIZE / 10) + WINDOW_SIZE / 2
    return px, py, z2

def draw_cube_edges():
    """Draw the 12 static edges of the main cube."""
    vertices = [
        (0, 0, 0), (GRID_SIZE, 0, 0), (GRID_SIZE, GRID_SIZE, 0), (0, GRID_SIZE, 0),
        (0, 0, GRID_SIZE), (GRID_SIZE, 0, GRID_SIZE), (GRID_SIZE, GRID_SIZE, GRID_SIZE), (0, GRID_SIZE, GRID_SIZE)
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom face
        (4, 5), (5, 6), (6, 7), (7, 4),  # Top face
        (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
    ]
    for v1, v2 in edges:
        x1, y1, z1 = vertices[v1]
        x2, y2, z2 = vertices[v2]
        px1, py1, _ = project_3d_to_2d(x1, y1, z1, angle_x, angle_y, zoom)
        px2, py2, _ = project_3d_to_2d(x2, y2, z2, angle_x, angle_y, zoom)
        pygame.draw.line(screen, WHITE, (px1, py1), (px2, py2), 3)

def draw_grid():
    """Draw the 3D grid projected to 2D with depth-based coloring and borders."""
    screen.fill(BLACK)
    # Draw button background
    pygame.draw.rect(screen, DARK_GRAY, (0, WINDOW_SIZE, WINDOW_SIZE, BUTTON_HEIGHT))
    # Draw main cube edges
    draw_cube_edges()
    # Draw cells with transparent borders
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            for z in range(GRID_SIZE):
                if grid[x, y, z] == 1:
                    px, py, depth = project_3d_to_2d(x, y, z, angle_x, angle_y, zoom)
                    color_value = int(255 * (1 - (depth + GRID_SIZE) / (2 * GRID_SIZE)))
                    color = (color_value, color_value, 255)
                    if 0 <= px < WINDOW_SIZE and 0 <= py < WINDOW_SIZE:
                        cell_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        cell_surface.fill(color)
                        pygame.draw.rect(cell_surface, WHITE_TRANSPARENT, (0, 0, CELL_SIZE, CELL_SIZE), 1)
                        screen.blit(cell_surface, (px, py))
    # Draw buttons with hover effects
    mouse_pos = pygame.mouse.get_pos()
    # First row
    start_color = HOVER_BLUE if button_start.collidepoint(mouse_pos) else PASTEL_BLUE
    stop_color = HOVER_GREEN if button_stop.collidepoint(mouse_pos) else PASTEL_GREEN
    next_color = HOVER_PINK if button_next.collidepoint(mouse_pos) else PASTEL_PINK
    back_color = HOVER_PURPLE if button_back.collidepoint(mouse_pos) else PASTEL_PURPLE
    generate_color = HOVER_YELLOW if button_generate.collidepoint(mouse_pos) else PASTEL_YELLOW
    pygame.draw.rect(screen, start_color, button_start, border_radius=5)
    pygame.draw.rect(screen, stop_color, button_stop, border_radius=5)
    pygame.draw.rect(screen, next_color, button_next, border_radius=5)
    pygame.draw.rect(screen, back_color, button_back, border_radius=5)
    pygame.draw.rect(screen, generate_color, button_generate, border_radius=5)
    # Second row
    clear_color = HOVER_YELLOW if button_clear.collidepoint(mouse_pos) else PASTEL_YELLOW
    zoom_in_color = HOVER_BLUE if button_zoom_in.collidepoint(mouse_pos) else PASTEL_BLUE
    zoom_out_color = HOVER_GREEN if button_zoom_out.collidepoint(mouse_pos) else PASTEL_GREEN
    left_color = HOVER_PINK if button_left.collidepoint(mouse_pos) else PASTEL_PINK
    right_color = HOVER_PURPLE if button_right.collidepoint(mouse_pos) else PASTEL_PURPLE
    up_color = HOVER_PURPLE if button_up.collidepoint(mouse_pos) else PASTEL_PURPLE
    down_color = HOVER_PURPLE if button_down.collidepoint(mouse_pos) else PASTEL_PURPLE
    pygame.draw.rect(screen, clear_color, button_clear, border_radius=5)
    pygame.draw.rect(screen, zoom_in_color, button_zoom_in, border_radius=5)
    pygame.draw.rect(screen, zoom_out_color, button_zoom_out, border_radius=5)
    pygame.draw.rect(screen, left_color, button_left, border_radius=5)
    pygame.draw.rect(screen, right_color, button_right, border_radius=5)
    pygame.draw.rect(screen, up_color, button_up, border_radius=5)
    pygame.draw.rect(screen, down_color, button_down, border_radius=5)
    # Draw button text
    screen.blit(font.render("Start", True, WHITE), (35, WINDOW_SIZE + 14))
    screen.blit(font.render("Stop", True, WHITE), (125, WINDOW_SIZE + 14))
    screen.blit(font.render("Next", True, WHITE), (215, WINDOW_SIZE + 14))
    screen.blit(font.render("Back", True, WHITE), (305, WINDOW_SIZE + 14))
    screen.blit(font.render("Generate", True, WHITE), (395, WINDOW_SIZE + 14))
    screen.blit(font.render("Clear", True, WHITE), (395, WINDOW_SIZE + 49))
    screen.blit(font.render("Zoom In", True, WHITE), (125, WINDOW_SIZE + 49))
    screen.blit(font.render("Zoom Out", True, WHITE), (25, WINDOW_SIZE + 49))
    screen.blit(font.render("Left", True, WHITE), (305, WINDOW_SIZE + 49))
    screen.blit(font.render("Right", True, WHITE), (395, WINDOW_SIZE + 49))
    screen.blit(font.render("Up", True, WHITE), (215, WINDOW_SIZE + 49))
    screen.blit(font.render("Down", True, WHITE), (125, WINDOW_SIZE + 49))
    pygame.display.flip()

async def main():
    global grid, previous_grid, angle_x, angle_y, zoom, is_running
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    angle_y -= 0.1
                elif event.key == pygame.K_RIGHT:
                    angle_y += 0.1
                elif event.key == pygame.K_UP:
                    angle_x -= 0.1
                elif event.key == pygame.K_DOWN:
                    angle_x += 0.1
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    zoom *= 1.1
                elif event.key == pygame.K_MINUS:
                    zoom /= 1.1
                    if zoom < 0.1:
                        zoom = 0.1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_start.collidepoint(event.pos):
                    is_running = True
                elif button_stop.collidepoint(event.pos):
                    is_running = False
                elif button_next.collidepoint(event.pos):
                    is_running = False
                    previous_grid = np.copy(grid)
                    grid = update_grid(grid)
                elif button_back.collidepoint(event.pos):
                    grid = np.copy(previous_grid)
                elif button_zoom_in.collidepoint(event.pos):
                    zoom *= 1.1
                elif button_zoom_out.collidepoint(event.pos):
                    zoom /= 1.1
                    if zoom < 0.1:
                        zoom = 0.1
                elif button_left.collidepoint(event.pos):
                    angle_y -= 0.1
                elif button_right.collidepoint(event.pos):
                    angle_y += 0.1
                elif button_up.collidepoint(event.pos):
                    angle_x -= 0.1
                elif button_down.collidepoint(event.pos):
                    angle_x += 0.1
                elif button_generate.collidepoint(event.pos):
                    is_running = False
                    previous_grid = np.copy(grid)
                    generate_random_gliders(grid, 10)
                elif button_clear.collidepoint(event.pos):
                    is_running = False
                    grid = reset_to_single_glider()
                    previous_grid = np.copy(grid)

        if is_running:
            previous_grid = np.copy(grid)
            grid = update_grid(grid)
        
        draw_grid()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
