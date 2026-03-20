"""
ga/operators.py
Genetic operators: tournament selection, single-point crossover, mutation.
"""
import random
import numpy as np

from ga.individual import Individual, N_GENES, MAX_THRUST, MAX_ANGLE_DELTA

TOURNAMENT_K: int = 5        # tournament size
MUTATION_RATE: float = 0.08  # probability per gene


# ------------------------------------------------------------------ #
def tournament_select(population: list, k: int = TOURNAMENT_K) -> Individual:
    """Return the fittest individual from a random k-subset."""
    contestants = random.sample(population, k)
    return max(contestants, key=lambda ind: ind.fitness)


# ------------------------------------------------------------------ #
def crossover(parent_a: Individual, parent_b: Individual) -> tuple:
    """Single-point crossover; returns two offspring."""
    cut = random.randint(1, N_GENES - 1)
    child_a = Individual(genes=parent_a.genes[:cut] + parent_b.genes[cut:])
    child_b = Individual(genes=parent_b.genes[:cut] + parent_a.genes[cut:])
    return child_a, child_b


# ------------------------------------------------------------------ #
def mutate(individual: Individual, rate: float = MUTATION_RATE) -> Individual:
    """Randomly perturb genes in-place; returns the individual."""
    genes = list(individual.genes)
    for i, (thrust, angle_delta) in enumerate(genes):
        if random.random() < rate:
            # Gaussian noise around current value
            new_thrust = float(np.clip(
                thrust + np.random.normal(0, MAX_THRUST * 0.15),
                0, MAX_THRUST
            ))
            new_angle = float(np.clip(
                angle_delta + np.random.normal(0, MAX_ANGLE_DELTA * 0.3),
                -MAX_ANGLE_DELTA, MAX_ANGLE_DELTA
            ))
            genes[i] = (new_thrust, new_angle)
    individual.genes = genes
    return individual
