"""
gui/renderer.py
Renders the simulation world with futuristic aesthetics on a Pygame surface.
"""
import pygame
import math
import random
from typing import List, Tuple, Optional

from gui.colors import (
    DEEP_SPACE, SPACE_MID, NEON_CYAN, NEON_GREEN, NEON_ORANGE,
    NEON_BLUE, NEON_MAGENTA, NEON_YELLOW, TEXT_BRIGHT, TEXT_DIM,
    PANEL_BG, PANEL_BORDER, STAR_COLORS, GROUND_COLOR, GROUND_EDGE,
    COLOR_LANDED, COLOR_CRASHED, COLOR_FLYING,
)
from gui.assets import create_spacecraft_surface, create_flame_surface, create_pad_surface
from simulation.physics import GROUND_Y
from ga.fitness import PAD_X, PAD_WIDTH

SCREEN_W = 900
SCREEN_H = 700
PANEL_W  = 220   # right sidebar width
SIM_W    = SCREEN_W - PANEL_W   # simulation viewport width


class StarField:
    """Parallax multi-layer star field."""
    def __init__(self, n_layers: int = 3):
        self.layers: List[List[dict]] = []
        counts = [80, 50, 25]
        speeds = [0.05, 0.12, 0.25]
        for i in range(n_layers):
            layer = []
            for _ in range(counts[i]):
                layer.append({
                    "x": random.uniform(0, SIM_W),
                    "y": random.uniform(0, SCREEN_H),
                    "r": random.randint(1, i + 1),
                    "color": random.choice(STAR_COLORS),
                    "speed": speeds[i],
                    "twinkle": random.uniform(0, math.pi * 2),
                })
            self.layers.append(layer)

    def update(self, tick: int) -> None:
        for layer in self.layers:
            for star in layer:
                star["twinkle"] += 0.04

    def draw(self, surface: pygame.Surface) -> None:
        for layer in self.layers:
            for star in layer:
                alpha = int(180 + 75 * math.sin(star["twinkle"]))
                alpha = max(80, min(255, alpha))
                r, g, b = star["color"]
                col = (
                    min(255, int(r * alpha / 255)),
                    min(255, int(g * alpha / 255)),
                    min(255, int(b * alpha / 255)),
                )
                pygame.draw.circle(surface, col,
                                   (int(star["x"]), int(star["y"])), star["r"])


