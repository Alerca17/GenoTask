"""
ga/operators.py
Genetic operators for (fx, fy) gene format.
"""
import random
import numpy as np

from ga.individual import Individual, N_GENES, MAX_FX, MAX_FY

TOURNAMENT_K:  int   = 5
MUTATION_RATE: float = 0.08
CROSSOVER_PROB: float = 0.85


def tournament_select(population: list, k: int = TOURNAMENT_K) -> Individual:
    contestants = random.sample(population, k)
    return max(contestants, key=lambda ind: ind.fitness)


def crossover(parent_a: Individual, parent_b: Individual) -> tuple:
    cut = random.randint(1, N_GENES - 1)
    child_a = Individual(genes=parent_a.genes[:cut] + parent_b.genes[cut:])
    child_b = Individual(genes=parent_b.genes[:cut] + parent_a.genes[cut:])
    return child_a, child_b


def mutate(individual: Individual, rate: float = MUTATION_RATE) -> Individual:
    genes = list(individual.genes)
    for i, (fx, fy) in enumerate(genes):
        if random.random() < rate:
            new_fx = float(np.clip(
                fx + np.random.normal(0, MAX_FX * 0.2), -MAX_FX, MAX_FX
            ))
            new_fy = float(np.clip(
                fy + np.random.normal(0, MAX_FY * 0.2), -MAX_FY, MAX_FY
            ))
            genes[i] = (new_fx, new_fy)
    individual.genes = genes
    return individual
