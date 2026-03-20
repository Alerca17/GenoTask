"""
gui/app.py
Main application controller.
Runs the GA in a background thread and animates the best individual.
"""
import threading
import time
import pygame
from typing import Optional

from gui.renderer import Renderer, SCREEN_W, SCREEN_H
from gui.colors import NEON_CYAN, COLOR_LANDED, COLOR_CRASHED, NEON_ORANGE
from ga.population import Population
from ga.fitness import simulate_trajectory, PAD_X, PAD_WIDTH

FPS = 60
BASE_ANIM_SPEED = 3   # frames to advance per display frame during replay


class AppState:
    EVOLVING    = "EVOLVING"
    REPLAYING   = "REPLAYING"
    PAUSED      = "PAUSED"
    FINISHED    = "FINISHED"


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("🛸 GenoTask — Alien Landing GA")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock  = pygame.time.Clock()
        self.renderer = Renderer(self.screen)

        self._reset()

    # ------------------------------------------------------------------ #
    def _reset(self) -> None:
        self.population  = Population(on_generation=self._on_generation)
        self.state       = AppState.EVOLVING
        self.paused      = False
        self.anim_step   = 0
        self.anim_speed  = BASE_ANIM_SPEED
        self.snapshots   = []
        self.final_state = None
        self.best_fitness_history: list = []
        self.current_gen = 0
        self.best_fit    = 0.0
        self.avg_fit     = 0.0
        self.landed      = False
        self.crashed     = False
        self._lock       = threading.Lock()
        self._evo_thread: Optional[threading.Thread] = None
        self._stop_flag  = threading.Event()
        self._start_evolution()

    # ------------------------------------------------------------------ #
    def _start_evolution(self) -> None:
        self._stop_flag.clear()
        self._evo_thread = threading.Thread(target=self._evolution_loop, daemon=True)
        self._evo_thread.start()

    # ------------------------------------------------------------------ #
    def _evolution_loop(self) -> None:
        """Background thread: runs generations until stopped."""
        max_gen = 200
        try:
            while not self._stop_flag.is_set():
                if self.paused:
                    time.sleep(0.05)
                    continue
                self.population.evolve_one_generation()
                if self.population.generation >= max_gen:
                    break
        except Exception as exc:
            import traceback
            traceback.print_exc()
        finally:
            # Always switch to replay when done (or on error)
            self._start_replay()

    # ------------------------------------------------------------------ #
    def _on_generation(self, pop: Population) -> None:
        # Compute trajectory OUTSIDE the lock (can be slow)
        snaps, fs = (None, None)
        if pop.best:
            try:
                snaps, fs = simulate_trajectory(pop.best)
            except Exception:
                pass

        with self._lock:
            self.current_gen = pop.generation
            self.best_fit    = pop.best.fitness if pop.best else 0.0
            self.avg_fit     = (pop.avg_fitness_history[-1]
                                if pop.avg_fitness_history else 0.0)
            self.best_fitness_history = list(pop.best_fitness_history)
            if snaps is not None and fs is not None:
                self.snapshots   = snaps
                self.final_state = fs
                self.landed      = fs.landed
                self.crashed     = fs.crashed

    # ------------------------------------------------------------------ #
    def _start_replay(self) -> None:
        with self._lock:
            self.anim_step = 0
            self.state = AppState.REPLAYING

    # ------------------------------------------------------------------ #
    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self._stop_flag.set()
                    self._reset()
                elif event.key == pygame.K_UP:
                    self.anim_speed = min(self.anim_speed + 1, 10)
                elif event.key == pygame.K_DOWN:
                    self.anim_speed = max(self.anim_speed - 1, 1)
        return True

    # ------------------------------------------------------------------ #
    def _determine_display_status(self) -> str:
        if self.paused:
            return "PAUSED"
        if self.state == AppState.EVOLVING:
            return "EVOLVING"
        if self.state == AppState.REPLAYING:
            return "REPLAYING"
        return "DONE"

    # ------------------------------------------------------------------ #
    def run(self) -> None:
        running = True
        while running:
            running = self._handle_events()

            # Advance animation frame
            with self._lock:
                snaps = list(self.snapshots)
                anim_step = self.anim_step
                gen  = self.current_gen
                bf   = self.best_fit
                af   = self.avg_fit
                hist = list(self.best_fitness_history)
                landed  = self.landed
                crashed = self.crashed

            if snaps:
                if (self.state == AppState.EVOLVING and not self.paused):
                    # Show live rolling preview
                    self.anim_step = (self.anim_step + self.anim_speed) % max(len(snaps), 1)
                elif self.state == AppState.REPLAYING:
                    self.anim_step += self.anim_speed
                    if self.anim_step >= len(snaps):
                        self.anim_step = 0  # loop replay

            status = self._determine_display_status()

            self.renderer.draw_frame(
                snapshots=snaps,
                current_step=min(anim_step, len(snaps) - 1) if snaps else 0,
                generation=gen,
                best_fitness=bf,
                avg_fitness=af,
                status=status,
                fitness_history=hist,
                landed=landed,
                crashed=crashed,
            )

            # Landing/crash overlay
            if self.state == AppState.REPLAYING:
                if landed:
                    self.renderer.draw_message("✓  ATERRIZAJE EXITOSO", COLOR_LANDED)
                elif crashed:
                    self.renderer.draw_message("✗  NAVE DESTRUIDA", COLOR_CRASHED)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
