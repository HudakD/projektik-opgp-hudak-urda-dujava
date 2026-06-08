WIDTH = 1280
HEIGHT = 720
FPS = 60

ROAD_WIDTH = 400
SCROLL_SPEED = 7
INITIAL_SCROLL_SPEED = 7
MAX_SCROLL_SPEED = 15

ROAD_COLOR = (110, 110, 110)
GRASS_COLOR = (20, 150, 20)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
YELLOW = (255, 255, 0)

PLAYER_COLOR = (220, 50, 50)
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 90

OBSTACLE_COLOR = (50, 50, 220)
OBSTACLE_WIDTH = 60
OBSTACLE_HEIGHT = 90

DIFFICULTY_INCREASE_INTERVAL = 100
SPEED_INCREASE = 0.5
OBSTACLE_SPAWN_INCREASE = 1

SCORE_FILE = "highscores.txt"
MAX_HIGHSCORES = 20

MULTIPLAYER_PORT = 5000
NETWORK_TICK_SECONDS = 1 / FPS

UI_BG_DARK = (12, 12, 20)
UI_PANEL_BG = (20, 25, 40)
UI_ACCENT = (0, 255, 200)
UI_ACCENT_HOVER = (150, 255, 230)
UI_WARNING = (255, 60, 80)
UI_GOLD = (255, 215, 0)
UI_TEXT_MAIN = (245, 245, 255)
UI_TEXT_DIM = (140, 140, 160)

GAUGE_LOW = (0, 255, 128)
GAUGE_MID = (255, 200, 0)
GAUGE_HIGH = (255, 50, 50)

# Audio nastavenia
SOUND_ON = True
SFX_VOLUME = 0.6
ENGINE_VOLUME = 0.2

# Car skins: (name, body_color, spoiler_color, wing_color, helmet_color)
CAR_SKINS = [
    {"name": "FERRARI",    "body": (220, 50, 50),   "spoiler": (150, 0, 0),   "wing": (50, 50, 50),  "helmet": (255, 255, 255)},
    {"name": "MCLAREN",    "body": (255, 140, 0),    "spoiler": (200, 100, 0), "wing": (40, 40, 40),  "helmet": (255, 200, 0)},
    {"name": "MERCEDES",   "body": (0, 200, 200),    "spoiler": (0, 140, 140), "wing": (30, 30, 30),  "helmet": (200, 255, 255)},
    {"name": "RED BULL",   "body": (30, 30, 180),    "spoiler": (10, 10, 120), "wing": (50, 50, 50),  "helmet": (255, 255, 0)},
    {"name": "ALPINE",     "body": (0, 120, 255),    "spoiler": (0, 80, 180),  "wing": (40, 40, 40),  "helmet": (255, 100, 100)},
    {"name": "ASTON MARTIN","body": (0, 100, 60),    "spoiler": (0, 70, 40),   "wing": (30, 30, 30),  "helmet": (200, 200, 200)},
    {"name": "WILLIAMS",   "body": (255, 255, 255),  "spoiler": (200, 200, 200),"wing": (50, 50, 50), "helmet": (0, 100, 255)},
    {"name": "HAAS",       "body": (180, 180, 180),  "spoiler": (120, 120, 120),"wing": (40, 40, 40), "helmet": (220, 50, 50)},
]

SELECTED_SKIN_INDEX = 0

# Lootbox & coins
LOOTBOX_COST = 100
COINS_FILE = "coins.txt"
COIN_SPAWN_CHANCE = 30
COIN_VALUE = 10
COIN_SIZE = 24
DUPLICATE_REFUND_PERCENT = 0.50

# Paywall packages (visual only - not real payments)
COIN_PACKAGES = [
    {"name": "STARTER", "coins": 100, "price": "0.99 EUR"},
    {"name": "POPULAR", "coins": 500, "price": "3.99 EUR"},
    {"name": "MEGA", "coins": 1500, "price": "9.99 EUR"},
    {"name": "ULTIMATE", "coins": 5000, "price": "24.99 EUR"},
]