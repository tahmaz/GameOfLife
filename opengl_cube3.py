import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

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

def draw_ui(zoom_in_rect, zoom_out_rect, screen_width, screen_height):
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
    
    # Draw zoom in button with border and label
    glColor3f(0.0, 0.7, 0.0)  # Green button
    glBegin(GL_QUADS)
    glVertex2f(zoom_in_rect[0], zoom_in_rect[1])
    glVertex2f(zoom_in_rect[0] + zoom_in_rect[2], zoom_in_rect[1])
    glVertex2f(zoom_in_rect[0] + zoom_in_rect[2], zoom_in_rect[1] + zoom_in_rect[3])
    glVertex2f(zoom_in_rect[0], zoom_in_rect[1] + zoom_in_rect[3])
    glEnd()
    # Button border
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(zoom_in_rect[0], zoom_in_rect[1])
    glVertex2f(zoom_in_rect[0] + zoom_in_rect[2], zoom_in_rect[1])
    glVertex2f(zoom_in_rect[0] + zoom_in_rect[2], zoom_in_rect[1] + zoom_in_rect[3])
    glVertex2f(zoom_in_rect[0], zoom_in_rect[1] + zoom_in_rect[3])
    glEnd()
    
    # Draw zoom out button with border and label
    glColor3f(0.7, 0.0, 0.0)  # Red button
    glBegin(GL_QUADS)
    glVertex2f(zoom_out_rect[0], zoom_out_rect[1])
    glVertex2f(zoom_out_rect[0] + zoom_out_rect[2], zoom_out_rect[1])
    glVertex2f(zoom_out_rect[0] + zoom_out_rect[2], zoom_out_rect[1] + zoom_out_rect[3])
    glVertex2f(zoom_out_rect[0], zoom_out_rect[1] + zoom_out_rect[3])
    glEnd()
    # Button border
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(zoom_out_rect[0], zoom_out_rect[1])
    glVertex2f(zoom_out_rect[0] + zoom_out_rect[2], zoom_out_rect[1])
    glVertex2f(zoom_out_rect[0] + zoom_out_rect[2], zoom_out_rect[1] + zoom_out_rect[3])
    glVertex2f(zoom_out_rect[0], zoom_out_rect[1] + zoom_out_rect[3])
    glEnd()
    
    # Restore 3D projection and depth test
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def main():
    pygame.init()
    display = (800, 600)
    screen_info = pygame.display.Info()
    fullscreen = False
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | RESIZABLE)
    
    # Initialize 3D projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, display[0]/display[1], 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -40)  # Initial zoom level
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    clock = pygame.time.Clock()
    rot_x = 0
    rot_y = 0
    zoom = -40
    mouse_down = False
    last_pos = (0, 0)
    
    # UI button rectangles (x, y, width, height)
    panel_height = 60
    button_size = 40
    zoom_in_rect = (20, 10, button_size, button_size)
    zoom_out_rect = (80, 10, button_size, button_size)
    
    while True:
        screen_width, screen_height = pygame.display.get_surface().get_size()
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
                    # Reset projection matrix
                    glMatrixMode(GL_PROJECTION)
                    glLoadIdentity()
                    gluPerspective(45, screen_width/screen_height, 0.1, 100.0)
                    glMatrixMode(GL_MODELVIEW)
                    glLoadIdentity()
                    glTranslatef(0.0, 0.0, zoom)
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:  # Zoom in
                    zoom += 2
                    if zoom > -10:
                        zoom = -10
                if event.key == pygame.K_MINUS:  # Zoom out
                    zoom -= 2
                    if zoom < -100:
                        zoom = -100
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                x, y = event.pos
                # Adjust y-coordinate for OpenGL (origin at bottom-left)
                y = screen_height - y
                # Check if click is within zoom in button
                if (zoom_in_rect[0] <= x <= zoom_in_rect[0] + zoom_in_rect[2] and
                    zoom_in_rect[1] <= y <= zoom_in_rect[1] + zoom_in_rect[3]):
                    zoom += 2
                    if zoom > -10:
                        zoom = -10
                # Check if click is within zoom out button
                elif (zoom_out_rect[0] <= x <= zoom_out_rect[0] + zoom_out_rect[2] and
                      zoom_out_rect[1] <= y <= zoom_out_rect[1] + zoom_out_rect[3]):
                    zoom -= 2
                    if zoom < -100:
                        zoom = -100
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
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                gluPerspective(45, event.w/event.h, 0.1, 100.0)
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                glTranslatef(0.0, 0.0, zoom)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Draw 3D cube
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslatef(0.0, 0.0, zoom)
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)
        draw_cube()
        glPopMatrix()
        
        # Draw UI
        draw_ui(zoom_in_rect, zoom_out_rect, screen_width, screen_height)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
