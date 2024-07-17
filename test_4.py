# IMPORTANT
# example rogue like

import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Classes

class Spear:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.components = []

    def add_component(self, component):
        self.components.append(component)

    def update(self):
        for component in self.components:
            component.update(self)

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), 10)

    def on_hit(self, target):
        for component in self.components:
            component.on_hit(self, target)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 3

    def draw(self, screen):
        pygame.draw.rect(screen, RED, pygame.Rect(self.x, self.y, 20, 20))
        

    def take_damage(self, damage):
        self.hp -= damage

# Components

class MultiplyingSpear:
    def __init__(self, multiplier):
        self.multiplier = multiplier

    def on_hit(self, spear, target):
        for _ in range(self.multiplier - 1):
            new_spear = Spear(spear.x, spear.y)
            new_spear.components = spear.components.copy()
            spears.append(new_spear)

class ElementalSpear:
    def __init__(self, element_color, damage):
        self.element_color = element_color
        self.damage = damage

    def on_hit(self, spear, target):
        target.take_damage(self.damage)

# Game setup

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Enhanced Roguelike Spear Game")

clock = pygame.time.Clock()

spears = []
enemies = [Enemy(random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50)) for _ in range(5)]

player_spear = Spear(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
player_spear.add_component(MultiplyingSpear(3))
player_spear.add_component(ElementalSpear(RED, 1))

# Game loop

running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_spear.x -= 5
    if keys[pygame.K_RIGHT]:
        player_spear.x += 5
    if keys[pygame.K_UP]:
        player_spear.y -= 5
    if keys[pygame.K_DOWN]:
        player_spear.y += 5

    if keys[pygame.K_SPACE]:
        spears.append(Spear(player_spear.x, player_spear.y))
        for spear in spears:
            spear.update()

    for spear in spears:
        spear.draw(screen)

    for enemy in enemies:
        enemy.draw(screen)

        # Check collision between spear and enemy
        for spear in spears:
            if pygame.Rect(spear.x - 10, spear.y - 10, 20, 20).colliderect(pygame.Rect(enemy.x, enemy.y, 20, 20)):
                spear.on_hit(enemy)
                spears.remove(spear)

        # Remove defeated enemies
        if enemy.hp <= 0:
            enemies.remove(enemy)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
