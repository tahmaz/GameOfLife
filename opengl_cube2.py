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

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0]/display[1]), 0.1, 100.0)
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
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:  # Zoom in
                    zoom += 2
                    if zoom > -10:  # Prevent zooming too close
                        zoom = -10
                if event.key == pygame.K_MINUS:  # Zoom out
                    zoom -= 2
                    if zoom < -100:  # Prevent zooming too far
                        zoom = -100
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                mouse_down = True
                last_pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
            if event.type == pygame.MOUSEMOTION and mouse_down:
                x, y = pygame.mouse.get_pos()
                dx = x - last_pos[0]
                dy = y - last_pos[1]
                rot_y += dx * 0.2  # Adjust rotation sensitivity
                rot_x += dy * 0.2
                last_pos = (x, y)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glTranslatef(0.0, 0.0, zoom)  # Apply zoom
        glRotatef(rot_x, 1, 0, 0)    # Rotate around X-axis
        glRotatef(rot_y, 0, 1, 0)    # Rotate around Y-axis
        draw_cube()
        glPopMatrix()
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
