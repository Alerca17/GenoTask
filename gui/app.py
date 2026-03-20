"""
gui/app.py
Main application controller.
Runs the simulation live frame by frame.
"""
import pygame
import math
from typing import List, Optional

from gui.renderer import Renderer, SCREEN_W, SCREEN_H
from gui.colors import NEON_CYAN, COLOR_LANDED, COLOR_CRASHED
from ga.population import Population
from ga.fitness import calculate_fitness, PAD_X, PAD_WIDTH, SPAWN_X, SPAWN_Y
from ga.individual import N_GENES
from simulation.physics import PhysicsState

FPS = 60

class AppState:
    EVOLVING = "EVOLVING"
    PAUSED   = "PAUSED"
    FINISHED = "FINISHED"

class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("🛸 GenoTask — Alien Landing GA")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock  = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        
        # Explosion asset preloading (using simple drawing for now, or Pygame circle)
        self._reset()

    # ------------------------------------------------------------------ #
    def _reset(self) -> None:
        self.population  = Population()
        self.state       = AppState.EVOLVING
        self.paused      = False
        self.anim_speed  = 1
        
        self.current_gen = 0
        self.best_fit    = 0.0
        self.avg_fit     = 0.0
        
        self._setup_generation()

    def _setup_generation(self) -> None:
        """Create initial physics states and empty trails for the new generation."""
        self.states: List[PhysicsState] = [
            PhysicsState(x=SPAWN_X, y=SPAWN_Y) 
            for _ in self.population.individuals
        ]
        self.trails: List[List[tuple]] = [[] for _ in self.population.individuals]
        self.current_step = 0
        self.frame_skip_counter = 0

    # ------------------------------------------------------------------ #
    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self._reset()
                elif event.key == pygame.K_UP:
                    self.anim_speed = min(self.anim_speed + 1, 10)
                elif event.key == pygame.K_DOWN:
                    self.anim_speed = max(self.anim_speed - 1, 1)
        return True

    # ------------------------------------------------------------------ #
    def _step_simulation(self) -> None:
        """Advance the physics simulation by 1 step for all individuals."""
        all_done = True
        
        for i, ind in enumerate(self.population.individuals):
            state = self.states[i]
            if state.alive and self.current_step < N_GENES:
                fx, fy = ind.genes[self.current_step]
                state.step(fx, fy)
                
                # Check ground hit during step
                if not state.alive:
                    state.check_landing(PAD_X, PAD_WIDTH)
                    
                all_done = False
                
                # Record trail point occasionally
                if self.current_step % 3 == 0:
                    self.trails[i].append((state.x, state.y))

        if not all_done and self.current_step < N_GENES:
            self.current_step += 1
        else:
            self._end_generation()

    def _end_generation(self) -> None:
        """All individuals stopped or ran out of genes. Evolve!"""
        # Assign fitness
        for i, ind in enumerate(self.population.individuals):
            state = self.states[i]
            # If they just ran out of genes mid-air, check landing status
            if state.alive:
                state.check_landing(PAD_X, PAD_WIDTH)
            ind.fitness = calculate_fitness(state)
            
        # Update metrics
        best_now = max((i for i in self.population.individuals), key=lambda x: x.fitness)
        self.best_fit = best_now.fitness
        self.avg_fit = sum(i.fitness for i in self.population.individuals) / len(self.population.individuals)
        
        # Evolve
        self.population.evolve_one_generation()
        self.current_gen = self.population.generation
        
        if self.current_gen >= 200:
            self.state = AppState.FINISHED
        else:
            self._setup_generation()

    # ------------------------------------------------------------------ #
    def run(self) -> None:
        running = True
        while running:
            running = self._handle_events()

            if self.state == AppState.EVOLVING and not self.paused:
                # Process physics steps based on animation speed
                for _ in range(self.anim_speed):
                    self._step_simulation()
            
            # Rendering
            status = "PAUSED" if self.paused else self.state
            
            # Pass everything to renderer
            self.renderer.draw_frame_live(
                states=self.states,
                trails=self.trails,
                individuals=self.population.individuals,
                current_step=self.current_step,
                generation=self.current_gen,
                best_fitness=self.best_fit,
                avg_fitness=self.avg_fit,
                status=status,
                fitness_history=self.population.best_fitness_history
            )
            
            if self.state == AppState.FINISHED:
                self.renderer.draw_message("EVOLUTION COMPLETE!", NEON_CYAN)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
