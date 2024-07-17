import pygame
import math
from settings import *

class Enemie:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = DUMMY_RADIUS
        self.color = DUMMY_COLOR
        self.hit = False

    def draw(self, display):
        pygame.draw.circle(display, self.color, (int(self.x), int(self.y)), self.radius)

    def check_collision(self, spear):
        if not self.hit and spear.thrown and not spear.destroyed:
            distance = math.sqrt((self.x - spear.x) ** 2 + (self.y - spear.y) ** 2)
            max_distance = self.radius + spear.length / 2
            if distance <= max_distance:
                self.hit = True
                spear.destroy()
                self.color = HIT_COLOR
                return True
        return False