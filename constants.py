SCREEN_WIDTH  = 1000
SCREEN_HEIGHT = 600
FPS           = 60
GRAVITY       = 0.55
LEVEL_WIDTH   = 6000

# Level-specific widths
LEVEL_WIDTHS = [3000, 4000, 6000]

# Enemy health per level [InsectEnemy, ReptileEnemy]
ENEMY_HEALTH = [
    [20, 35],    # Level 1
    [60, 90],    # Level 2
    [110, 160],  # Level 3
]

LEVEL_TEMPLATES = [
    {
        "width": 3000,  # Level 1: Half width for beginners
        "platforms": [
            (0, SCREEN_HEIGHT - 60, 3000),    # Ground platform
            (330, SCREEN_HEIGHT - 180, 200),  # Wide platform, small gap from ground
            (700, SCREEN_HEIGHT - 170, 180),  # Slightly lower, wide platform
            (1075, SCREEN_HEIGHT - 185, 220), # Slightly higher, widest platform
            (1450, SCREEN_HEIGHT - 175, 190), # Medium height, wide platform
            (1825, SCREEN_HEIGHT - 180, 210), # Standard height, wide platform
            (2200, SCREEN_HEIGHT - 170, 180), # Slightly lower, wide platform
            (2575, SCREEN_HEIGHT - 185, 200), # Slightly higher, wide platform
        ],
        "enemies": [
            (310, SCREEN_HEIGHT - 140, "reptile"),
            (610, SCREEN_HEIGHT - 210, "insect"),
            (890, SCREEN_HEIGHT - 170, "reptile"),
            (1170, SCREEN_HEIGHT - 140, "insect"),
            (1450, SCREEN_HEIGHT - 180, "reptile"),
            (1730, SCREEN_HEIGHT - 120, "insect"),
            (2010, SCREEN_HEIGHT - 200, "reptile"),
            (2290, SCREEN_HEIGHT - 160, "insect"),
        ],
        "crates": [
            160,
            (380, SCREEN_HEIGHT - 180 - 36),
            670,
            (1120, SCREEN_HEIGHT - 185 - 36),
            1205,
            (1490, SCREEN_HEIGHT - 175 - 36),
            1765,
            (2575, SCREEN_HEIGHT - 185 - 36),
        ],
        "door": (2880, None),
    },
    {
        "width": 4000,  # Level 2: Intermediate with high platforms for insect combat
        "platforms": [
            (0, SCREEN_HEIGHT - 60, 4000),    # Ground platform
            (400, SCREEN_HEIGHT - 220, 150),  # Medium platform, higher
            (850, SCREEN_HEIGHT - 150, 130),  # Lower platform
            (1300, SCREEN_HEIGHT - 260, 170), # Much higher platform
            (1750, SCREEN_HEIGHT - 170, 140), # Medium height
            (2200, SCREEN_HEIGHT - 230, 160), # Higher platform
            (2650, SCREEN_HEIGHT - 160, 130), # Lower platform
            (3100, SCREEN_HEIGHT - 250, 150), # High platform
            (3550, SCREEN_HEIGHT - 180, 140), # Medium height
            # High platforms for insect combat (around y = 280-320)
            (500, SCREEN_HEIGHT - 300, 120),  # High platform for insects
            (1500, SCREEN_HEIGHT - 310, 140), # High platform for insects
            (2700, SCREEN_HEIGHT - 290, 130), # High platform for insects
            (3400, SCREEN_HEIGHT - 320, 150), # High platform for insects
        ],
        "enemies": [
            (440, SCREEN_HEIGHT - 130, "insect"),
            (900, SCREEN_HEIGHT - 160, "reptile"),
            (1400, SCREEN_HEIGHT - 230, "insect"),
            (1900, SCREEN_HEIGHT - 200, "reptile"),
            (2300, SCREEN_HEIGHT - 170, "insect"),
            (2800, SCREEN_HEIGHT - 210, "reptile"),
            (3300, SCREEN_HEIGHT - 160, "insect"),
            (3800, SCREEN_HEIGHT - 240, "reptile"),
        ],
        "crates": [
            200,
            (420, SCREEN_HEIGHT - 220 - 36),
            (520, SCREEN_HEIGHT - 300 - 36),
            1050,
            (1500, SCREEN_HEIGHT - 310 - 36),
            1900,
            (2300, SCREEN_HEIGHT - 230 - 36),
            2850,
        ],
        "door": (3880, None),
    },
    {
        "width": 6000,  # Level 3: Full distance with many high platforms
        "platforms": [
            (0, SCREEN_HEIGHT - 60, 6000),      # Ground platform
            (420, SCREEN_HEIGHT - 220, 100),    # Narrow platform, medium height
            (900, SCREEN_HEIGHT - 260, 120),    # Narrow platform, high
            (1420, SCREEN_HEIGHT - 200, 90),    # Very narrow, medium height
            (1920, SCREEN_HEIGHT - 280, 130),   # Narrow platform, very high
            (2450, SCREEN_HEIGHT - 210, 100),   # Narrow platform, medium height
            (2990, SCREEN_HEIGHT - 250, 110),   # Narrow platform, high
            (3450, SCREEN_HEIGHT - 190, 85),    # Very narrow, low
            (3950, SCREEN_HEIGHT - 270, 120),   # Narrow platform, very high
            (4450, SCREEN_HEIGHT - 220, 95),    # Very narrow, medium height
            (4950, SCREEN_HEIGHT - 240, 110),   # Narrow platform, high
            (5450, SCREEN_HEIGHT - 210, 100),   # Narrow platform, medium height
            # High platforms for insect combat (y = 320-380)
            (600, SCREEN_HEIGHT - 350, 110),    # Very high platform
            (1600, SCREEN_HEIGHT - 340, 120),   # Very high platform
            (2600, SCREEN_HEIGHT - 360, 100),   # Very high platform
            (3600, SCREEN_HEIGHT - 330, 130),   # Very high platform
            (4600, SCREEN_HEIGHT - 350, 110),   # Very high platform
            (5600, SCREEN_HEIGHT - 340, 120),   # Very high platform
        ],
        "enemies": [
            (420, SCREEN_HEIGHT - 140, "insect"),
            (830, SCREEN_HEIGHT - 200, "reptile"),
            (1240, SCREEN_HEIGHT - 170, "insect"),
            (1650, SCREEN_HEIGHT - 240, "reptile"),
            (2060, SCREEN_HEIGHT - 180, "insect"),
            (2470, SCREEN_HEIGHT - 160, "reptile"),
            (2880, SCREEN_HEIGHT - 200, "insect"),
            (3290, SCREEN_HEIGHT - 230, "reptile"),
        ],
        "crates": [
            280,
            (620, SCREEN_HEIGHT - 350 - 36),
            (950, SCREEN_HEIGHT - 260 - 36),
            1280,
            (1660, SCREEN_HEIGHT - 340 - 36),
            2060,
            (2460, SCREEN_HEIGHT - 210 - 36),
            2860,
            3260,
            (4060, SCREEN_HEIGHT - 270 - 36),
            5340,
        ],
        "door": (5880, None),
    },
]

