"""
ga/individual.py
Individual (chromosome) for the alien landing GA.
Each gene encodes one thrust command: (thrust, angle_delta)
applied for a fixed dt step in the simulation.
"""
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple

# ---- tunable constants ----
N_GENES: int = 120          # number of time-steps per individual
MAX_THRUST: float = 15.0    # max engine thrust magnitude
MAX_ANGLE_DELTA: float = 8.0  # max angle change per step (degrees)

Gene = Tuple[float, float]  # (thrust, angle_delta)


@dataclass
class Individual:
    genes: List[Gene] = field(default_factory=list)
    fitness: float = -1.0

    # ------------------------------------------------------------------ #
    @classmethod
    def random(cls) -> "Individual":
        """Create a random individual."""
        genes = [
            (
                np.random.uniform(0, MAX_THRUST),
                np.random.uniform(-MAX_ANGLE_DELTA, MAX_ANGLE_DELTA),
            )
            for _ in range(N_GENES)
        ]
        return cls(genes=genes)

    # ------------------------------------------------------------------ #
    def clone(self) -> "Individual":
        return Individual(genes=list(self.genes), fitness=self.fitness)

    def __len__(self) -> int:
        return len(self.genes)
