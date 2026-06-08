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
MIN_MULTIPLAYER_PLAYERS = 2
MAX_MULTIPLAYER_PLAYERS = 6
MULTIPLAYER_COUNTDOWN_SECONDS = 5
MULTIPLAYER_LEADERBOARD_SECONDS = 7

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

# Rarity system
RARITY_COMMON = "common"
RARITY_RARE = "rare"
RARITY_EPIC = "epic"
RARITY_LEGENDARY = "legendary"

RARITY_COLORS = {
    RARITY_COMMON:    (180, 180, 180),
    RARITY_RARE:      (60, 140, 255),
    RARITY_EPIC:      (180, 60, 255),
    RARITY_LEGENDARY: (255, 200, 0),
}

RARITY_LABELS = {
    RARITY_COMMON:    "BEZNY",
    RARITY_RARE:      "VZACNY",
    RARITY_EPIC:      "EPICKY",
    RARITY_LEGENDARY: "LEGENDARNY",
}

# Drop weights per rarity
RARITY_WEIGHTS = {
    RARITY_COMMON:    55,
    RARITY_RARE:      28,
    RARITY_EPIC:      13,
    RARITY_LEGENDARY: 4,
}

# Pity thresholds (guaranteed after N boxes)
PITY_EPIC_THRESHOLD = 10
PITY_LEGENDARY_THRESHOLD = 30
PITY_FILE = "pity.txt"

# Duplicate refund per rarity (flat coin amounts)
RARITY_REFUND = {
    RARITY_COMMON:    25,
    RARITY_RARE:      50,
    RARITY_EPIC:      80,
    RARITY_LEGENDARY: 150,
}

# Car skins: (name, body_color, spoiler_color, wing_color, helmet_color, rarity)
CAR_SKINS = [
    {"name": "FERRARI",      "body": (220, 50, 50),   "spoiler": (150, 0, 0),   "wing": (50, 50, 50),  "helmet": (255, 255, 255), "rarity": RARITY_COMMON},
    {"name": "MCLAREN",      "body": (255, 140, 0),    "spoiler": (200, 100, 0), "wing": (40, 40, 40),  "helmet": (255, 200, 0),   "rarity": RARITY_RARE},
    {"name": "MERCEDES",     "body": (0, 200, 200),    "spoiler": (0, 140, 140), "wing": (30, 30, 30),  "helmet": (200, 255, 255), "rarity": RARITY_RARE},
    {"name": "RED BULL",     "body": (30, 30, 180),    "spoiler": (10, 10, 120), "wing": (50, 50, 50),  "helmet": (255, 255, 0),   "rarity": RARITY_EPIC},
    {"name": "ALPINE",       "body": (0, 120, 255),    "spoiler": (0, 80, 180),  "wing": (40, 40, 40),  "helmet": (255, 100, 100), "rarity": RARITY_EPIC},
    {"name": "ASTON MARTIN", "body": (0, 100, 60),     "spoiler": (0, 70, 40),   "wing": (30, 30, 30),  "helmet": (200, 200, 200), "rarity": RARITY_LEGENDARY},
    {"name": "WILLIAMS",     "body": (255, 255, 255),  "spoiler": (200, 200, 200),"wing": (50, 50, 50), "helmet": (0, 100, 255),   "rarity": RARITY_LEGENDARY},
    {"name": "HAAS",         "body": (180, 180, 180),  "spoiler": (120, 120, 120),"wing": (40, 40, 40), "helmet": (220, 50, 50),   "rarity": RARITY_LEGENDARY},
    {"name": "ALFA ROMEO",   "body": (180, 30, 30),    "spoiler": (120, 20, 20), "wing": (50, 50, 50),  "helmet": (255, 255, 255), "rarity": RARITY_RARE},
    {"name": "ALPHATAURI",   "body": (200, 220, 255),  "spoiler": (150, 170, 220),"wing": (40, 40, 50), "helmet": (100, 150, 255), "rarity": RARITY_COMMON},
    {"name": "PORSCHE",      "body": (255, 200, 0),    "spoiler": (200, 160, 0), "wing": (40, 40, 40),  "helmet": (255, 255, 200), "rarity": RARITY_LEGENDARY},
    {"name": "LAMBORGHINI",  "body": (100, 200, 0),    "spoiler": (60, 140, 0),  "wing": (30, 30, 30),  "helmet": (200, 255, 100), "rarity": RARITY_LEGENDARY},
]

