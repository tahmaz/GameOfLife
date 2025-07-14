import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

def draw_sphere(radius=20, slices=60, stacks=60):
    # Enable blending for transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Draw square grid on sphere surface with transparent lines
    glLineWidth(1.0)
    glColor4f(0.5, 0.5, 0.5, 0.3)  # Semi-transparent gray
    
    glBegin(GL_LINES)
    # Generate points for a square-like grid pattern
    for i in range(stacks + 1):
        phi = i * math.pi / stacks
        # Adjust theta steps to reduce polar distortion
        theta_steps = max(1, int(slices * math.sin(phi)))  # Vary slices based on phi to avoid pole compression
        if theta_steps == 0:
            theta_steps = 1  # Ensure at least one step near poles
        
        for j in range(theta_steps + 1):
            theta = j * 2 * math.pi / theta_steps
            
            # Current point
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            
            # Next point in phi direction (vertical lines)
            if i < stacks:
                x_next_phi = radius * math.sin((i + 1) * math.pi / stacks) * math.cos(theta)
                y_next_phi = radius * math.sin((i + 1) * math.pi / stacks) * math.sin(theta)
                z_next_phi = radius * math.cos((i + 1) * math.pi / stacks)
                glVertex3f(x, y, z)
                glVertex3f(x_next_phi, y_next_phi, z_next_phi)
            
            # Next point in theta direction (horizontal lines)
            if j < theta_steps:
                x_next_theta = radius * math.sin(phi) * math.cos((j + 1) * 2 * math.pi / theta_steps)
                y_next_theta = radius * math.sin(phi) * math.sin((j + 1) * 2 * math.pi / theta_steps)
                z_next_theta = radius * math.cos(phi)
                glVertex3f(x, y, z)
                glVertex3f(x_next_theta, y_next_theta, z_next_theta)
    
    glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0]/display[1]), 0.1, 200.0)  # Increased far plane for larger sphere
    glTranslatef(0.0, 0.0, -80)  # Adjusted initial zoom for larger sphere
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    clock = pygame.time.Clock()
    rot_x = 0
    rot_y = 0
    zoom = -80
    mouse_down = False
    last_pos = (0, 0)
    slices = 60  # Initial slices for ~1x1 unit cells
    stacks = 60  # Initial stacks for ~1x1 unit cells
    
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
                    zoom += 4
                    if zoom > -20:  # Adjusted for larger sphere
                        zoom = -20
                if event.key == pygame.K_MINUS:  # Zoom out
                    zoom -= 4
                    if zoom < -200:  # Adjusted for larger sphere
                        zoom = -200
                if event.key == pygame.K_u:  # Increase cell size (decrease slices/stacks)
                    slices = max(10, slices - 5)
                    stacks = max(10, stacks - 5)
                if event.key == pygame.K_i:  # Decrease cell size (increase slices/stacks)
                    slices = min(100, slices + 5)
                    stacks = min(100, stacks + 5)
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
        draw_sphere(radius=20, slices=slices, stacks=stacks)
        glPopMatrix()
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
