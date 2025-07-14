import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from copy import deepcopy
import random

# Configurable Game of Life variables
GRID_SIZE = 20  # Size of the 3D grid (GRID_SIZE x GRID_SIZE x GRID_SIZE)
SURVIVAL_MIN = 4  # Minimum number of neighbors for a live cell to survive
SURVIVAL_MAX = 5  # Maximum number of neighbors for a live cell to survive
BIRTH_MIN = 4  # Minimum number of neighbors for a dead cell to be born
BIRTH_MAX = 4  # Maximum number of neighbors for a dead cell to be born
UPDATE_INTERVAL = 500  # Milliseconds between automatic updates (when running)
GLIDER_PATTERN = [
    (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0)
]  # 5-cell glider pattern

def initialize_grid():
    grid = np.zeros((GRID_SIZE, GRID_SIZE, GRID_SIZE), dtype=int)
    # Initialize a 3D glider near the center
    center = GRID_SIZE // 2
    for dx, dy, dz in GLIDER_PATTERN:
        grid[center + dx, center + dy, center + dz] = 1
    return grid

def add_random_gliders(grid):
    # Clear grid and add one centered glider
    grid = initialize_grid()
    # Add 4 random gliders
    for _ in range(4):
        x = random.randint(2, GRID_SIZE - 3)  # Ensure glider fits
        y = random.randint(2, GRID_SIZE - 3)
        z = random.randint(2, GRID_SIZE - 3)
        orientation = random.choice(['xy', 'xz', 'yz'])
        for dx, dy, dz in GLIDER_PATTERN:
            if orientation == 'xy':
                if 0 <= x+dx < GRID_SIZE and 0 <= y+dy < GRID_SIZE and 0 <= z+dz < GRID_SIZE:
                    grid[x+dx, y+dy, z+dz] = 1
            elif orientation == 'xz':
                if 0 <= x+dx < GRID_SIZE and 0 <= y+dz < GRID_SIZE and 0 <= z+dy < GRID_SIZE:
                    grid[x+dx, y+dz, z+dy] = 1
            elif orientation == 'yz':
                if 0 <= x+dz < GRID_SIZE and 0 <= y+dx < GRID_SIZE and 0 <= z+dy < GRID_SIZE:
                    grid[x+dz, y+dx, z+dy] = 1
    return grid

def count_neighbors(grid, x, y, z):
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
    new_grid = np.zeros((GRID_SIZE, GRID_SIZE, GRID_SIZE), dtype=int)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            for z in range(GRID_SIZE):
                neighbors = count_neighbors(grid, x, y, z)
                if grid[x, y, z] == 1:
                    if SURVIVAL_MIN <= neighbors <= SURVIVAL_MAX:
                        new_grid[x, y, z] = 1
                else:
                    if BIRTH_MIN <= neighbors <= BIRTH_MAX:
                        new_grid[x, y, z] = 1
    return new_grid