WEAPON_POOL_STAGE2 = [
    {"name": "Stick",  "damage": 11, "range": 55,  "durability": 15, "color": (139, 90, 43)},
    {"name": "Sword",  "damage": 22, "range": 75,  "durability": 20, "color": (180, 180, 180)},
    {"name": "Hammer", "damage": 30, "range": 50,  "durability": 10, "color": (60, 60, 60)},
    {"name": "Spear",  "damage": 18, "range": 100, "durability": 18, "color": (230, 120, 30)},
    {"name": "Axe",    "damage": 26, "range": 60,  "durability": 12, "color": (180, 100, 40)},
    {"name": "Dagger", "damage": 14, "range": 45,  "durability": 25, "color": (200, 200, 230)},
]

WEAPON_POOL_STAGE3 = [
    {"name": "Stick",  "damage": 14, "range": 55,  "durability": 15, "color": (139, 90, 43)},
    {"name": "Sword",  "damage": 29, "range": 75,  "durability": 20, "color": (180, 180, 180)},
    {"name": "Hammer", "damage": 39, "range": 50,  "durability": 10, "color": (60, 60, 60)},
    {"name": "Spear",  "damage": 23, "range": 100, "durability": 18, "color": (230, 120, 30)},
    {"name": "Axe",    "damage": 34, "range": 60,  "durability": 12, "color": (180, 100, 40)},
    {"name": "Dagger", "damage": 18, "range": 45,  "durability": 25, "color": (200, 200, 230)},
]

