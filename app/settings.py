# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
RED = (255, 0, 0)
CRIMSON = (220, 20, 60)
BLUE = (0, 0, 255)

# Game properties
BACKGROUND_COLOR = WHITE
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 288
FONT_NAME = None
FONT_SIZE = 36


# Main character properties
CHARACTER_POS = [100, SCREEN_HEIGHT - 100] 
CHARACTER_COLOR = BLACK
CHARACTER_RADIUS = 15
CHARACTER_SPEED = 10

# Spear properties
SPEAR_COLOR = BLACK
SPEAR_WIDTH = 5
SPEAR_HEIGHT = 50
SPEAR_MAX_SPEED = 60  # 50
SPEAR_IMPULSE = 4.5 # 4
CHARGE_TIME = 1.5  # Charge time in seconds
CHARGE_VALUE_MAX = 100

# Enemies properties
NUM_ENEMIES = 10
DUMMY_RADIUS = 23
DUMMY_SPEED = 10
DUMMY_COLOR = CRIMSON
DUMMY_SPAWN_INTERVAL = 0.4
KILLED_COLOR = GREY
