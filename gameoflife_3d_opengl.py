import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from copy import deepcopy
import random

def initialize_grid():
    # 20x20x20 grid for Game of Life
    grid = np.zeros((20, 20, 20), dtype=int)
    # Initialize a 3D glider near the center (at ~10,10,10)
    center = 10
    grid[center, center, center] = 1
    grid[center+1, center, center] = 1
    grid[center, center+1, center] = 1
    grid[center, center, center+1] = 1
    grid[center+1, center+1, center] = 1
    return grid

def add_random_gliders(grid):
    # Clear grid and add one centered glider
    grid = initialize_grid()
    # Add 4 random gliders
    glider = [
        (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0)
    ]
    for _ in range(4):
        x = random.randint(2, 17)  # Ensure glider fits within 20x20x20
        y = random.randint(2, 17)
        z = random.randint(2, 17)
        orientation = random.choice(['xy', 'xz', 'yz'])
        for dx, dy, dz in glider:
            if orientation == 'xy':
                if 0 <= x+dx < 20 and 0 <= y+dy < 20 and 0 <= z+dz < 20:
                    grid[x+dx, y+dy, z+dz] = 1
            elif orientation == 'xz':
                if 0 <= x+dx < 20 and 0 <= y+dz < 20 and 0 <= z+dy < 20:
                    grid[x+dx, y+dz, z+dy] = 1
            elif orientation == 'yz':
                if 0 <= x+dz < 20 and 0 <= y+dx < 20 and 0 <= z+dy < 20:
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
                if 0 <= nx < 20 and 0 <= ny < 20 and 0 <= nz < 20:
                    count += grid[nx, ny, nz]
    return count

def update_grid(grid):
    new_grid = np.zeros((20, 20, 20), dtype=int)
    for x in range(20):
        for y in range(20):
            for z in range(20):
                neighbors = count_neighbors(grid, x, y, z)
                if grid[x, y, z] == 1:
                    if 4 <= neighbors <= 6:  # Survives
                        new_grid[x, y, z] = 1
                else:
                    if 5 <= neighbors <= 7:  # Born
                        new_grid[x, y, z] = 1
    return new_grid

def draw_cube():
    # Define vertices for the main cube (20x20x20)
    vertices = [
        (10, -10, -10), (10, 10, -10), (-10, 10, -10), (-10, -10, -10),  # Back face
        (10, -10, 10), (10, 10, 10), (-10, 10, 10), (-10, -10, 10)       # Front face
    ]
    
    # Define edges for the main cube
    edges = [
        (0,1), (1,2), (2,3), (3,0),  # Back face
        (4,5), (5,6), (6,7), (7,4),  # Front face
        (0,4), (1,5), (2,6), (3,7)   # Connecting edges
    ]
    
    # Draw main cube with bold lines
    glLineWidth(3.0)
    glColor3f(1.0, 1.0, 1.0)  # White color for main cube
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()
    
    # Draw internal grid (1x1x1 cells) with transparent lines
    glLineWidth(1.0)
    glColor4f(0.5, 0.5, 0.5, 0.3)  # Semi-transparent gray
    glBegin(GL_LINES)
    # X-axis lines
    for x in range(-10, 11, 1):
        for y in range(-10, 11, 1):
            glVertex3f(x, y, -10)
            glVertex3f(x, y, 10)
        for z in range(-10, 11, 1):
            glVertex3f(x, -10, z)
            glVertex3f(x, 10, z)
    # Y-axis lines
    for y in range(-10, 11, 1):
        for x in range(-10, 11, 1):
            glVertex3f(x, y, -10)
            glVertex3f(x, y, 10)
        for z in range(-10, 11, 1):
            glVertex3f(-10, y, z)
            glVertex3f(10, y, z)
    # Z-axis lines
    for z in range(-10, 11, 1):
        for x in range(-10, 11, 1):
            glVertex3f(x, -10, z)
            glVertex3f(x, 10, z)
        for y in range(-10, 11, 1):
            glVertex3f(-10, y, z)
            glVertex3f(10, y, z)
    glEnd()

def draw_cells(grid):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.0, 1.0, 0.8)  # Blue, 0.8 transparency
    for x in range(20):
        for y in range(20):
            for z in range(20):
                if grid[x, y, z] == 1:
                    # Translate to center of cell (grid indices to world coords)
                    glPushMatrix()
                    glTranslatef(x - 10 + 0.5, y - 10 + 0.5, z - 10 + 0.5)
                    glutSolidCube(1.0)
                    glPopMatrix()

def draw_rounded_button(x, y, width, height, r, g, b, radius=5):
    # Approximate rounded corners with multiple quads
    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    # Main body
    glVertex2f(x + radius, y)
    glVertex2f(x + width - radius, y)
    glVertex2f(x + width - radius, y + height)
    glVertex2f(x + radius, y + height)
    # Left strip
    glVertex2f(x, y + radius)
    glVertex2f(x + radius, y + radius)
    glVertex2f(x + radius, y + height - radius)
    glVertex2f(x, y + height - radius)
    # Right strip
    glVertex2f(x + width - radius, y + radius)
    glVertex2f(x + width, y + radius)
    glVertex2f(x + width, y + height - radius)
    glVertex2f(x + width - radius, y + height - radius)
    # Top strip
    glVertex2f(x + radius, y + height - radius)
    glVertex2f(x + width - radius, y + height - radius)
    glVertex2f(x + width - radius, y + height)
    glVertex2f(x + radius, y + height)
    # Bottom strip
    glVertex2f(x + radius, y)
    glVertex2f(x + width - radius, y)
    glVertex2f(x + width - radius, y + radius)
    glVertex2f(x + radius, y + radius)
    glEnd()
    # White border
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
    glColor3f(1.0, 1.0, 1.0)  # White text
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(font, ord(char))

