import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import random
import math

# Initialize Pygame and OpenGL
def initialize_pygame_opengl():
    pygame.init()
    pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

initialize_pygame_opengl()

# Define shaders
VERTEX_SHADER = """
#version 330
in vec2 position;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330
out vec4 outColor;
uniform vec4 color;
void main()
{
    float dist = length(gl_PointCoord - vec2(0.5));
    float alpha = smoothstep(0.5, 0.45, dist);
    outColor = vec4(color.rgb, alpha * color.a);
}
"""

shader_program = compileProgram(
    compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
    compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
)

# Particle system class with added randomness
class ParticleSystem:
    def __init__(self, max_particles):
        self.max_particles = max_particles
        self.particles = np.zeros((max_particles, 2), dtype=np.float32)
        self.velocities = np.zeros((max_particles, 2), dtype=np.float32)
        self.colors = np.ones((max_particles, 4), dtype=np.float32)
        self.alive = np.zeros(max_particles, dtype=bool)
        self.lifetimes = np.zeros(max_particles, dtype=np.float32)

    def emit(self, position, velocity):
        for i in range(self.max_particles):
            if not self.alive[i]:
                self.particles[i] = position
                # Add randomness to particle velocity
                random_velocity = velocity + (np.random.rand(2) - 0.5) * 0.02
                self.velocities[i] = random_velocity
                self.colors[i] = np.array([1.0, 0.5, 0.0, 1.0])
                self.alive[i] = True
                self.lifetimes[i] = np.random.uniform(0.5, 1.5)  # Random lifetime between 0.5 and 1.5 seconds
                break

    def update(self, dt):
        self.particles[self.alive] += self.velocities[self.alive] * dt
        self.lifetimes[self.alive] -= dt
        self.colors[self.alive, 3] = self.lifetimes[self.alive]  # Fade out particles
        self.alive[self.lifetimes <= 0] = False

particle_system = ParticleSystem(1000)

# Player class with animations
class Player:
    def __init__(self):
        self.position = np.array([0.0, 0.0], dtype=np.float32)
        self.velocity = 0.01
        self.size = 0.05
        self.squish_factor = 1.0

    def move(self, direction):
        self.position += direction * self.velocity
        # Squishing animation
        if np.any(direction):
            self.squish_factor = 0.8
        else:
            self.squish_factor = 1.0

    def draw(self):
        glColor3f(0.0, 1.0, 0.0)  # Green player
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], 0.0)
        glScalef(1.0, self.squish_factor, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(-self.size, -self.size)
        glVertex2f(self.size, -self.size)
        glVertex2f(self.size, self.size)
        glVertex2f(-self.size, self.size)
        glEnd()
        glPopMatrix()

# Obstacle class
class Obstacle:
    def __init__(self, x, y, width, height):
        self.position = np.array([x, y], dtype=np.float32)
        self.width = width
        self.height = height

    def draw(self):
        glColor3f(1.0, 0.0, 0.0)  # Red obstacles
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], 0.0)
        glBegin(GL_QUADS)
        glVertex2f(-self.width / 2, -self.height / 2)
        glVertex2f(self.width / 2, -self.height / 2)
        glVertex2f(self.width / 2, self.height / 2)
        glVertex2f(-self.width / 2, self.height / 2)
        glEnd()
        glPopMatrix()

# Create player and obstacles
player = Player()
obstacles = [Obstacle(random.uniform(-0.8, 0.8), random.uniform(-0.8, 0.8), 0.1, 0.1) for _ in range(5)]

# Render function
def render(particles, colors, player, obstacles):
    glClear(GL_COLOR_BUFFER_BIT)

    # Render particles
    glUseProgram(shader_program)
    glEnable(GL_POINT_SPRITE)
    glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, particles)
    glUniform4f(glGetUniformLocation(shader_program, "color"), 1.0, 0.5, 0.0, 1.0)
    glDrawArrays(GL_POINTS, 0, len(particles))
    glDisableVertexAttribArray(0)
    glDisable(GL_POINT_SPRITE)
    glUseProgram(0)

    # Render player
    player.draw()

    # Render obstacles
    for obstacle in obstacles:
        obstacle.draw()

    pygame.display.flip()

# Main game loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            running = False

    keys = pygame.key.get_pressed()
    direction = np.array([0.0, 0.0])
    if keys[K_LEFT]:
        direction[0] -= 1
    if keys[K_RIGHT]:
        direction[0] += 1
    if keys[K_UP]:
        direction[1] += 1
    if keys[K_DOWN]:
        direction[1] -= 1
    if np.any(direction):
        direction = direction / np.linalg.norm(direction)
        player.move(direction)
        particle_system.emit(player.position.copy(), direction * -0.02)

    dt = clock.tick(60) / 1000.0
    particle_system.update(dt)
    render(particle_system.particles[particle_system.alive], particle_system.colors[particle_system.alive], player, obstacles)

pygame.quit()
