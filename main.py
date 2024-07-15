import sys
import math
import time

from settings import *

import pygame
import moderngl
import numpy as np


pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flying Spear")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


class Character:
    def __init__(self, x = CHARACTER_POS[0], y = CHARACTER_POS[1]):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def draw(self, screen):
        pygame.draw.circle(screen, CHARACTER_COLOR, (int(self.x), int(self.y)), CHARACTER_RADIUS)


class Spear:
    def __init__(self, character):
        self.x = character.x + 30
        self.y = character.y - 30
        self.angle = 0
        self.speed = 0
        self.vx = 0
        self.vy = 0
        self.thrown = False
        self.charge_start_time = None
        self.length = SPEAR_HEIGHT
        self.charge_value = 0

    def start_charging(self):
        self.charge_start_time = time.time()

    def charge(self):
        if self.charge_start_time:
            elapsed_time = time.time() - self.charge_start_time
            self.speed = min(SPEAR_MAX_SPEED, SPEAR_MAX_SPEED * (elapsed_time / CHARGE_TIME))
            self.length = SPEAR_HEIGHT + (SPEAR_HEIGHT * 3 * (elapsed_time / CHARGE_TIME))  # Stretching effect
            self.charge_value = min(CHARGE_VALUE_MAX, int(100 * (elapsed_time / CHARGE_TIME)))  # Max charge value of 100
            if elapsed_time >= CHARGE_TIME:
                self.throw()

    def follow_cursor(self, cursor_x, cursor_y):
        self.angle = math.degrees(math.atan2(self.y - cursor_y, cursor_x - self.x))

    # def throw(self):
    #     self.vx = math.cos(math.radians(self.angle)) * self.speed
    #     self.vy = -math.sin(math.radians(self.angle)) * self.speed
    #     self.thrown = True

    # def update(self):
    #     if self.thrown:
    #         self.x += self.vx
    #         self.y += self.vy
            
    def throw(self):
        initial_speed = self.speed * 4.0  # Example: starting with double the speed
        self.vx = math.cos(math.radians(self.angle)) * initial_speed
        self.vy = -math.sin(math.radians(self.angle)) * initial_speed
        self.thrown = True

    def update(self):
        if self.thrown:
            if abs(self.vx) > self.speed or abs(self.vy) > self.speed:
                # Apply deceleration to simulate slowing down after initial impulse
                deceleration = 0.1  # Adjust as needed
                self.vx *= (1 - deceleration)
                self.vy *= (1 - deceleration)
                print(f"Velocity (vx, vy): ({self.vx}, {self.vy})")
            else:
                # Once velocity reaches or falls below self.speed, maintain steady speed
                self.vx = math.cos(math.radians(self.angle)) * self.speed
                self.vy = -math.sin(math.radians(self.angle)) * self.speed
                print(f"Steady Velocity (vx, vy): ({self.vx}, {self.vy})")

            self.x += self.vx
            self.y += self.vy


    def draw(self, screen):
        spear_surface = pygame.Surface((self.length, SPEAR_WIDTH), pygame.SRCALPHA)
        spear_surface.fill(SPEAR_COLOR)
        rotated_spear = pygame.transform.rotate(spear_surface, self.angle)
        screen.blit(rotated_spear, rotated_spear.get_rect(center=(self.x, self.y)))

def draw_charge_indicator(screen, charge_value):
    charge_indicator_width = int((charge_value / 100) * SCREEN_WIDTH)
    pygame.draw.rect(screen, RED, (0, SCREEN_HEIGHT - 20, charge_indicator_width, 20))
    charge_text = font.render(f"Charge: {charge_value}", True, BLACK)
    screen.blit(charge_text, (10, SCREEN_HEIGHT - 60))


def apply_zoom(surface, scale):
    width, height = surface.get_size()
    zoomed_surface = pygame.transform.smoothscale(surface, (int(width * scale), int(height * scale)))
    return zoomed_surface

def handle_events(character, spear):
    global zoom_level

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and spear is None:
            spear = Spear(character)
            spear.start_charging()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and spear and not spear.thrown:
            spear.throw()
            zoom_level = 1.0

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        character.move(-CHARACTER_SPEED, 0)
    if keys[pygame.K_d]:
        character.move(CHARACTER_SPEED, 0)
    if keys[pygame.K_w]:
        character.move(0, -CHARACTER_SPEED)
    if keys[pygame.K_s]:
        character.move(0, CHARACTER_SPEED)

    return spear, True

def main():
    global zoom_level

    running = True
    character = Character(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    spear = None

    while running:
        cursor_x, cursor_y = pygame.mouse.get_pos()
        spear, running = handle_events(character, spear)

        screen.fill(WHITE)
        character.draw(screen)

        if spear:
            if not spear.thrown:
                spear.follow_cursor(cursor_x, cursor_y)
                spear.charge()
                draw_charge_indicator(screen, spear.charge_value)
            spear.update()
            spear.draw(screen)
            if spear.thrown and (spear.y > SCREEN_HEIGHT or spear.x > SCREEN_WIDTH or spear.y < 0 or spear.x < 0):
                spear = None

        # Apply zoom effect
        zoomed_screen = apply_zoom(screen, zoom_level)
        screen.blit(zoomed_screen, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
