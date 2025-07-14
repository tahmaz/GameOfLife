import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import sys
from copy import deepcopy

# Initialize Pygame and OpenGL
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

# Camera parameters
zoom = -3.0  # Adjusted initial z translation for better visibility
zoom_min = -10.0  # Farthest zoom out
zoom_max = -2.0  # Closest zoom in
zoom_step = 0.5  # Zoom increment per scroll

# Sphere parameters
radius = 1.5  # Radius of the sphere
grid_size = 40  # Number of 1x1 squares per cube face side
cell_size = 1.0 / grid_size  # Size of each square (0.025)

# Game of Life grid (6 faces, grid_size x grid_size)
gol_grid = [[[0 for _ in range(grid_size)] for _ in range(grid_size)] for _ in range(6)]
# Initialize some cells as alive (random example)
for face in range(6):
    for i in range(grid_size):
        for j in range(grid_size):
            if np.random.random() < 0.2:  # 20% chance of being alive
                gol_grid[face][i][j] = 1

# Mouse control variables
rot_x = 0
rot_y = 0
mouse_down = False
last_pos = None

# Cylinder parameters
cyl_radius = 0.2
cyl_height = 1.0

def normalize_vertex(x, y, z):
    """Normalize a point to lie on the sphere's surface."""
    length = math.sqrt(x*x + y*y + z*z)
    if length == 0:
        return x, y, z
    return (x/length) * radius, (y/length) * radius, (z/length) * radius

def draw_cube_mapped_sphere():
    """Draw the sphere as a cube projected onto a sphere with transparent square cells."""
    # Enable blending for transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Draw transparent surface
    glBegin(GL_QUADS)
    glColor4f(0.5, 0.5, 0.5, 0.2)  # Grey with 20% opacity
    for face in range(6):
        for i in range(grid_size):
            for j in range(grid_size):
                u0 = -0.5 + i * cell_size
                u1 = -0.5 + (i + 1) * cell_size
                v0 = -0.5 + j * cell_size
                v1 = -0.5 + (j + 1) * cell_size
                if face == 0:  # Front (+z)
                    vertices = [
                        normalize_vertex(u0, v0, 0.5),
                        normalize_vertex(u1, v0, 0.5),
                        normalize_vertex(u1, v1, 0.5),
                        normalize_vertex(u0, v1, 0.5)
                    ]
                elif face == 1:  # Back (-z)
                    vertices = [
                        normalize_vertex(-u0, v0, -0.5),
                        normalize_vertex(-u1, v0, -0.5),
                        normalize_vertex(-u1, v1, -0.5),
                        normalize_vertex(-u0, v1, -0.5)
                    ]
                elif face == 2:  # Top (+y)
                    vertices = [
                        normalize_vertex(u0, 0.5, v0),
                        normalize_vertex(u1, 0.5, v0),
                        normalize_vertex(u1, 0.5, v1),
                        normalize_vertex(u0, 0.5, v1)
                    ]
                elif face == 3:  # Bottom (-y)
                    vertices = [
                        normalize_vertex(u0, -0.5, -v0),
                        normalize_vertex(u1, -0.5, -v0),
                        normalize_vertex(u1, -0.5, -v1),
                        normalize_vertex(u0, -0.5, -v1)
                    ]
                elif face == 4:  # Right (+x)
                    vertices = [
                        normalize_vertex(0.5, v0, -u0),
                        normalize_vertex(0.5, v0, -u1),
                        normalize_vertex(0.5, v1, -u1),
                        normalize_vertex(0.5, v1, -u0)
                    ]
                elif face == 5:  # Left (-x)
                    vertices = [
                        normalize_vertex(-0.5, v0, u0),
                        normalize_vertex(-0.5, v0, u1),
                        normalize_vertex(-0.5, v1, u1),
                        normalize_vertex(-0.5, v1, u0)
                    ]
                for vertex in vertices:
                    glVertex3f(*vertex)
    glEnd()

    # Draw transparent mesh lines
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glBegin(GL_QUADS)
    glColor4f(1.0, 1.0, 1.0, 0.3)  # White lines with 30% opacity
    for face in range(6):
        for i in range(grid_size):
            for j in range(grid_size):
                u0 = -0.5 + i * cell_size
                u1 = -0.5 + (i + 1) * cell_size
                v0 = -0.5 + j * cell_size
                v1 = -0.5 + (j + 1) * cell_size
                if face == 0:
                    vertices = [
                        normalize_vertex(u0, v0, 0.5),
                        normalize_vertex(u1, v0, 0.5),
                        normalize_vertex(u1, v1, 0.5),
                        normalize_vertex(u0, v1, 0.5)
                    ]
                elif face == 1:
                    vertices = [
                        normalize_vertex(-u0, v0, -0.5),
                        normalize_vertex(-u1, v0, -0.5),
                        normalize_vertex(-u1, v1, -0.5),
                        normalize_vertex(-u0, v1, -0.5)
                    ]
                elif face == 2:
                    vertices = [
                        normalize_vertex(u0, 0.5, v0),
                        normalize_vertex(u1, 0.5, v0),
                        normalize_vertex(u1, 0.5, v1),
                        normalize_vertex(u0, 0.5, v1)
                    ]
                elif face == 3:
                    vertices = [
                        normalize_vertex(u0, -0.5, -v0),
                        normalize_vertex(u1, -0.5, -v0),
                        normalize_vertex(u1, -0.5, -v1),
                        normalize_vertex(u0, -0.5, -v1)
                    ]
                elif face == 4:
                    vertices = [
                        normalize_vertex(0.5, v0, -u0),
                        normalize_vertex(0.5, v0, -u1),
                        normalize_vertex(0.5, v1, -u1),
                        normalize_vertex(0.5, v1, -u0)
                    ]
                elif face == 5:
                    vertices = [
                        normalize_vertex(-0.5, v0, u0),
                        normalize_vertex(-0.5, v0, u1),
                        normalize_vertex(-0.5, v1, u1),
                        normalize_vertex(-0.5, v1, u0)
                    ]
                for vertex in vertices:
                    glVertex3f(*vertex)
    glEnd()
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)  # Reset to fill mode
    glDisable(GL_BLEND)

