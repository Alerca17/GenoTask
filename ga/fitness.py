"""
ga/fitness.py
Fitness evaluation with 4-direction (fx, fy) gene system.
Spawn top-left, land on platform bottom-right — a diagonal challenge.
"""
import math
from ga.individual import Individual, N_GENES
from simulation.physics import PhysicsState, GROUND_Y, WORLD_W

# ── Landing pad ───────────────────────────────────────────────────────── #
PAD_X:     float = 520.0   # center of landing pad (right side)
PAD_WIDTH: float = 110.0   # full width

# ── Spawn position (top-left) ─────────────────────────────────────────── #
SPAWN_X: float = 120.0
SPAWN_Y: float = 70.0


def calculate_fitness(state: PhysicsState,
                      pad_x: float = PAD_X,
                      pad_width: float = PAD_WIDTH) -> float:
    """Calculate fitness from a completed or terminated physics state."""
    # ── Fitness components ───────────────────────────────────────────── #
    dist_x = abs(state.x - pad_x)
    dist_y = abs(state.y - GROUND_Y)                        # how close vertically
    dist_score  = max(0.0, 1200.0 - dist_x * 2.0 - dist_y * 0.5)

    speed = math.hypot(state.vx, state.vy)
    vel_score   = max(0.0, 600.0 - speed * 18.0)

    bonus = 4000.0 if state.landed else (600.0 if not state.crashed else 0.0)
    survive     = state.steps_survived * 0.8

    fitness = dist_score + vel_score + bonus + survive
    return fitness
