import pygame
import math
import sys
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flying Spear")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Main character properties
CHARACTER_POS = (100, SCREEN_HEIGHT - 100)
CHARACTER_COLOR = BLACK
CHARACTER_RADIUS = 20

# Spear properties
SPEAR_COLOR = BLACK
SPEAR_WIDTH = 5
SPEAR_HEIGHT = 50
SPEAR_MAX_SPEED = 25
CHARGE_TIME = 1.5  # Charge time in seconds

# Zoom properties
ZOOM_SCALE = 1.1  # Maximum zoom scale
zoom_level = 1.0

# Font
font = pygame.font.Font(None, 74)

class Spear:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.vx = 0
        self.vy = 0
        self.thrown = False
        self.charge_start_time = None
        self.length = SPEAR_HEIGHT

    def start_charging(self):
        self.charge_start_time = time.time()

    def charge(self):
        if self.charge_start_time:
            current_time = time.time()
            elapsed_time = current_time - self.charge_start_time
            self.speed = min(SPEAR_MAX_SPEED, SPEAR_MAX_SPEED * (elapsed_time / CHARGE_TIME))
            self.length = SPEAR_HEIGHT + (SPEAR_HEIGHT * 3 * (elapsed_time / CHARGE_TIME))  # Stretching effect
            if elapsed_time >= CHARGE_TIME:
                self.throw()

    def follow_cursor(self, cursor_x, cursor_y):
        self.angle = math.degrees(math.atan2(self.y - cursor_y, cursor_x - self.x))

    def throw(self):
        self.vx = math.cos(math.radians(self.angle)) * self.speed
        self.vy = -math.sin(math.radians(self.angle)) * self.speed
        self.thrown = True

    def update(self):
        if self.thrown:
            self.x += self.vx
            self.y += self.vy
            # Gravity effect
            self.vy += 0.5

    def draw(self, screen):
        spear_surface = pygame.Surface((self.length, SPEAR_WIDTH), pygame.SRCALPHA)
        spear_surface.fill(SPEAR_COLOR)
        rotated_spear = pygame.transform.rotate(spear_surface, self.angle)
        screen.blit(rotated_spear, rotated_spear.get_rect(center=(self.x, self.y)))

def draw_character(screen):
    pygame.draw.circle(screen, CHARACTER_COLOR, CHARACTER_POS, CHARACTER_RADIUS)

def apply_zoom(surface, scale):
    width, height = surface.get_size()
    zoomed_surface = pygame.transform.smoothscale(surface, (int(width * scale), int(height * scale)))
    return zoomed_surface

def main():
    global zoom_level

    running = True
    spear = None
    while running:
        cursor_x, cursor_y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and spear is None:
                spear = Spear(CHARACTER_POS[0] + 30, CHARACTER_POS[1] - 30)
                spear.start_charging()

        screen.fill(WHITE)
        draw_character(screen)

        if spear:
            if not spear.thrown:
                spear.follow_cursor(cursor_x, cursor_y)
                spear.charge()
                elapsed_time = time.time() - spear.charge_start_time
                zoom_level = 1.0 + (ZOOM_SCALE - 1.0) * min(elapsed_time / CHARGE_TIME, 1)
            spear.update()
            spear.draw(screen)
            if spear.thrown and (spear.y > SCREEN_HEIGHT or spear.x > SCREEN_WIDTH):
                spear = None
                zoom_level = 1.0

        # Apply zoom effect
        zoomed_screen = apply_zoom(screen, zoom_level)
        screen.blit(zoomed_screen, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
