import pygame

from settings import CHARACTER_COLOR, CHARACTER_RADIUS

class Character:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def draw(self, display):
        pygame.draw.circle(display, CHARACTER_COLOR, (int(self.x), int(self.y)), CHARACTER_RADIUS)