def draw_ui(zoom_in_rect, zoom_out_rect, start_rect, stop_rect, next_rect, back_rect, clear_rect, generate_rect, running, screen_width, screen_height):
    # Switch to 2D orthographic projection for UI
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, screen_width, 0, screen_height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Disable depth test for UI
    glDisable(GL_DEPTH_TEST)
    
    # Draw bottom panel
    panel_height = 60
    glColor3f(0.3, 0.3, 0.3)  # Dark gray panel
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(screen_width, 0)
    glVertex2f(screen_width, panel_height)
    glVertex2f(0, panel_height)
    glEnd()
    
    # Draw zoom in button
    draw_rounded_button(zoom_in_rect[0], zoom_in_rect[1], zoom_in_rect[2], zoom_in_rect[3], 0.0, 0.7, 0.0)
    draw_text(zoom_in_rect[0] + 5, zoom_in_rect[1] + 25, "Zoom In")
    
    # Draw zoom out button
    draw_rounded_button(zoom_out_rect[0], zoom_out_rect[1], zoom_out_rect[2], zoom_out_rect[3], 0.7, 0.0, 0.0)
    draw_text(zoom_out_rect[0] + 5, zoom_out_rect[1] + 25, "Zoom Out")
    
    # Draw start button
    if not running:
        draw_rounded_button(start_rect[0], start_rect[1], start_rect[2], start_rect[3], 0.0, 0.7, 0.0)  # Green
    else:
        draw_rounded_button(start_rect[0], start_rect[1], start_rect[2], start_rect[3], 0.5, 0.5, 0.5)  # Gray
    draw_text(start_rect[0] + 5, start_rect[1] + 25, "Start")
    
    # Draw stop button
    if running:
        draw_rounded_button(stop_rect[0], stop_rect[1], stop_rect[2], stop_rect[3], 0.7, 0.0, 0.0)  # Red
    else:
        draw_rounded_button(stop_rect[0], stop_rect[1], stop_rect[2], stop_rect[3], 0.5, 0.5, 0.5)  # Gray
    draw_text(stop_rect[0] + 5, stop_rect[1] + 25, "Stop")
    
    # Draw next button
    draw_rounded_button(next_rect[0], next_rect[1], next_rect[2], next_rect[3], 0.0, 0.0, 0.7)  # Blue
    draw_text(next_rect[0] + 5, next_rect[1] + 25, "Next")
    
    # Draw back button
    draw_rounded_button(back_rect[0], back_rect[1], back_rect[2], back_rect[3], 0.5, 0.0, 0.5)  # Purple
    draw_text(back_rect[0] + 5, back_rect[1] + 25, "Back")
    
    # Draw clear button
    draw_rounded_button(clear_rect[0], clear_rect[1], clear_rect[2], clear_rect[3], 0.0, 0.7, 0.7)  # Cyan
    draw_text(clear_rect[0] + 5, clear_rect[1] + 25, "Clear")
    
    # Draw generate button
    draw_rounded_button(generate_rect[0], generate_rect[1], generate_rect[2], generate_rect[3], 0.7, 0.7, 0.0)  # Yellow
    draw_text(generate_rect[0] + 5, generate_rect[1] + 25, "Generate")
    
    # Restore 3D projection and depth test
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
    
    # Initialize GLUT
    glutInit()
    
    # Initialize 3D projection
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
    
    # Game of Life variables
    grid = initialize_grid()
    history = [deepcopy(grid)]  # Store initial state
    running = False
    last_update = pygame.time.get_ticks()
    update_interval = 500  # 0.5 seconds per generation
    
    while True:
        screen_width, screen_height = pygame.display.get_surface().get_size()
        # Define button rectangles dynamically (x, y, width, height)
        button_size = 60  # For text
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
                if event.key == pygame.K_f:  # Toggle fullscreen
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), DOUBLEBUF | OPENGL | FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | RESIZABLE)
                    screen_width, screen_height = pygame.display.get_surface().get_size()
                    update_projection(screen_width, screen_height, zoom)
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:  # Zoom in
                    zoom += 2
                    if zoom > -10:
                        zoom = -10
                    update_projection(screen_width, screen_height, zoom)
                if event.key == pygame.K_MINUS:  # Zoom out
                    zoom -= 2
                    if zoom < -100:
                        zoom = -100
                    update_projection(screen_width, screen_height, zoom)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                x, y = event.pos
                # Adjust y-coordinate for OpenGL (origin at bottom-left)
                y = screen_height - y
                # Check button clicks
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
                    if len(history) > 50:  # Limit history size
                        history.pop(0)
                elif (back_rect[0] <= x <= back_rect[0] + back_rect[2] and
                      back_rect[1] <= y <= back_rect[1] + back_rect[3]):
                    if len(history) > 1:
                        history.pop()  # Remove current state
                        grid = deepcopy(history[-1])  # Revert to previous
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
        
        # Update Game of Life if running
        if running:
            current_time = pygame.time.get_ticks()
            if current_time - last_update >= update_interval:
                grid = update_grid(grid)
                history.append(deepcopy(grid))
                if len(history) > 50:  # Limit history size
                    history.pop(0)
                last_update = current_time
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Draw 3D cube and cells
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslatef(0.0, 0.0, zoom)
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)
        draw_cube()
        draw_cells(grid)
        glPopMatrix()
        
        # Draw UI
        draw_ui(zoom_in_rect, zoom_out_rect, start_rect, stop_rect, next_rect, back_rect, clear_rect, generate_rect, running, screen_width, screen_height)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
