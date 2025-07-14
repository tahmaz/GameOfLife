import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

def generate_icosahedron():
    # Golden ratio for icosahedron vertices
    t = (1.0 + math.sqrt(5.0)) / 2.0  # Golden ratio
    vertices = [
        (-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0),  # Equatorial vertices
        (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),   # Polar vertices
        (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)    # Other vertices
    ]
    
    # Normalize vertices to lie on a unit sphere (radius 10 for visibility)
    vertices = [(x * 10 / math.sqrt(x**2 + y**2 + z**2),
                 y * 10 / math.sqrt(x**2 + y**2 + z**2),
                 z * 10 / math.sqrt(x**2 + y**2 + z**2)) for x, y, z in vertices]
    
    # Define edges of the icosahedron (corrected to ensure valid connections)
    edges = [
        (0, 1), (0, 5), (0, 10), (0, 11), (0, 7),
        (1, 5), (1, 7), (1, 8), (1, 9),
        (2, 3), (2, 6), (2, 10), (2, 11),
        (3, 6), (3, 8), (3, 9),
        (4, 5), (4, 9), (4, 10), (4, 11),
        (5, 9), (5, 11),
        (6, 10), (6, 8),
        (7, 8), (7, 10),
        (8, 9), (9, 10),
        (10, 11)
    ]
    
    # Validate edges to prevent duplicates or self-loops
    edges = [(i, j) for i, j in edges if i != j]
    
    return vertices, edges

def draw_sphere():
    vertices, edges = generate_icosahedron()
    
    # Draw main sphere edges (bold lines)
    glLineWidth(3.0)
    glColor3f(1.0, 1.0, 1.0)  # White color for main edges
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()
    
    # Draw internal grid lines for finer cells (with zero-division protection)
    glLineWidth(1.0)
    glColor4f(0.5, 0.5, 0.5, 0.3)  # Semi-transparent gray
    glBegin(GL_LINES)
    for edge in edges:
        v1, v2 = vertices[edge[0]], vertices[edge[1]]
        mid = ((v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2, (v1[2] + v2[2]) / 2)
        # Calculate length and protect against zero division
        length = math.sqrt(sum(x**2 for x in mid))
        if length > 1e-6:  # Small epsilon to avoid division by zero
            mid = (mid[0] * 10 / length, mid[1] * 10 / length, mid[2] * 10 / length)
            glVertex3fv(v1)
            glVertex3fv(mid)
            glVertex3fv(mid)
            glVertex3fv(v2)
    glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
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
