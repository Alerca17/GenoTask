"""
ga/fitness.py
Fitness evaluation: run a full simulation, return scalar score.
Higher is better.
"""
from ga.individual import Individual, N_GENES
from simulation.physics import PhysicsState, GROUND_Y, DT

# Landing pad configuration (shared with renderer)
PAD_X: float = 450.0      # center x of landing pad
PAD_WIDTH: float = 100.0  # full width of pad

# Spawn position
SPAWN_X: float = 100.0
SPAWN_Y: float = 80.0


def evaluate(individual: Individual,
             pad_x: float = PAD_X,
             pad_width: float = PAD_WIDTH) -> float:
    """
    Simulate the individual's genes and return a fitness score.
    Returns a positive float; the higher the better.
    """
    state = PhysicsState(x=SPAWN_X, y=SPAWN_Y)

    for thrust, angle_delta in individual.genes:
        if not state.alive:
            break
        state.step(thrust, angle_delta)

    state.check_landing(pad_x, pad_width)

    # ----- fitness decomposition -----
    # 1. Distance penalty: how far from pad center at termination
    dist_x = abs(state.x - pad_x)
    dist_score = max(0.0, 1000.0 - dist_x * 2.5)

    # 2. Velocity penalty: reward soft landing
    speed = (state.vx ** 2 + state.vy ** 2) ** 0.5
    vel_score = max(0.0, 500.0 - speed * 20.0)

    # 3. Angle penalty
    angle_score = max(0.0, 200.0 - abs(state.angle) * 5.0)

    # 4. Bonus for landing vs crashing
    bonus = 3000.0 if state.landed else (500.0 if not state.crashed else 0.0)

    # 5. Survival time (prefer individuals that don't crash immediately)
    survive_score = state.steps_survived * 0.5

    fitness = dist_score + vel_score + angle_score + bonus + survive_score
    individual.fitness = fitness
    return fitness


def simulate_trajectory(individual: Individual,
                         pad_x: float = PAD_X,
                         pad_width: float = PAD_WIDTH):
    """
    Re-run simulation and return list of (x, y, angle) snapshots for animation.
    """
    state = PhysicsState(x=SPAWN_X, y=SPAWN_Y)
    snapshots = [(state.x, state.y, state.angle, 0.0)]

    for thrust, angle_delta in individual.genes:
        if not state.alive:
            break
        state.step(thrust, angle_delta)
        snapshots.append((state.x, state.y, state.angle, thrust))

    state.check_landing(pad_x, pad_width)
    return snapshots, state
