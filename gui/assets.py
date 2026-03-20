"""
gui/assets.py
Procedurally generated Pygame surfaces for the spacecraft and decorations.
No external image files required.
"""
import pygame
import math
import random
from gui.colors import (
    SHIP_BODY, SHIP_ACCENT, NEON_CYAN, NEON_MAGENTA,
    FLAME_INNER, FLAME_OUTER, PAD_COLOR, PAD_GLOW,
    NEON_ORANGE, NEON_YELLOW
)


def create_spacecraft_surface(scale: float = 1.0) -> pygame.Surface:
    """Return a Surface with the alien spacecraft drawn on it."""
    w, h = int(48 * scale), int(60 * scale)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2

    # Main body (futuristic egg/saucer shape)
    body_rect = pygame.Rect(cx - int(16*scale), int(10*scale),
                            int(32*scale), int(36*scale))
    pygame.draw.ellipse(surf, SHIP_BODY, body_rect)
    pygame.draw.ellipse(surf, SHIP_ACCENT, body_rect, max(1, int(2*scale)))

    # Cockpit dome
    dome_rect = pygame.Rect(cx - int(10*scale), int(4*scale),
                            int(20*scale), int(18*scale))
    pygame.draw.ellipse(surf, (60, 140, 220), dome_rect)
    pygame.draw.ellipse(surf, NEON_CYAN, dome_rect, max(1, int(1*scale)))

    # Side wings
    wing_pts_l = [
        (cx - int(16*scale), int(28*scale)),
        (cx - int(30*scale), int(40*scale)),
        (cx - int(14*scale), int(42*scale)),
    ]
    wing_pts_r = [
        (cx + int(16*scale), int(28*scale)),
        (cx + int(30*scale), int(40*scale)),
        (cx + int(14*scale), int(42*scale)),
    ]
    pygame.draw.polygon(surf, NEON_MAGENTA, wing_pts_l)
    pygame.draw.polygon(surf, NEON_MAGENTA, wing_pts_r)
    pygame.draw.polygon(surf, SHIP_ACCENT, wing_pts_l, max(1, int(1*scale)))
    pygame.draw.polygon(surf, SHIP_ACCENT, wing_pts_r, max(1, int(1*scale)))

    # Engine nozzle
    nozzle_rect = pygame.Rect(cx - int(6*scale), int(44*scale),
                              int(12*scale), int(10*scale))
    pygame.draw.ellipse(surf, (80, 80, 100), nozzle_rect)

    return surf


def create_flame_surface(thrust: float, tick: int, scale: float = 1.0) -> pygame.Surface:
    """Return an animated flame Surface. thrust in [0,1]."""
    if thrust < 0.01:
        s = pygame.Surface((1, 1), pygame.SRCALPHA)
        return s

    flicker = 0.85 + 0.15 * math.sin(tick * 0.5)
    fh = int(thrust * 38 * flicker * scale)
    fw = int(12 * scale)
    surf = pygame.Surface((fw, fh + 1), pygame.SRCALPHA)

    for row in range(fh):
        t = row / max(fh, 1)
        r = int(FLAME_INNER[0] * (1 - t) + FLAME_OUTER[0] * t)
        g = int(FLAME_INNER[1] * (1 - t) + FLAME_OUTER[1] * t)
        b = int(FLAME_INNER[2] * (1 - t) + FLAME_OUTER[2] * t)
        alpha = int(255 * (1 - t ** 1.5))
        width = int(fw * (1 - t * 0.6))
        x0 = (fw - width) // 2
        pygame.draw.line(surf, (r, g, b, alpha), (x0, row), (x0 + width, row))

    return surf


def create_pad_surface(pad_w: int, scale: float = 1.0) -> pygame.Surface:
    """Landing pad surface with blinking lights."""
    h = int(14 * scale)
    surf = pygame.Surface((pad_w, h), pygame.SRCALPHA)

    # Base platform
    pygame.draw.rect(surf, PAD_COLOR, (0, int(4*scale), pad_w, int(10*scale)))
    pygame.draw.rect(surf, PAD_GLOW,  (0, int(4*scale), pad_w, int(10*scale)), 2)

    # Dashed center line
    cx = pad_w // 2
    pygame.draw.line(surf, (255, 255, 100), (cx, 0), (cx, h), max(1, int(2*scale)))

    return surf

def create_explosion_surface(scale: float = 1.0) -> pygame.Surface:
    """Return an explosion Graphic."""
    w, h = int(40 * scale), int(40 * scale)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    
    # Draw jagged starburst
    for _ in range(12):
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(5 * scale, 18 * scale)
        ex = cx + math.cos(angle) * dist
        ey = cy + math.sin(angle) * dist
        color = random.choice([NEON_ORANGE, NEON_MAGENTA, FLAME_INNER])
        pygame.draw.line(surf, color, (cx, cy), (ex, ey), int(2 * scale))
        
    pygame.draw.circle(surf, FLAME_INNER, (cx, cy), int(6 * scale))
    return surf