class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.stars = StarField()
        self.tick = 0

        # Pre-load fonts (pygame.font must be initialized)
        self.font_big   = pygame.font.SysFont("Consolas", 22, bold=True)
        self.font_med   = pygame.font.SysFont("Consolas", 16)
        self.font_small = pygame.font.SysFont("Consolas", 13)
        self.font_title = pygame.font.SysFont("Consolas", 28, bold=True)

        # Pre-build spacecraft and pad surfaces
        self.ship_surf = create_spacecraft_surface(scale=1.0)
        self.pad_surf  = create_pad_surface(int(PAD_WIDTH))

    # ------------------------------------------------------------------ #
    def _draw_background(self) -> None:
        # Gradient background
        sim_surf = self.screen.subsurface((0, 0, SIM_W, SCREEN_H))
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            r = int(DEEP_SPACE[0] * (1-t) + SPACE_MID[0] * t)
            g = int(DEEP_SPACE[1] * (1-t) + SPACE_MID[1] * t)
            b = int(DEEP_SPACE[2] * (1-t) + SPACE_MID[2] * t)
            pygame.draw.line(sim_surf, (r, g, b), (0, y), (SIM_W, y))

        self.stars.update(self.tick)
        self.stars.draw(sim_surf)

    # ------------------------------------------------------------------ #
    def _draw_ground(self) -> None:
        gy = int(GROUND_Y)
        # Ground fill
        pygame.draw.rect(self.screen, GROUND_COLOR,
                         (0, gy, SIM_W, SCREEN_H - gy))
        # Edge glow
        pygame.draw.line(self.screen, GROUND_EDGE, (0, gy), (SIM_W, gy), 3)

        # Distant mountain silhouettes
        pts = [(0, gy)]
        step = SIM_W // 8
        for i in range(9):
            h = 20 + 35 * math.sin(i * 1.7) + 10 * math.sin(i * 3.1)
            pts.append((i * step, gy - int(h)))
        pts.append((SIM_W, gy))
        pygame.draw.polygon(self.screen, (18, 28, 45), pts)

    # ------------------------------------------------------------------ #
    def _draw_pad(self) -> None:
        px = int(PAD_X - PAD_WIDTH / 2)
        py = int(GROUND_Y - 10)

        # Glow halo
        for radius in range(6, 0, -1):
            alpha_surf = pygame.Surface((int(PAD_WIDTH) + radius*4, 20),
                                        pygame.SRCALPHA)
            glow_col = (*NEON_GREEN, max(0, 15 * radius))
            pygame.draw.rect(alpha_surf, glow_col,
                             (0, 0, int(PAD_WIDTH) + radius*4, 20))
            self.screen.blit(alpha_surf, (px - radius*2, py - 2))

        self.screen.blit(self.pad_surf, (px, py))

        # Blinking chevrons
        blink = int(self.tick * 0.04) % 2 == 0
        if blink:
            tri_y = py - 12
            for dx in [-20, 0, 20]:
                cx = int(PAD_X) + dx
                pts = [(cx, tri_y), (cx - 6, tri_y + 10), (cx + 6, tri_y + 10)]
                pygame.draw.polygon(self.screen, NEON_GREEN, pts)

    # ------------------------------------------------------------------ #
    def _draw_spacecraft(self, sx: float, sy: float,
                         angle: float, thrust: float) -> None:
        # Clamp to visible sim area
        sx = max(20.0, min(SIM_W - 20.0, sx))
        sy = max(20.0, min(SCREEN_H - 20.0, sy))

        ship = pygame.transform.rotozoom(self.ship_surf, -angle, 1.0)
        flame = create_flame_surface(min(thrust / 18.0, 1.0), self.tick, scale=1.0)
        flame_rot = pygame.transform.rotozoom(flame, -angle, 1.0)

        ship_rect = ship.get_rect(center=(int(sx), int(sy)))
        self.screen.blit(ship, ship_rect)

        # Place flame below nozzle
        nozzle_offset = pygame.math.Vector2(0, 30).rotate(angle)
        fx = int(sx + nozzle_offset.x - flame_rot.get_width() / 2)
        fy = int(sy + nozzle_offset.y - flame_rot.get_height() / 2)
        self.screen.blit(flame_rot, (fx, fy))

    # ------------------------------------------------------------------ #
    def _draw_trajectory(self, snapshots: list) -> None:
        """Draw faded trajectory trail."""
        if len(snapshots) < 2:
            return
        pts = [(int(s[0]), int(s[1])) for s in snapshots]
        n = len(pts)
        for i in range(1, n):
            t = i / n
            alpha = int(100 * t)
            col = (
                int(NEON_CYAN[0] * t),
                int(NEON_CYAN[1] * t),
                int(NEON_CYAN[2] * t),
            )
            pygame.draw.line(self.screen, col, pts[i-1], pts[i], 1)

    # ------------------------------------------------------------------ #
    def _draw_panel(self, generation: int, best_fitness: float,
                    avg_fitness: float, status: str,
                    fitness_history: list, landed: bool, crashed: bool) -> None:
        # Panel background
        panel_rect = pygame.Rect(SIM_W, 0, PANEL_W, SCREEN_H)
        pygame.draw.rect(self.screen, PANEL_BG, panel_rect)
        pygame.draw.line(self.screen, PANEL_BORDER,
                         (SIM_W, 0), (SIM_W, SCREEN_H), 2)

        x0 = SIM_W + 12
        y = 18

        # Title
        title = self.font_title.render("GENOTASK", True, NEON_CYAN)
        self.screen.blit(title, (SIM_W + (PANEL_W - title.get_width())//2, y))
        y += 36
        sub = self.font_small.render("Alien Landing · GA", True, TEXT_DIM)
        self.screen.blit(sub, (SIM_W + (PANEL_W - sub.get_width())//2, y))
        y += 28

        # Divider
        pygame.draw.line(self.screen, PANEL_BORDER,
                         (SIM_W + 10, y), (SIM_W + PANEL_W - 10, y), 1)
        y += 14

        def stat(label: str, value: str, color=TEXT_BRIGHT) -> None:
            nonlocal y
            lbl = self.font_small.render(label, True, TEXT_DIM)
            val = self.font_med.render(value, True, color)
            self.screen.blit(lbl, (x0, y))
            self.screen.blit(val, (x0, y + 14))
            y += 38

        stat("GENERATION", str(generation))
        stat("BEST FITNESS", f"{best_fitness:,.0f}", NEON_GREEN)
        stat("AVG FITNESS",  f"{avg_fitness:,.0f}", NEON_BLUE)

        # Status badge
        y += 4
        if landed:
            scol, stxt = COLOR_LANDED,  " [OK] LANDED "
        elif crashed:
            scol, stxt = COLOR_CRASHED, " [!] CRASHED "
        else:
            scol, stxt = COLOR_FLYING,  f" {status} "
        badge = self.font_med.render(stxt, True, scol)
        pygame.draw.rect(self.screen, (*scol, 40),
                         (x0 - 2, y, badge.get_width() + 4, badge.get_height() + 4))
        self.screen.blit(badge, (x0, y + 2))
        y += 44

        # Fitness history mini-chart
        pygame.draw.line(self.screen, PANEL_BORDER,
                         (SIM_W + 10, y), (SIM_W + PANEL_W - 10, y), 1)
        y += 10
        chart_label = self.font_small.render("FITNESS HISTORY", True, TEXT_DIM)
        self.screen.blit(chart_label, (x0, y))
        y += 16

        if len(fitness_history) > 1:
            chart_h = 80
            chart_w = PANEL_W - 24
            chart_rect = pygame.Rect(x0 - 2, y, chart_w, chart_h)
            pygame.draw.rect(self.screen, (15, 20, 50), chart_rect)
            pygame.draw.rect(self.screen, PANEL_BORDER, chart_rect, 1)

            mn = min(fitness_history)
            mx = max(fitness_history)
            span = max(mx - mn, 1.0)   # guard against zero-division
            pts = []
            for i, v in enumerate(fitness_history[-chart_w:]):
                px_x = x0 - 2 + int(i / max(len(fitness_history[-chart_w:]), 1) * chart_w)
                px_y = y + chart_h - int((v - mn) / span * (chart_h - 4)) - 2
                pts.append((px_x, px_y))
            if len(pts) >= 2:
                pygame.draw.lines(self.screen, NEON_GREEN, False, pts, 2)

        y += 100
        # Instructions
        pygame.draw.line(self.screen, PANEL_BORDER,
                         (SIM_W + 10, y), (SIM_W + PANEL_W - 10, y), 1)
        y += 12
        instructions = [
            ("SPACE", "Pause / Run"),
            ("R", "Reset GA"),
            ("↑ ↓", "Speed x2 / x0.5"),
        ]
        for key, desc in instructions:
            k = self.font_small.render(f"[{key}]", True, NEON_YELLOW)
            d = self.font_small.render(desc, True, TEXT_DIM)
            self.screen.blit(k, (x0, y))
            self.screen.blit(d, (x0 + k.get_width() + 6, y))
            y += 18

    # ------------------------------------------------------------------ #
    def draw_frame(self,
                   snapshots: list,
                   current_step: int,
                   generation: int,
                   best_fitness: float,
                   avg_fitness: float,
                   status: str,
                   fitness_history: list,
                   landed: bool = False,
                   crashed: bool = False) -> None:
        self.tick += 1
        self._draw_background()
        self._draw_ground()
        self._draw_pad()

        if snapshots and current_step < len(snapshots):
            trail = snapshots[:current_step + 1]
            self._draw_trajectory(trail)
            sx, sy, angle, thrust = snapshots[current_step]
            self._draw_spacecraft(sx, sy, angle, thrust)

        self._draw_panel(generation, best_fitness, avg_fitness, status,
                         fitness_history, landed, crashed)

    # ------------------------------------------------------------------ #
    def draw_message(self, msg: str, color=NEON_CYAN) -> None:
        """Overlay a centered message on the simulation area."""
        surf = self.font_big.render(msg, True, color)
        x = (SIM_W - surf.get_width()) // 2
        y = SCREEN_H // 2 - 20
        # semi-transparent backdrop
        bg = pygame.Surface((surf.get_width() + 20, surf.get_height() + 14),
                            pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        self.screen.blit(bg, (x - 10, y - 7))
        self.screen.blit(surf, (x, y))
