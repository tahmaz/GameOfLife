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
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -40)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    clock = pygame.time.Clock()
    rotation = 0
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(rotation, 1, 1, 1)  # Rotate around all axes
        draw_cube()
        glPopMatrix()
        
        rotation += 1
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
