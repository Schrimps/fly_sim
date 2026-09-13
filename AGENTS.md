# AGENTS.md

## Project purpose

This repository contains a biologically inspired simulation of the Drosophila
looming-object escape pathway. The long-term goal is to use real fruit-fly
connectome data to control an embodied simulated fly and, potentially, a physical
robot.

Development is intentionally incremental. Keep each model simple, inspectable,
and replaceable so later biological detail does not require rewriting unrelated
layers.

## Current status

Milestone 0.1, the looming-stimulus foundation, is implemented. It includes:

- a circular object approaching a stationary fly;
- physical distance, radius, and approach speed;
- angular size and angular expansion velocity calculations;
- a Pygame looming-stimulus display and diagnostic panel;
- collision handling and stimulus clipping;
- trial reset and keyboard controls;
- lightweight unit tests for world and vision behavior; and
- a runnable `main.py` entry point.

The next planned milestone is Milestone 0.2: a separate, approximate neural layer
that converts angular size and angular velocity into LPLC2 and LC4 activity. Do
not add Giant Fiber dynamics, escape behavior, body mechanics, connectome data,
or robot integration unless the user explicitly advances the scope.

See `README.md` for the broader milestone roadmap.

## Architecture

The current data flow is:

```text
Clock
  |
  v
Simulation loop
  |
  +----> World.step(dt)
  |
  +----> VisionSystem.observe(world, dt)
  |              |
  |              v
  |       VisualObservation
  |
  +----> Renderer.draw(world, observation)
```

The intended later loop is:

```text
World -> VisionSystem -> Brain -> Body -> World
```

Preserve these boundaries:

1. `world.py` owns physical state and physical updates only.
2. World quantities use physical/world units, never pixels.
3. `vision.py` converts physical geometry into sensory quantities.
4. `VisualObservation` contains only values intended for the neural model:
   angular size and angular velocity.
5. Time to collision (TTC) is an experimenter-facing diagnostic and must not be
   added to `VisualObservation`.
6. `VisionSystem` owns the previous angular size used for its finite-difference
   angular-velocity calculation.
7. Every trial reset must call `VisionSystem.reset()`.
8. The renderer is passive. It may format read-only diagnostics, but it must not
   mutate the world or calculate sensory/neural state.
9. The Pygame clock and event loop belong to the simulation layer.
10. Avoid frameworks and abstractions that are not needed for the current
    milestone.

## Current files

- `world.py`: `LoomingObject`, `World`, physical stepping, and collision state.
- `vision.py`: `VisualObservation` and `VisionSystem`.
- `render.py`: passive Pygame `Renderer` and human-facing diagnostics.
- `sim.py`: trial parameters, Pygame lifecycle, controls, and simulation loop.
- `main.py`: application entry point; calls the simulation runner.
- `tests/test_world.py`: physical stepping and collision tests.
- `tests/test_vision.py`: visual geometry, finite difference, and reset tests.
- `README.md`: project overview and roadmap.

The original design called the rendering and simulation files `renderer.py` and
`simulation.py`; the repository currently uses `render.py` and `sim.py`. If these
are renamed, update all imports, documentation, and run checks together.

## Mathematical model

For object radius `r` and axial distance `d`, angular diameter is:

```text
theta = 2 * atan2(r, d)
```

Angular expansion velocity is calculated as a finite difference:

```text
theta_dot = (theta - previous_theta) / dt
```

The first observation after construction or `VisionSystem.reset()` has angular
velocity zero because no earlier sample exists.

For diagnostics under constant positive approach speed:

```text
TTC = distance / speed
```

At collision TTC is zero. If distance is positive and speed is zero, TTC is
infinity.

Rendering projects angular diameter into pixels using:

```text
pixels_per_radian = screen_width / horizontal_fov
diameter_px = angular_size * pixels_per_radian
```

The initial horizontal field of view is 120 degrees. Drawing is clipped to the
upper stimulus panel so a valid stimulus larger than the field of view cannot
cover the diagnostics panel.

## Numerical and trial behavior

- All physical parameters and time steps must be finite.
- Initial distance must be positive.
- Runtime distance is clamped at zero and must never become negative.
- Radius must remain strictly positive.
- Approach speed must be non-negative.
- Zero speed means a stationary object.
- `World.step(0)` is a no-op; negative or non-finite `dt` is invalid.
- `VisionSystem.observe()` requires finite `dt > 0` because it divides by `dt`.
- At collision, distance and current physical speed become zero and the trial
  stops until reset.
- Initial trial parameters are stored separately from mutable runtime state.
- Reset creates a fresh world from those parameters and resets vision history.

## Controls

- `Space`: reset/restart from the initial trial parameters.
- `Up` / `Down`: increase/decrease current approach speed.
- `Right` / `Left`: increase/decrease current object radius.
- `Escape`: quit.

Speed is clamped at zero and radius at a small positive minimum. Changing radius
during a running trial causes a real angular-velocity transient because the
visible size changes instantaneously; this is accepted for Milestone 0.1.

## Development commands

Run the simulation:

```bash
uv run python main.py
```

Run the test suite:

```bash
uv run python -m unittest discover -s tests -v
```

The project currently uses Python 3.13, Pygame, `uv`, and the standard-library
`unittest` framework.

## Testing expectations

Keep numerical behavior covered with small deterministic unit tests. At minimum,
tests should continue to cover:

- distance reduction during a world step;
- zero and invalid `dt` behavior;
- zero approach speed;
- collision clamping;
- angular-size geometry;
- finite-difference angular velocity;
- zero angular velocity on the first observation;
- vision reset behavior; and
- the 180-degree angular size at zero distance.

Pygame rendering can remain manually checked during Milestone 0.1. Avoid adding a
heavy GUI-testing setup unless rendering behavior becomes complex enough to
justify it.

## Next milestone boundary

For Milestone 0.2, introduce a separate brain module with an interface similar to:

```python
@dataclass(frozen=True)
class NeuralActivity:
    lplc2: float
    lc4: float


class Brain:
    def process(
        self,
        observation: VisualObservation,
        dt: float,
    ) -> NeuralActivity:
        ...

    def reset(self) -> None:
        ...
```

The first neural equations should be explicitly documented phenomenological
approximations, not presented as biologically exact. The renderer may display
their outputs but must not calculate them. If the brain has temporal state, trial
reset must reset both vision and brain state.

Before choosing LPLC2 or LC4 response equations, discuss and document the modeling
assumptions with the user. Do not silently invent biological parameters.
