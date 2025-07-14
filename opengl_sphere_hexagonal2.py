import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

def draw_sphere(radius=10, slices=20, stacks=20):
    # Enable blending for transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Draw hexagonal grid on sphere surface with transparent lines
    glLineWidth(1.0)
    glColor4f(0.5, 0.5, 0.5, 0.3)  # Semi-transparent gray
    
    glBegin(GL_LINES)
    # Generate points for a hexagonal grid pattern
    for i in range(stacks):
        phi = i * math.pi / stacks
        phi_next = (i + 1) * math.pi / stacks
        
        for j in range(slices):
            theta = j * 2 * math.pi / slices
            theta_next = (j + 1) * 2 * math.pi / slices
            
            # Current point
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            
            # Next point in phi direction (vertical)
            x_next_phi = radius * math.sin(phi_next) * math.cos(theta)
            y_next_phi = radius * math.sin(phi_next) * math.sin(theta)
            z_next_phi = radius * math.cos(phi_next)
            
            # Next point in theta direction (horizontal)
            x_next_theta = radius * math.sin(phi) * math.cos(theta_next)
            y_next_theta = radius * math.sin(phi) * math.sin(theta_next)
            z_next_theta = radius * math.cos(phi)
            
            # Offset for hexagonal pattern (alternate rows)
            offset = (math.pi / slices) if i % 2 else 0
            theta_offset = j * 2 * math.pi / slices + offset
            theta_next_offset = (j + 1) * 2 * math.pi / slices + offset
            
            x_offset = radius * math.sin(phi) * math.cos(theta_offset)
            y_offset = radius * math.sin(phi) * math.sin(theta_offset)
            z_offset = radius * math.cos(phi)
            
            x_next_offset = radius * math.sin(phi) * math.cos(theta_next_offset)
            y_next_offset = radius * math.sin(phi) * math.sin(theta_next_offset)
            z_next_offset = radius * math.cos(phi)
            
            # Draw lines for hexagonal pattern
            glVertex3f(x, y, z)
            glVertex3f(x_next_phi, y_next_phi, z_next_phi)
            
            glVertex3f(x_offset, y_offset, z_offset)
            glVertex3f(x_next_offset, y_next_offset, z_next_offset)
            
            # Connect to next phi for hexagonal structure
            if i < stacks - 1:
                glVertex3f(x, y, z)
                glVertex3f(x_next_phi, y_next_phi, z_next_phi)
    
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
        draw_sphere()
        glPopMatrix()
        
        rotation += 1
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
