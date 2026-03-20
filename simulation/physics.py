"""
simulation/physics.py
2D physics engine for the alien spacecraft simulation.
Uses simple Euler integration.
"""
import math
from dataclasses import dataclass

# ---- world constants ----
GRAVITY: float = 3.5          # pixels/s² downward (scaled for screen)
DT: float = 0.25              # seconds per simulation step
GROUND_Y: float = 650.0       # y-coordinate of ground (screen coords, down=+)
WORLD_W: float = 900.0


@dataclass
class PhysicsState:
    x: float          # horizontal position (pixels)
    y: float          # vertical position (pixels, 0=top)
    vx: float = 0.0   # horizontal velocity
    vy: float = 0.0   # vertical velocity (positive = downward)
    angle: float = 0.0  # current spacecraft angle (degrees, 0=up)
    alive: bool = True
    landed: bool = False
    crashed: bool = False
    steps_survived: int = 0

    def step(self, thrust: float, angle_delta: float) -> None:
        """Advance simulation one step."""
        if not self.alive:
            return

        self.angle += angle_delta
        self.angle = max(-90.0, min(90.0, self.angle))

        # Thrust vector (angle 0 = upward, i.e. vy decreases)
        rad = math.radians(self.angle)
        ax = thrust * math.sin(rad)
        ay = -thrust * math.cos(rad) + GRAVITY  # net downward acceleration

        self.vx += ax * DT
        self.vy += ay * DT

        self.x += self.vx * DT
        self.y += self.vy * DT
        self.steps_survived += 1

        # Clamp to world width
        if self.x < 0 or self.x > WORLD_W:
            self.vx *= -0.3
            self.x = max(0.0, min(WORLD_W, self.x))

        # Ground collision
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.alive = False

    def check_landing(self, pad_x: float, pad_width: float,
                      max_land_vy: float = 5.0,
                      max_land_vx: float = 4.0) -> None:
        """Evaluate landing quality once the craft hits the ground."""
        in_pad = abs(self.x - pad_x) <= pad_width / 2
        gentle_v = abs(self.vy) <= max_land_vy and abs(self.vx) <= max_land_vx
        level = abs(self.angle) <= 20.0

        if in_pad and gentle_v and level:
            self.landed = True
        else:
            self.crashed = True
