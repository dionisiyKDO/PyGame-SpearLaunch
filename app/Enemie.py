import pygame
import math
from app.settings import *

class Enemie:
    def __init__(self, x, y, hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        self.radius = DUMMY_RADIUS
        self.color = DUMMY_COLOR
        self.killed = False

    def draw(self, display):
        pygame.draw.circle(display, self.color, (int(self.x), int(self.y)), self.radius)
        charge_text = self.font.render(f"{self.hp}", True, WHITE)
        charge_text_rect = charge_text.get_rect(center=(int(self.x), int(self.y)))
        display.blit(charge_text, charge_text_rect)

    def check_collision(self, spear):
        if not self.killed and spear.thrown and not spear.destroyed:
            distance = math.sqrt((self.x - spear.x) ** 2 + (self.y - spear.y) ** 2)
            max_distance = self.radius + spear.length / 2
            if distance <= max_distance:
                # self.killed = True
                self.hp -= spear.charge_value
                spear.destroy()
                if self.hp <= 0:
                    self.hp = 0
                    self.killed = True
                    self.color = KILLED_COLOR
                return True
        return False