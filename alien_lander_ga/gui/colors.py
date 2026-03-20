"""
gui/colors.py
Cyberpunk / futuristic color palette.
All colors are (R, G, B) tuples suitable for Pygame.
"""

# Background
DEEP_SPACE    = (4,   4,  18)
SPACE_MID     = (8,  10,  35)
SPACE_NEAR    = (14, 18,  55)

# Neon accents
NEON_CYAN     = (0,  240, 255)
NEON_GREEN    = (57, 255, 20)
NEON_MAGENTA  = (255,  0, 200)
NEON_BLUE     = (30, 100, 255)
NEON_ORANGE   = (255, 140, 0)
NEON_YELLOW   = (255, 230, 0)

# UI elements
PANEL_BG      = (10,  12,  40)
PANEL_BORDER  = (0,  180, 220)
TEXT_BRIGHT   = (220, 235, 255)
TEXT_DIM      = (100, 120, 160)

# Star colors
STAR_COLORS   = [
    (200, 200, 220), (180, 200, 255),
    (255, 230, 200), (200, 255, 240),
]

# Landing pad
PAD_COLOR     = (50, 200, 50)
PAD_GLOW      = (30, 255, 100)

# Spacecraft
SHIP_BODY     = (130, 180, 255)
SHIP_ACCENT   = NEON_CYAN
FLAME_INNER   = (255, 255, 200)
FLAME_OUTER   = NEON_ORANGE

# Ground / planet surface
GROUND_COLOR  = (25,  35,  55)
GROUND_EDGE   = (40,  65,  90)

# Status
COLOR_LANDED  = NEON_GREEN
COLOR_CRASHED = (255, 60,  60)
COLOR_FLYING  = NEON_CYAN