def draw_game_of_life_cubes():
    """Draw cubes for alive cells on the sphere's surface."""
    cube_size = cell_size  # Cube edge length matches mesh square size
    glColor3f(1.0, 0.0, 0.0)  # Red cubes for alive cells
    for face in range(6):
        for i in range(grid_size):
            for j in range(grid_size):
                if gol_grid[face][i][j] == 1:
                    # Center of the square
                    u = -0.5 + (i + 0.5) * cell_size
                    v = -0.5 + (j + 0.5) * cell_size
                    if face == 0:  # Front (+z)
                        center = normalize_vertex(u, v, 0.5)
                        normal = (0, 0, 1)
                    elif face == 1:  # Back (-z)
                        center = normalize_vertex(-u, v, -0.5)
                        normal = (0, 0, -1)
                    elif face == 2:  # Top (+y)
                        center = normalize_vertex(u, 0.5, v)
                        normal = (0, 1, 0)
                    elif face == 3:  # Bottom (-y)
                        center = normalize_vertex(u, -0.5, -v)
                        normal = (0, -1, 0)
                    elif face == 4:  # Right (+x)
                        center = normalize_vertex(0.5, v, -u)
                        normal = (1, 0, 0)
                    elif face == 5:  # Left (-x)
                        center = normalize_vertex(-0.5, v, u)
                        normal = (-1, 0, 0)
                    # Move cube slightly outward along normal
                    center = (
                        center[0] + normal[0] * cube_size * 0.5,
                        center[1] + normal[1] * cube_size * 0.5,
                        center[2] + normal[2] * cube_size * 0.5
                    )
                    glPushMatrix()
                    glTranslatef(*center)
                    glScalef(cube_size, cube_size, cube_size)
                    draw_cube()
                    glPopMatrix()

def draw_cube():
    """Draw a unit cube centered at origin."""
    vertices = [
        (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),  # Front
        (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)     # Back
    ]
    faces = [
        (0, 1, 2, 3),  # Front
        (5, 4, 7, 6),  # Back
        (4, 5, 1, 0),  # Bottom
        (6, 7, 3, 2),  # Top
        (4, 0, 3, 7),  # Left
        (1, 5, 6, 2)   # Right
    ]
    glBegin(GL_QUADS)
    for face in faces:
        for vertex in face:
            glVertex3f(*vertices[vertex])
    glEnd()

def draw_cylinder():
    """Draw a cylinder at the center."""
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 1.0, 0.0, 0.5)  # Green cylinder with 50% opacity
    quad = gluNewQuadric()
    glPushMatrix()
    glTranslatef(0, -cyl_height/2, 0)
    gluCylinder(quad, cyl_radius, cyl_radius, cyl_height, 32, 32)
    glPopMatrix()
    gluDeleteQuadric(quad)
    glDisable(GL_BLEND)

