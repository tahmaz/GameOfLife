import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import sys

# Initialize Pygame and OpenGL
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -5)

# Sphere parameters
radius = 1.0
slices = 20  # Number of subdivisions in longitude
stacks = 20  # Number of subdivisions in latitude

# Mouse control variables
rot_x = 0
rot_y = 0
mouse_down = False
last_pos = None

def create_sphere():
    glBegin(GL_QUADS)
    for i in range(stacks):
        lat0 = math.pi * (-0.5 + float(i) / stacks)
        z0 = math.sin(lat0)
        zr0 = math.cos(lat0)
        lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
        z1 = math.sin(lat1)
        zr1 = math.cos(lat1)

        for j in range(slices):
            lng0 = 2 * math.pi * float(j) / slices
            x0 = math.cos(lng0)
            y0 = math.sin(lng0)
            lng1 = 2 * math.pi * float(j + 1) / slices
            x1 = math.cos(lng1)
            y1 = math.sin(lng1)

            # Define the four vertices of the quad
            glVertex3f(radius * x0 * zr0, radius * y0 * zr0, radius * z0)
            glVertex3f(radius * x1 * zr0, radius * y1 * zr0, radius * z0)
            glVertex3f(radius * x1 * zr1, radius * y1 * zr1, radius * z1)
            glVertex3f(radius * x0 * zr1, radius * y0 * zr1, radius * z1)
    glEnd()

def main():
    global rot_x, rot_y, mouse_down, last_pos

    # OpenGL settings
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)

    clock = pygame.time.Clock()

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

        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Apply rotation based on mouse input
        glPushMatrix()
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)

        # Draw the sphere with wireframe to show square cells
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor3f(1.0, 1.0, 1.0)
        create_sphere()

        glPopMatrix()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
