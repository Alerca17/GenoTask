"""
ga/individual.py
Individual (chromosome) for the alien landing GA.
Gene = (fx, fy): direct force impulse each DT step.
  fx ∈ [-MAX_FX, MAX_FX]  — horizontal thrust (left/right)
  fy ∈ [-MAX_FY, MAX_FY]  — vertical thrust   (up/down, negative=up)
"""
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple

# ── tunable constants ────────────────────────────────────────────────── #
N_GENES:  int   = 140     # simulation time steps
MAX_FX:   float = 9.0     # max horizontal force
MAX_FY:   float = 9.0     # max vertical force  (negative = thrust up)

Gene = Tuple[float, float]   # (fx, fy)


@dataclass
class Individual:
    genes: List[Gene] = field(default_factory=list)
    fitness: float = -1.0

    @classmethod
    def random(cls) -> "Individual":
        genes = [
            (
                float(np.random.uniform(-MAX_FX, MAX_FX)),
                float(np.random.uniform(-MAX_FY, MAX_FY)),
            )
            for _ in range(N_GENES)
        ]
        return cls(genes=genes)

    def clone(self) -> "Individual":
        return Individual(genes=list(self.genes), fitness=self.fitness)

    def __len__(self) -> int:
        return len(self.genes)