def get_neighbor_count(face, i, j):
    """Count alive neighbors for a cell, handling cube face boundaries."""
    count = 0
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            ni, nj = i + di, j + dj
            nface = face
            if ni < 0:
                if face == 0:  # Front
                    nface, ni, nj = 5, grid_size-1, nj
                elif face == 1:  # Back
                    nface, ni, nj = 4, grid_size-1, nj
                elif face == 2:  # Top
                    nface, ni, nj = 5, grid_size-1, grid_size-1-nj
                elif face == 3:  # Bottom
                    nface, ni, nj = 4, grid_size-1, grid_size-1-nj
                elif face == 4:  # Right
                    nface, ni, nj = 3, grid_size-1, grid_size-1-nj
                elif face == 5:  # Left
                    nface, ni, nj = 2, grid_size-1, grid_size-1-nj
            elif ni >= grid_size:
                if face == 0:
                    nface, ni, nj = 4, 0, nj
                elif face == 1:
                    nface, ni, nj = 5, 0, nj
                elif face == 2:
                    nface, ni, nj = 4, 0, grid_size-1-nj
                elif face == 3:
                    nface, ni, nj = 5, 0, grid_size-1-nj
                elif face == 4:
                    nface, ni, nj = 2, 0, grid_size-1-nj
                elif face == 5:
                    nface, ni, nj = 3, 0, grid_size-1-nj
            if nj < 0:
                if face == 0:
                    nface, ni, nj = 3, ni, grid_size-1
                elif face == 1:
                    nface, ni, nj = 3, grid_size-1-ni, 0
                elif face == 2:
                    nface, ni, nj = 0, ni, grid_size-1
                elif face == 3:
                    nface, ni, nj = 1, grid_size-1-ni, grid_size-1
                elif face == 4:
                    nface, ni, nj = 0, grid_size-1, ni
                elif face == 5:
                    nface, ni, nj = 0, 0, grid_size-1-ni
            elif nj >= grid_size:
                if face == 0:
                    nface, ni, nj = 2, ni, 0
                elif face == 1:
                    nface, ni, nj = 2, grid_size-1-ni, grid_size-1
                elif face == 2:
                    nface, ni, nj = 1, ni, 0
                elif face == 3:
                    nface, ni, nj = 0, grid_size-1-ni, 0
                elif face == 4:
                    nface, ni, nj = 1, 0, ni
                elif face == 5:
                    nface, ni, nj = 1, grid_size-1, grid_size-1-ni
            if 0 <= ni < grid_size and 0 <= nj < grid_size:
                count += gol_grid[nface][ni][nj]
    return count

def update_game_of_life():
    """Update the Game of Life grid based on standard rules."""
    global gol_grid
    new_grid = deepcopy(gol_grid)
    for face in range(6):
        for i in range(grid_size):
            for j in range(grid_size):
                neighbors = get_neighbor_count(face, i, j)
                if gol_grid[face][i][j] == 1:
                    if neighbors < 2 or neighbors > 3:
                        new_grid[face][i][j] = 0
                else:
                    if neighbors == 3:
                        new_grid[face][i][j] = 1
    gol_grid = new_grid

def main():
    global rot_x, rot_y, mouse_down, last_pos, zoom

    # OpenGL settings
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glViewport(0, 0, display[0], display[1])  # Ensure viewport matches window size

    clock = pygame.time.Clock()
    frame_count = 0
    update_interval = 10  # Update Game of Life every 10 frames

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_down = True
                    last_pos = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False
            elif event.type == pygame.MOUSEMOTION and mouse_down:
                curr_pos = pygame.mouse.get_pos()
                dx = curr_pos[0] - last_pos[0]
                dy = curr_pos[1] - last_pos[1]
                rot_y += dx * 0.5
                rot_x += dy * 0.5
                last_pos = curr_pos
            elif event.type == pygame.MOUSEWHEEL:
                # Zoom in/out with mouse wheel
                zoom += zoom_step * event.y  # event.y: positive for scroll up, negative for scroll down
                zoom = max(min(zoom, zoom_max), zoom_min)  # Clamp zoom within range

        # Update Game of Life periodically
        frame_count += 1
        if frame_count % update_interval == 0:
            update_game_of_life()

        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set up camera with zoom
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 0, zoom, 0, 0, 0, 0, 1, 0)  # Camera at (0,0,zoom) looking at origin

        # Apply rotation
        glPushMatrix()
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)

        # Draw the sphere, cylinder, and Game of Life cubes
        draw_cube_mapped_sphere()
        draw_cylinder()
        draw_game_of_life_cubes()

        glPopMatrix()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()