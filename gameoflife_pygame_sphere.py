import pygame
import math
import platform
import asyncio
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game of Life on a Sphere with 3D Rotation and Square Cells")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Sphere parameters
BASE_RADIUS = 200
CENTER = (WIDTH // 2, HEIGHT // 2)
N_THETA = 20  # Number of divisions in theta (polar angle)
N_PHI = 40    # Number of divisions in phi (azimuthal angle)
CELL_SIZE = 8  # Base size of square cells in pixels, adjusted by projection

# Rotation and zoom variables
rotation_x = 0  # Rotation around x-axis (radians)
rotation_y = 0  # Rotation around y-axis (radians)
zoom_level = 1.0  # Zoom factor (1.0 is default)
dragging = False
last_mouse_pos = None

# Game of Life grid
cells = []
neighbors = []

def setup():
    global cells, neighbors
    # Create spherical grid points
    cells = []
    for i in range(N_THETA):
        for j in range(N_PHI):
            cells.append(random.choice([0, 1]))  # Random initial state: 0 (dead) or 1 (alive)
    
    # Compute neighbors based on angular proximity
    neighbors = [[] for _ in range(len(cells))]
    for i in range(N_THETA):
        for j in range(N_PHI):
            idx = i * N_PHI + j
            # Neighbors: adjacent theta and phi points, wrapping around phi
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni = (i + di) % N_THETA  # No wrapping in theta to avoid poles
                    nj = (j + dj) % N_PHI    # Wrap in phi
                    if 0 <= ni < N_THETA:
                        neighbors[idx].append(ni * N_PHI + nj)

def project_point(theta, phi):
    # Apply 3D rotation (x-axis then y-axis)
    cos_rx, sin_rx = math.cos(rotation_x), math.sin(rotation_x)
    cos_ry, sin_ry = math.cos(rotation_y), math.sin(rotation_y)
    
    # Spherical to Cartesian
    x = math.sin(theta) * math.cos(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(theta)
    
    # Rotate around x-axis
    y_rot = y * cos_rx - z * sin_rx
    z_rot = y * sin_rx + z * cos_rx
    x_rot = x
    
    # Rotate around y-axis
    x_final = x_rot * cos_ry + z_rot * sin_ry
    z_final = -x_rot * sin_ry + z_rot * cos_ry
    y_final = y_rot
    
    # Project to 2D (orthographic projection along z-axis)
    scale = 1 / (1 + z_final / (BASE_RADIUS * 2))  # Depth scaling
    screen_x = CENTER[0] + x_final * BASE_RADIUS * zoom_level * scale
    screen_y = CENTER[1] + y_final * BASE_RADIUS * zoom_level * scale
    return screen_x, screen_y, scale

def get_square_vertices(theta, phi, size):
    # Calculate vertices of a square around the point (theta, phi)
    dtheta = size / (BASE_RADIUS * zoom_level)  # Angular size based on cell size
    dphi = dtheta / math.sin(theta + 1e-6)      # Adjust for spherical geometry
    vertices = [
        (theta - dtheta/2, phi - dphi/2),
        (theta + dtheta/2, phi - dphi/2),
        (theta + dtheta/2, phi + dphi/2),
        (theta - dtheta/2, phi + dphi/2)
    ]
    return [project_point(t, p)[:2] for t, p in vertices]  # Return 2D coordinates

def draw():
    screen.fill(BLACK)
    # Draw all cells as squares
    for i in range(N_THETA):
        for j in range(N_PHI):
            idx = i * N_PHI + j
            theta = i * math.pi / (N_THETA - 1)  # Polar angle from 0 to pi
            phi = j * 2 * math.pi / N_PHI       # Azimuthal angle from 0 to 2pi
            vertices = get_square_vertices(theta, phi, CELL_SIZE)
            color = RED if cells[idx] == 1 else WHITE
            # Only draw if vertices are valid (not too distorted)
            if all(abs(v[0]) < WIDTH * 2 and abs(v[1]) < HEIGHT * 2 for v in vertices):
                pygame.draw.polygon(screen, color, vertices)
    pygame.display.flip()

def update_game():
    global cells
    new_cells = cells.copy()
    for i in range(len(cells)):
        live_neighbors = sum(cells[n] for n in neighbors[i])
        if cells[i] == 1:  # Live cell
            if live_neighbors < 2 or live_neighbors > 3:
                new_cells[i] = 0  # Die
        else:  # Dead cell
            if live_neighbors == 3:
                new_cells[i] = 1  # Become alive
    cells = new_cells

async def main():
    global rotation_x, rotation_y, zoom_level, dragging, last_mouse_pos
    setup()
    FPS = 10  # Slower for visibility
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    dragging = True
                    last_mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                dx = event.pos[0] - last_mouse_pos[0]
                dy = event.pos[1] - last_mouse_pos[1]
                rotation_y += dx * 0.005  # Y-axis rotation (horizontal drag)
                rotation_x += dy * 0.005  # X-axis rotation (vertical drag)
                last_mouse_pos = event.pos
            elif event.type == pygame.MOUSEWHEEL:
                zoom_level += event.y * 0.1  # Zoom in/out with mouse wheel
                zoom_level = max(0.5, min(zoom_level, 2.0))  # Limit zoom range
        
        update_game()
        draw()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())