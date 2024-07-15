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
RED = (255, 0, 0)

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Main character properties
CHARACTER_POS = (100, SCREEN_HEIGHT - 100)
CHARACTER_COLOR = BLACK
CHARACTER_RADIUS = 5

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
font = pygame.font.Font(None, 36)

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
        self.charge_value = 0

    def start_charging(self):
        self.charge_start_time = time.time()

    def charge(self):
        if self.charge_start_time:
            elapsed_time = time.time() - self.charge_start_time
            self.speed = min(SPEAR_MAX_SPEED, SPEAR_MAX_SPEED * (elapsed_time / CHARGE_TIME))
            self.length = SPEAR_HEIGHT + (SPEAR_HEIGHT * 3 * (elapsed_time / CHARGE_TIME))  # Stretching effect
            self.charge_value = min(100, int(100 * (elapsed_time / CHARGE_TIME)))  # Max charge value of 100
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

def handle_events(spear):
    global zoom_level

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and spear is None:
            spear = Spear(CHARACTER_POS[0] + 30, CHARACTER_POS[1] - 30)
            spear.start_charging()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and spear and not spear.thrown:
            spear.throw()
            zoom_level = 1.0
    return spear, True

def main():
    global zoom_level

    running = True
    spear = None
    charge_indicator_width = 0
    while running:
        cursor_x, cursor_y = pygame.mouse.get_pos()
        spear, running = handle_events(spear)

        screen.fill(WHITE)
        draw_character(screen)

        if spear:
            if not spear.thrown:
                spear.follow_cursor(cursor_x, cursor_y)
                spear.charge()
                charge_indicator_width = int((spear.charge_value / 100) * SCREEN_WIDTH)
                # Display charge value
                charge_text = font.render(f"Charge: {spear.charge_value}", True, BLACK)
                screen.blit(charge_text, (10, SCREEN_HEIGHT - 60))
            spear.update()
            spear.draw(screen)
            if spear.thrown and (spear.y > SCREEN_HEIGHT or spear.x > SCREEN_WIDTH):
                spear = None
                charge_indicator_width = 0

        # Draw charge indicator
        pygame.draw.rect(screen, RED, (0, SCREEN_HEIGHT - 20, charge_indicator_width, 20))

        # Apply zoom effect
        zoomed_screen = apply_zoom(screen, zoom_level)
        screen.blit(zoomed_screen, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
