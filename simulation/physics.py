"""
simulation/physics.py
2D physics engine — direct (fx, fy) thrust model.
Gravity pulls the craft downward; genes apply force in any direction.
"""
import math
from dataclasses import dataclass, field

# ---- world constants ----
GRAVITY: float  = 4.0     # pixels/s² downward
DT: float       = 0.22    # seconds per step
GROUND_Y: float = 640.0   # y-coord of ground  (screen: down = +)
WORLD_W: float  = 680.0   # simulation area width (= SIM_W in renderer)
DRAG: float     = 0.985   # velocity damping per step


@dataclass
class PhysicsState:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    alive: bool = True
    landed: bool = False
    crashed: bool = False
    steps_survived: int = 0

    # ── computed angle for rendering ──────────────────────────────────── #
    @property
    def angle(self) -> float:
        """Visual angle (degrees) from velocity vector; 0 = pointing up."""
        speed = math.hypot(self.vx, self.vy)
        if speed < 0.3:
            return 0.0
        # atan2(vx, -vy): 0=up, +CW, −CCW
        return math.degrees(math.atan2(self.vx, -self.vy))

    # ── simulation step ───────────────────────────────────────────────── #
    def step(self, fx: float, fy: float) -> None:
        """Advance one DT step; fx/fy are direct force components."""
        if not self.alive:
            return

        # Net acceleration
        ax = fx
        ay = fy + GRAVITY          # gravity always pulls down

        self.vx += ax * DT
        self.vy += ay * DT

        # Drag (prevents runaway velocities)
        self.vx *= DRAG
        self.vy *= DRAG

        self.x += self.vx * DT
        self.y += self.vy * DT
        self.steps_survived += 1

        # Horizontal wall bounce
        if self.x < 0.0:
            self.vx = abs(self.vx) * 0.4
            self.x = 0.0
        elif self.x > WORLD_W:
            self.vx = -abs(self.vx) * 0.4
            self.x = WORLD_W

        # Ground check
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.alive = False

    # ── landing quality ───────────────────────────────────────────────── #
    def check_landing(self, pad_x: float, pad_width: float,
                      max_vy: float = 6.0,
                      max_vx: float = 5.0) -> None:
        """Called once craft touches the ground."""
        in_pad    = abs(self.x - pad_x) <= pad_width / 2.0
        soft_v    = abs(self.vy) <= max_vy and abs(self.vx) <= max_vx
        if in_pad and soft_v:
            self.landed = True
        else:
            self.crashed = True