LEVEL_TEMPLATES_STAGE2 = [
    {
        "stage": 2,
        "weapon_pool": WEAPON_POOL_STAGE2,
        "width": 3000,
        "platforms": [
            (0, SCREEN_HEIGHT - 60, 900),
            (1120, SCREEN_HEIGHT - 60, 1880),
            (900, SCREEN_HEIGHT - 180, 220),
            (860, SCREEN_HEIGHT - 200, 110),
            (1500, SCREEN_HEIGHT - 180, 250),
            (1465, SCREEN_HEIGHT - 200, 125),
            (2220, SCREEN_HEIGHT - 180, 380),
            (2170, SCREEN_HEIGHT - 200, 190),
        ],
        "moving_platforms": [
            {"x": 900,  "y": SCREEN_HEIGHT - 120, "width": 180, "axis": "horizontal", "start": 900,  "end": 940, "speed": 2.4},
            {"x": 1180, "y": SCREEN_HEIGHT - 150, "width": 160, "axis": "horizontal", "start": 1180, "end": 1360, "speed": 2.2},
        ],
        "enemies": [
            (180, SCREEN_HEIGHT - 140, "insect"),
            (520, SCREEN_HEIGHT - 60 - 34, "reptile"),
            (820, SCREEN_HEIGHT - 140, "insect"),
            (1010, SCREEN_HEIGHT - 180 - 34, "reptile"),
            (1220, SCREEN_HEIGHT - 220, "insect"),
            (980, SCREEN_HEIGHT - 180 - 34, "reptile"),
            (1625, SCREEN_HEIGHT - 180 - 34, "reptile"),
            (1820, SCREEN_HEIGHT - 140, "insect"),
            (2410, SCREEN_HEIGHT - 180 - 34, "reptile"),
            (2620, SCREEN_HEIGHT - 140, "insect"),
            (2060, SCREEN_HEIGHT - 60 - 34, "reptile"),
        ],
        "crates": [
            450,
            1800,
            (1010, SCREEN_HEIGHT - 180 - 36),
            (1625, SCREEN_HEIGHT - 180 - 36),
            (2410, SCREEN_HEIGHT - 180 - 36),
        ],
        "door": (2880, None),
    },
    {
        "stage": 2,
        "weapon_pool": WEAPON_POOL_STAGE2,
        "width": 4000,
        "platforms": [
            (0, SCREEN_HEIGHT - 60, 900),
            (1200, SCREEN_HEIGHT - 60, 900),
            (2500, SCREEN_HEIGHT - 60, 1400),
            (700, SCREEN_HEIGHT - 220, 200),
            (700, SCREEN_HEIGHT - 200, 100),
            (1650, SCREEN_HEIGHT - 240, 220),
            (1650, SCREEN_HEIGHT - 220, 110),
            (2250, SCREEN_HEIGHT - 220, 250),
            (2250, SCREEN_HEIGHT - 200, 125),
            (3050, SCREEN_HEIGHT - 240, 260),
            (3050, SCREEN_HEIGHT - 200, 130),
            (3450, SCREEN_HEIGHT - 220, 240),
            (3450, SCREEN_HEIGHT - 200, 120),
            (1300, SCREEN_HEIGHT - 420, 260),
            (1300, SCREEN_HEIGHT - 400, 130),
            (2500, SCREEN_HEIGHT - 430, 240),
            (2500, SCREEN_HEIGHT - 410, 120),
            (3300, SCREEN_HEIGHT - 430, 300),
            (3300, SCREEN_HEIGHT - 410, 150),
        ],
        "moving_platforms": [
            {"x": 900,  "y": SCREEN_HEIGHT - 120, "width": 200, "axis": "horizontal", "start": 900,  "end": 1000, "speed": 2.4},
            {"x": 2100, "y": SCREEN_HEIGHT - 120, "width": 220, "axis": "horizontal", "start": 2100, "end": 2280, "speed": 2.2},
            {"x": 1700, "y": SCREEN_HEIGHT - 250, "width": 160, "axis": "horizontal", "start": 1700, "end": 1880, "speed": 2.0},
            {"x": 1320, "y": SCREEN_HEIGHT - 420, "width": 140, "axis": "vertical",   "start": SCREEN_HEIGHT - 420, "end": SCREEN_HEIGHT - 240, "speed": 2.0},
            {"x": 3300, "y": SCREEN_HEIGHT - 430, "width": 140, "axis": "vertical",   "start": SCREEN_HEIGHT - 430, "end": SCREEN_HEIGHT - 240, "speed": 2.2},
        ],
        "enemies": [
            (240, SCREEN_HEIGHT - 140, "insect"),
            (520, SCREEN_HEIGHT - 60 - 34, "reptile"),
            (900, SCREEN_HEIGHT - 140, "insect"),
            (1430, SCREEN_HEIGHT - 60 - 34, "reptile"),
            (760, SCREEN_HEIGHT - 220 - 34, "reptile"),
            (1680, SCREEN_HEIGHT - 260, "insect"),
            (1760, SCREEN_HEIGHT - 240 - 34, "reptile"),
            (2250, SCREEN_HEIGHT - 220 - 34, "reptile"),
            (2760, SCREEN_HEIGHT - 140, "insect"),
            (3450, SCREEN_HEIGHT - 430 - 34, "reptile"),
            (1350, SCREEN_HEIGHT - 430, "insect"),
            (2570, SCREEN_HEIGHT - 430 - 34, "reptile"),
            (3600, SCREEN_HEIGHT - 220, "insect"),
            (3200, SCREEN_HEIGHT - 60 - 34, "reptile"),
        ],
        "crates": [
            450,
            3200,
            (800, SCREEN_HEIGHT - 220 - 36),
            (1430, SCREEN_HEIGHT - 420 - 36),
            (1760, SCREEN_HEIGHT - 240 - 36),
            (2375, SCREEN_HEIGHT - 220 - 36),
            (2570, SCREEN_HEIGHT - 430 - 36),
        ],
        "door": (3880, None),
    },
    {
        "stage": 2,
        "weapon_pool": WEAPON_POOL_STAGE2,
        "width": 6000,
        "platforms": [
            (0, SCREEN_HEIGHT - 60, 760),
            (1040, SCREEN_HEIGHT - 60, 820),
            (2120, SCREEN_HEIGHT - 60, 880),
            (3340, SCREEN_HEIGHT - 60, 1060),
            (4400, SCREEN_HEIGHT - 60, 1600),
            # Bridge platforms centered above holes between ground segments
            # Lowered so bridges have clear vertical space above and below them
            # Hole 1: between x=760 and x=1040 (width 280) -> bridge ~140 wide, centered at x=900
            (830, SCREEN_HEIGHT - 300, 140),
            # Hole 2: between x=1860 and x=2120 (width 260) -> bridge ~130 wide, centered at x=1990
            (1925, SCREEN_HEIGHT - 300, 130),
            # Hole 3: between x=3000 and x=3340 (width 340) -> bridge ~170 wide, centered at x=3170
            (3085, SCREEN_HEIGHT - 300, 170),
            (760, SCREEN_HEIGHT - 220, 280),
            (760, SCREEN_HEIGHT - 200, 140),
            (1480, SCREEN_HEIGHT - 240, 220),
            (1480, SCREEN_HEIGHT - 220, 110),
            (1800, SCREEN_HEIGHT - 240, 180),
            (1800, SCREEN_HEIGHT - 220, 90),
            (2550, SCREEN_HEIGHT - 240, 260),
            (2550, SCREEN_HEIGHT - 220, 130),
            (3360, SCREEN_HEIGHT - 220, 280),
            (3360, SCREEN_HEIGHT - 200, 140),
            (3800, SCREEN_HEIGHT - 240, 180),
            (3800, SCREEN_HEIGHT - 220, 90),
            (4300, SCREEN_HEIGHT - 260, 240),
            (4300, SCREEN_HEIGHT - 220, 120),
            (1250, SCREEN_HEIGHT - 430, 260),
            (1250, SCREEN_HEIGHT - 390, 130),
            (2480, SCREEN_HEIGHT - 440, 240),
            (2480, SCREEN_HEIGHT - 400, 120),
            (3720, SCREEN_HEIGHT - 440, 260),
            (3720, SCREEN_HEIGHT - 400, 130),
            (4930, SCREEN_HEIGHT - 430, 220),
            (4930, SCREEN_HEIGHT - 390, 110),
        ],
        "moving_platforms": [
            # Horizontal moving platforms located over each hole - travel spans the hole width so player can ride across
            {"x": 760,  "y": SCREEN_HEIGHT - 120, "width": 200, "axis": "horizontal", "start": 760,  "end": 840, "speed": 2.4},
            {"x": 1860, "y": SCREEN_HEIGHT - 120, "width": 220, "axis": "horizontal", "start": 1860, "end": 1900, "speed": 2.2},
            {"x": 3000, "y": SCREEN_HEIGHT - 120, "width": 280, "axis": "horizontal", "start": 3000, "end": 3060, "speed": 2.0},
            {"x": 1250, "y": SCREEN_HEIGHT - 430, "width": 140, "axis": "vertical",   "start": SCREEN_HEIGHT - 430, "end": SCREEN_HEIGHT - 240, "speed": 3.0},
            {"x": 3720, "y": SCREEN_HEIGHT - 440, "width": 140, "axis": "vertical",   "start": SCREEN_HEIGHT - 440, "end": SCREEN_HEIGHT - 240, "speed": 3.2},
        ],
        "enemies": [
            (220, SCREEN_HEIGHT - 140, "insect"),
            (520, SCREEN_HEIGHT - 140, "reptile"),
            (900, SCREEN_HEIGHT - 220 - 34, "reptile"),
            (940, SCREEN_HEIGHT - 300 - 34, "insect"),
            (1140, SCREEN_HEIGHT - 60 - 34, "reptile"),
            (1300, SCREEN_HEIGHT - 430 - 34, "insect"),
            (1520, SCREEN_HEIGHT - 240 - 34, "reptile"),
            (1860, SCREEN_HEIGHT - 240 - 34, "insect"),
            (1990, SCREEN_HEIGHT - 300 - 34, "insect"),
            (2240, SCREEN_HEIGHT - 140, "reptile"),
            (2520, SCREEN_HEIGHT - 440 - 34, "insect"),
            (2580, SCREEN_HEIGHT - 240 - 34, "reptile"),
            (3420, SCREEN_HEIGHT - 220 - 34, "reptile"),
            (3840, SCREEN_HEIGHT - 240 - 34, "insect"),
            (4330, SCREEN_HEIGHT - 260 - 34, "insect"),
            (4930, SCREEN_HEIGHT - 430 - 34, "reptile"),
            (5400, SCREEN_HEIGHT - 60 - 34, "insect"),
        ],
        # Crates placed on platforms that do not have enemies; no crate shares a platform with an enemy
        "crates": [
            (820, SCREEN_HEIGHT - 220 - 36),
            (1550, SCREEN_HEIGHT - 240 - 36),
            (2680, SCREEN_HEIGHT - 240 - 36),
            (3800, SCREEN_HEIGHT - 240 - 36),
            (4370, SCREEN_HEIGHT - 260 - 36),
        ],
        "door": (5880, None),
    },
]