SELECTED_SKIN_INDEX = 0

# Lootbox & coins
LOOTBOX_COST = 100
EFFECT_BOX_COST = 75
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
    {"name": "ADMIN", "coins": 1000, "price": "ZDARMA", "admin": True},
]

# --- Gameplay Effects System ---
EFFECT_EXHAUST = "exhaust"
EFFECT_TRAIL = "trail"
EFFECT_GLOW = "glow"
EFFECT_AURA = "aura"
EFFECT_BOOST = "boost"

EFFECT_TYPE_LABELS = {
    EFFECT_EXHAUST: "VYFUK",
    EFFECT_TRAIL: "STOPY",
    EFFECT_GLOW: "ZIARA",
    EFFECT_AURA: "AURA",
    EFFECT_BOOST: "BOOST",
}

# 5 types x 4 color variants = 20 effects
EFFECTS = [
    # Exhaust (index 0-3)
    {"type": EFFECT_EXHAUST, "color": (255, 100, 30),  "name": "OHEŇ",     "rarity": RARITY_COMMON},
    {"type": EFFECT_EXHAUST, "color": (80, 160, 255),  "name": "ĽADOVÝ",   "rarity": RARITY_RARE},
    {"type": EFFECT_EXHAUST, "color": (180, 60, 255),  "name": "TOXICKÝ",  "rarity": RARITY_EPIC},
    {"type": EFFECT_EXHAUST, "color": (255, 215, 0),   "name": "ZLATÝ",    "rarity": RARITY_LEGENDARY},
    # Trail (index 4-7)
    {"type": EFFECT_TRAIL, "color": (200, 200, 200),   "name": "KOTÚČE",   "rarity": RARITY_COMMON},
    {"type": EFFECT_TRAIL, "color": (255, 50, 50),     "name": "ČERVENÉ",  "rarity": RARITY_RARE},
    {"type": EFFECT_TRAIL, "color": (0, 200, 255),     "name": "NEÓN",     "rarity": RARITY_EPIC},
    {"type": EFFECT_TRAIL, "color": (255, 215, 0),     "name": "ZLATÉ",    "rarity": RARITY_LEGENDARY},
    # Glow (index 8-11)
    {"type": EFFECT_GLOW, "color": (255, 255, 255),    "name": "BIELY",    "rarity": RARITY_COMMON},
    {"type": EFFECT_GLOW, "color": (0, 150, 255),      "name": "MODRÝ",    "rarity": RARITY_RARE},
    {"type": EFFECT_GLOW, "color": (200, 0, 255),      "name": "FIALOVÝ",  "rarity": RARITY_EPIC},
    {"type": EFFECT_GLOW, "color": (255, 200, 0),      "name": "KRÁĽOVSKÝ","rarity": RARITY_LEGENDARY},
    # Aura (index 12-15)
    {"type": EFFECT_AURA, "color": (200, 200, 200),    "name": "VIETOR",   "rarity": RARITY_COMMON},
    {"type": EFFECT_AURA, "color": (0, 255, 150),      "name": "SMRŠŤ",    "rarity": RARITY_RARE},
    {"type": EFFECT_AURA, "color": (255, 80, 80),      "name": "INFERNO",  "rarity": RARITY_EPIC},
    {"type": EFFECT_AURA, "color": (255, 215, 0),      "name": "AURA",     "rarity": RARITY_LEGENDARY},
    # Boost (index 16-19)
    {"type": EFFECT_BOOST, "color": (255, 255, 255),   "name": "ISKRY",    "rarity": RARITY_COMMON},
    {"type": EFFECT_BOOST, "color": (0, 200, 255),     "name": "ELEKTRIKA","rarity": RARITY_RARE},
    {"type": EFFECT_BOOST, "color": (255, 0, 100),     "name": "RUŽOVÝ",   "rarity": RARITY_EPIC},
    {"type": EFFECT_BOOST, "color": (255, 215, 0),     "name": "BLESK",    "rarity": RARITY_LEGENDARY},
]

# Starter effects: one common per type auto-unlocked
STARTER_EFFECTS = [0, 4, 8, 12, 16]
EFFECTS_FILE = "unlocked_effects.txt"
EQUIPPED_EFFECTS_FILE = "equipped_effects.txt"
