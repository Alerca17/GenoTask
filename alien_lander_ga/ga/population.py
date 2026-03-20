"""
ga/population.py
Manages a population of individuals over generations.
"""
import random
from typing import Callable, List, Optional

from alien_lander_ga.ga.individual import Individual
from alien_lander_ga.ga.operators import tournament_select, crossover, mutate

POPULATION_SIZE: int = 80
ELITE_COUNT: int = 4
CROSSOVER_PROB: float = 0.85


class Population:
    def __init__(
        self,
        size: int = POPULATION_SIZE,
        on_generation: Optional[Callable] = None,
    ):
        self.size = size
        self.generation = 0
        self.individuals: List[Individual] = [Individual.random() for _ in range(size)]
        self.best: Optional[Individual] = None
        self.best_fitness_history: List[float] = []
        self.avg_fitness_history: List[float] = []
        self.on_generation = on_generation  # callback after each generation

    # ------------------------------------------------------------------ #
    def evolve_one_generation(self) -> None:
        """Selects → Reproduces one generation (fitness must be evaluated prior)."""
        # Sort descending by fitness
        self.individuals.sort(key=lambda i: i.fitness, reverse=True)
        best_now = self.individuals[0]

        if self.best is None or best_now.fitness > self.best.fitness:
            self.best = best_now.clone()

        avg = sum(i.fitness for i in self.individuals) / len(self.individuals)
        self.best_fitness_history.append(best_now.fitness)
        self.avg_fitness_history.append(avg)

        # Elitism: carry over top individuals unchanged
        new_pop = [ind.clone() for ind in self.individuals[:ELITE_COUNT]]

        while len(new_pop) < self.size:
            p1 = tournament_select(self.individuals)
            p2 = tournament_select(self.individuals)
            if random.random() < CROSSOVER_PROB:
                c1, c2 = crossover(p1, p2)
            else:
                c1, c2 = p1.clone(), p2.clone()
            mutate(c1)
            mutate(c2)
            new_pop.append(c1)
            if len(new_pop) < self.size:
                new_pop.append(c2)

        self.individuals = new_pop
        self.generation += 1