THEMES = [
    {
        "name": "Morning",
        "sky_color": (170, 210, 255),
        "platform_color": (90, 170, 70),
        "scene": {
            "type": "sun",
            "color": (255, 220, 90),
            "pos": (SCREEN_WIDTH - 120, 80),
            "radius": 36,
        },
    },
    {
        "name": "Afternoon",
        "sky_color": (240, 160, 90),
        "platform_color": (140, 100, 60),
        "scene": {
            "type": "sun",
            "color": (240, 140, 40),
            "pos": (SCREEN_WIDTH - 120, 120),
            "radius": 36,
        },
    },
    {
        "name": "Night",
        "sky_color": (16, 32, 72),
        "platform_color": (80, 88, 102),
        "scene": {
            "type": "moon",
            "color": (216, 224, 232),
            "pos": (SCREEN_WIDTH - 120, 90),
            "radius": 26,
            "star_color": (220, 220, 240),
            "stars": [
                (840, 50), (870, 30), (900, 70), (925, 40), (955, 65),
                (980, 25), (1010, 55), (1040, 40), (1080, 30), (1110, 65),
                (1140, 45), (1180, 20), (1210, 68), (1240, 35), (1270, 60),
            ],
        },
    },
]

WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
RED     = (220, 50,  50)
GRAY    = (120, 120, 120)
DGRAY   = (60,  60,  60)
LGRAY   = (180, 180, 180)
SKY     = (100, 180, 240)
GREEN   = (40,  180, 60)
YELLOW  = (240, 210, 30)
BROWN   = (139, 90,  43)
LBROWN  = (205, 160, 100)
GOLD    = (255, 200, 0)
BLUE    = (50,  100, 220)
PURPLE  = (140, 60,  200)
ORANGE  = (255, 140, 0)
TEAL    = (0, 150, 150)

# Stage 1 weapon pool (baseline)
WEAPON_POOL = [
    {"name": "Fist",  "damage": 6,  "range": 36,  "durability": None, "color": (200, 200, 200)},
    {"name": "Stick", "damage": 9,  "range": 50,  "durability": 20,   "color": (139, 90, 43)},
    {"name": "Dagger","damage": 12, "range": 40,  "durability": 25,   "color": (200, 200, 230)},
]

# Fist shorthand used by player default slot
FIST = {"name": "Fist", "damage": 6, "range": 36, "durability": None, "color": (200, 200, 200)}

# Derive stage 2 and stage 3 enemy health tables from base ENEMY_HEALTH
ENEMY_HEALTH_STAGE2 = [[int(round(v * 1.27)) for v in pair] for pair in ENEMY_HEALTH]
ENEMY_HEALTH_STAGE3 = [[int(round(v * 1.27 * 1.7)) for v in pair] for pair in ENEMY_HEALTH]
 
