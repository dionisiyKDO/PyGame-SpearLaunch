# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
RED = (255, 0, 0)
CRIMSON = (220, 20, 60)
BLUE = (0, 0, 255)

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 144

# Main character properties
CHARACTER_POS = [100, SCREEN_HEIGHT - 100]  # Changed to list for mutable position
CHARACTER_COLOR = BLACK
CHARACTER_RADIUS = 15
CHARACTER_SPEED = 5  # Movement speed of the character

# Spear properties
SPEAR_COLOR = BLACK
SPEAR_WIDTH = 5
SPEAR_HEIGHT = 50
SPEAR_MAX_SPEED = 50
CHARGE_TIME = 1.5  # Charge time in seconds
CHARGE_VALUE_MAX = 100

# Zoom properties
ZOOM_SCALE = 1.1  # Maximum zoom scale
zoom_level = 1.0

# Game properties
NUM_DUMMIES = 10
DUMMY_RADIUS = 20
DUMMY_SPEED = 10
DUMMY_COLOR = CRIMSON
HIT_COLOR = BLUE