def draw_cube():
    vertices = [
        (GRID_SIZE/2, -GRID_SIZE/2, -GRID_SIZE/2), (GRID_SIZE/2, GRID_SIZE/2, -GRID_SIZE/2),
        (-GRID_SIZE/2, GRID_SIZE/2, -GRID_SIZE/2), (-GRID_SIZE/2, -GRID_SIZE/2, -GRID_SIZE/2),
        (GRID_SIZE/2, -GRID_SIZE/2, GRID_SIZE/2), (GRID_SIZE/2, GRID_SIZE/2, GRID_SIZE/2),
        (-GRID_SIZE/2, GRID_SIZE/2, GRID_SIZE/2), (-GRID_SIZE/2, -GRID_SIZE/2, GRID_SIZE/2)
    ]
    edges = [
        (0,1), (1,2), (2,3), (3,0),  # Back face
        (4,5), (5,6), (6,7), (7,4),  # Front face
        (0,4), (1,5), (2,6), (3,7)   # Connecting edges
    ]
    glLineWidth(3.0)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()
    glLineWidth(1.0)
    glColor4f(0.5, 0.5, 0.5, 0.3)
    glBegin(GL_LINES)
    for x in range(-GRID_SIZE//2, GRID_SIZE//2 + 1, 1):
        for y in range(-GRID_SIZE//2, GRID_SIZE//2 + 1, 1):
            glVertex3f(x, y, -GRID_SIZE/2)
            glVertex3f(x, y, GRID_SIZE/2)
        for z in range(-GRID_SIZE//2, GRID_SIZE//2 + 1, 1):
            glVertex3f(x, -GRID_SIZE/2, z)
            glVertex3f(x, GRID_SIZE/2, z)
    for y in range(-GRID_SIZE//2, GRID_SIZE//2 + 1, 1):
        for x in range(-GRID_SIZE//2, GRID_SIZE//2 + 1, 1):
            glVertex3f(x, y, -GRID_SIZE/2)
            glVertex3f(x, y, GRID_SIZE/2)
        for z in range(-GRID_SIZE//2, GRID_SIZE//2 + 1, 1):
            glVertex3f(-GRID_SIZE/2, y, z)
            glVertex3f(GRID_SIZE/2, y, z)
    for z in range(-GRID_SIZE//2, GRID_SIZE//2 + 1, 1):
        for x in range(-GRID_SIZE//2, GRID_SIZE//2 + 1, 1):
            glVertex3f(x, -GRID_SIZE/2, z)
            glVertex3f(x, GRID_SIZE/2, z)
        for y in range(-GRID_SIZE//2, GRID_SIZE//2 + 1, 1):
            glVertex3f(-GRID_SIZE/2, y, z)
            glVertex3f(GRID_SIZE/2, y, z)
    glEnd()

def draw_cells(grid):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.0, 1.0, 0.8)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            for z in range(GRID_SIZE):
                if grid[x, y, z] == 1:
                    glPushMatrix()
                    glTranslatef(x - GRID_SIZE/2 + 0.5, y - GRID_SIZE/2 + 0.5, z - GRID_SIZE/2 + 0.5)
                    glutSolidCube(1.0)
                    glPopMatrix()

def draw_rounded_button(x, y, width, height, r, g, b, radius=5):
    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    glVertex2f(x + radius, y)
    glVertex2f(x + width - radius, y)
    glVertex2f(x + width - radius, y + height)
    glVertex2f(x + radius, y + height)
    glVertex2f(x, y + radius)
    glVertex2f(x + radius, y + radius)
    glVertex2f(x + radius, y + height - radius)
    glVertex2f(x, y + height - radius)
    glVertex2f(x + width - radius, y + radius)
    glVertex2f(x + width, y + radius)
    glVertex2f(x + width, y + height - radius)
    glVertex2f(x + width - radius, y + height - radius)
    glVertex2f(x + radius, y + height - radius)
    glVertex2f(x + width - radius, y + height - radius)
    glVertex2f(x + width - radius, y + height)
    glVertex2f(x + radius, y + height)
    glVertex2f(x + radius, y)
    glVertex2f(x + width - radius, y)
    glVertex2f(x + width - radius, y + radius)
    glVertex2f(x + radius, y + radius)
    glEnd()
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x + radius, y)
    glVertex2f(x + width - radius, y)
    glVertex2f(x + width, y + radius)
    glVertex2f(x + width, y + height - radius)
    glVertex2f(x + width - radius, y + height)
    glVertex2f(x + radius, y + height)
    glVertex2f(x, y + height - radius)
    glVertex2f(x, y + radius)
    glEnd()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_12):
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(font, ord(char))

def draw_ui(zoom_in_rect, zoom_out_rect, start_rect, stop_rect, next_rect, back_rect, clear_rect, generate_rect, running, screen_width, screen_height):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, screen_width, 0, screen_height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    panel_height = 60
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(screen_width, 0)
    glVertex2f(screen_width, panel_height)
    glVertex2f(0, panel_height)
    glEnd()
    draw_rounded_button(zoom_in_rect[0], zoom_in_rect[1], zoom_in_rect[2], zoom_in_rect[3], 0.0, 0.7, 0.0)
    draw_text(zoom_in_rect[0] + 5, zoom_in_rect[1] + 25, "Zoom In")
    draw_rounded_button(zoom_out_rect[0], zoom_out_rect[1], zoom_out_rect[2], zoom_out_rect[3], 0.7, 0.0, 0.0)
    draw_text(zoom_out_rect[0] + 5, zoom_out_rect[1] + 25, "Zoom Out")
    if not running:
        draw_rounded_button(start_rect[0], start_rect[1], start_rect[2], start_rect[3], 0.0, 0.7, 0.0)
    else:
        draw_rounded_button(start_rect[0], start_rect[1], start_rect[2], start_rect[3], 0.5, 0.5, 0.5)
    draw_text(start_rect[0] + 5, start_rect[1] + 25, "Start")
    if running:
        draw_rounded_button(stop_rect[0], stop_rect[1], stop_rect[2], stop_rect[3], 0.7, 0.0, 0.0)
    else:
        draw_rounded_button(stop_rect[0], stop_rect[1], stop_rect[2], stop_rect[3], 0.5, 0.5, 0.5)
    draw_text(stop_rect[0] + 5, stop_rect[1] + 25, "Stop")
    draw_rounded_button(next_rect[0], next_rect[1], next_rect[2], next_rect[3], 0.0, 0.0, 0.7)
    draw_text(next_rect[0] + 5, next_rect[1] + 25, "Next")
    draw_rounded_button(back_rect[0], back_rect[1], back_rect[2], back_rect[3], 0.5, 0.0, 0.5)
    draw_text(back_rect[0] + 5, back_rect[1] + 25, "Back")
    draw_rounded_button(clear_rect[0], clear_rect[1], clear_rect[2], clear_rect[3], 0.0, 0.7, 0.7)
    draw_text(clear_rect[0] + 5, clear_rect[1] + 25, "Clear")
    draw_rounded_button(generate_rect[0], generate_rect[1], generate_rect[2], generate_rect[3], 0.7, 0.7, 0.0)
    draw_text(generate_rect[0] + 5, generate_rect[1] + 25, "Generate")
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def update_projection(screen_width, screen_height, zoom):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, screen_width / screen_height if screen_height > 0 else 1, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, zoom)

def main():
    pygame.init()
    display = (800, 600)
    screen_info = pygame.display.Info()
    fullscreen = False
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | RESIZABLE)
    glutInit()
    screen_width, screen_height = display
    zoom = -40
    update_projection(screen_width, screen_height, zoom)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    clock = pygame.time.Clock()
    rot_x = 0
    rot_y = 0
    mouse_down = False
    last_pos = (0, 0)
    grid = initialize_grid()
    history = [deepcopy(grid)]
    running = False
    last_update = pygame.time.get_ticks()
    
    while True:
        screen_width, screen_height = pygame.display.get_surface().get_size()
        button_size = 60
        panel_height = 60
        zoom_in_rect = (screen_width * 0.025, 10, button_size, button_size - 20)
        zoom_out_rect = (screen_width * 0.1, 10, button_size, button_size - 20)
        start_rect = (screen_width * 0.175, 10, button_size, button_size - 20)
        stop_rect = (screen_width * 0.25, 10, button_size, button_size - 20)
        next_rect = (screen_width * 0.325, 10, button_size, button_size - 20)
        back_rect = (screen_width * 0.4, 10, button_size, button_size - 20)
        clear_rect = (screen_width * 0.475, 10, button_size, button_size - 20)
        generate_rect = (screen_width * 0.55, 10, button_size, button_size - 20)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), DOUBLEBUF | OPENGL | FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | RESIZABLE)
                    screen_width, screen_height = pygame.display.get_surface().get_size()
                    update_projection(screen_width, screen_height, zoom)
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    zoom += 2
                    if zoom > -10:
                        zoom = -10
                    update_projection(screen_width, screen_height, zoom)
                if event.key == pygame.K_MINUS:
                    zoom -= 2
                    if zoom < -100:
                        zoom = -100
                    update_projection(screen_width, screen_height, zoom)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                y = screen_height - y
                if (zoom_in_rect[0] <= x <= zoom_in_rect[0] + zoom_in_rect[2] and
                    zoom_in_rect[1] <= y <= zoom_in_rect[1] + zoom_in_rect[3]):
                    zoom += 2
                    if zoom > -10:
                        zoom = -10
                    update_projection(screen_width, screen_height, zoom)
                elif (zoom_out_rect[0] <= x <= zoom_out_rect[0] + zoom_out_rect[2] and
                      zoom_out_rect[1] <= y <= zoom_out_rect[1] + zoom_out_rect[3]):
                    zoom -= 2
                    if zoom < -100:
                        zoom = -100
                    update_projection(screen_width, screen_height, zoom)
                elif (start_rect[0] <= x <= start_rect[0] + start_rect[2] and
                      start_rect[1] <= y <= start_rect[1] + start_rect[3]):
                    running = True
                elif (stop_rect[0] <= x <= stop_rect[0] + stop_rect[2] and
                      stop_rect[1] <= y <= stop_rect[1] + stop_rect[3]):
                    running = False
                elif (next_rect[0] <= x <= next_rect[0] + next_rect[2] and
                      next_rect[1] <= y <= next_rect[1] + next_rect[3]):
                    grid = update_grid(grid)
                    history.append(deepcopy(grid))
                    if len(history) > 50:
                        history.pop(0)
                elif (back_rect[0] <= x <= back_rect[0] + back_rect[2] and
                      back_rect[1] <= y <= back_rect[1] + back_rect[3]):
                    if len(history) > 1:
                        history.pop()
                        grid = deepcopy(history[-1])
                elif (clear_rect[0] <= x <= clear_rect[0] + clear_rect[2] and
                      clear_rect[1] <= y <= clear_rect[1] + clear_rect[3]):
                    grid = initialize_grid()
                    history = [deepcopy(grid)]
                    running = False
                elif (generate_rect[0] <= x <= generate_rect[0] + generate_rect[2] and
                      generate_rect[1] <= y <= generate_rect[1] + generate_rect[3]):
                    grid = add_random_gliders(grid)
                    history = [deepcopy(grid)]
                    running = False
                else:
                    mouse_down = True
                    last_pos = event.pos
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
            if event.type == pygame.MOUSEMOTION and mouse_down:
                x, y = pygame.mouse.get_pos()
                dx = x - last_pos[0]
                dy = y - last_pos[1]
                rot_y += dx * 0.2
                rot_x += dy * 0.2
                last_pos = (x, y)
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), DOUBLEBUF | OPENGL | RESIZABLE)
                screen_width, screen_height = event.w, event.h
                update_projection(screen_width, screen_height, zoom)
        
        if running:
            current_time = pygame.time.get_ticks()
            if current_time - last_update >= UPDATE_INTERVAL:
                grid = update_grid(grid)
                history.append(deepcopy(grid))
                if len(history) > 50:
                    history.pop(0)
                last_update = current_time
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslatef(0.0, 0.0, zoom)
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)
        draw_cube()
        draw_cells(grid)
        glPopMatrix()
        draw_ui(zoom_in_rect, zoom_out_rect, start_rect, stop_rect, next_rect, back_rect, clear_rect, generate_rect, running, screen_width, screen_height)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
