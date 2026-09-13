# Drosophila Looming-Escape Simulation

This project is a biologically inspired simulation of the fruit-fly looming-object
escape pathway. The long-term goal is to use Drosophila connectome data to control
an embodied simulated fly and, potentially, a physical robot.

The project is being developed incrementally. Early milestones use deliberately
simple, inspectable models so that physical simulation, sensory processing, neural
processing, behavior, and rendering remain separate.

## Intended architecture

The current stimulus pipeline is:

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

The longer-term embodied loop is:

```text
World
  |
  v
VisionSystem
  |
  v
Brain
  |
  v
Body
  |
  v
World
```

The renderer is passive: it displays state but does not update the simulation or
calculate sensory or neural activity. Physical world quantities are also kept
independent of Pygame pixels.

## Milestone overview

### Milestone 0.1 — Looming stimulus foundation (current, completed)

Build the minimal physical and visual simulation on which the neural model will
depend.

- Simulate a circular object approaching a stationary fly.
- Track physical distance, object radius, and approach speed.
- Convert geometry into angular size and angular expansion velocity.
- Render the looming stimulus as an expanding circle in Pygame.
- Display diagnostic values, including time to collision (TTC).
- Stop cleanly at collision and keep the stimulus inside its display region.
- Support trial reset and interactive speed/radius controls.
- Test world stepping and visual geometry with lightweight unit tests.

No neural model is included in this milestone. `VisualObservation` exposes only
angular size and angular velocity; TTC is an experimenter-facing diagnostic.

### Milestone 0.2 — Approximate LPLC2 and LC4 activity (next)

Add a separate brain-processing layer that converts angular size and angular
velocity into simplified LPLC2 and LC4 activity signals.

- Define explicit, documented phenomenological response equations.
- Keep neural processing separate from vision and rendering.
- Add neural activity to the diagnostic display.
- Add reset behavior for any temporal neural state.
- Test response direction, bounds, and reset behavior.

The output of this milestone will be inspectable neural activity, not behavior.

### Milestone 0.3 — Giant Fiber spiking model

- Feed looming-sensitive activity into a simplified Giant Fiber neuron.
- Introduce membrane dynamics, a firing threshold, and spike events.
- Test spike timing and trial-reset behavior.

### Milestone 0.4 — Escape action

- Convert Giant Fiber output into an escape command.
- Define a minimal action policy and measurable escape latency.
- Keep the neural decision separate from body mechanics.

### Milestone 0.5 — Embodied simulated fly

- Add a movable fly body to the simulated world.
- Close the perception-action loop: world, vision, brain, body, world.
- Evaluate whether escape behavior avoids the approaching threat.

### Later direction — Connectome-informed control and robotics

- Replace or constrain approximate pathways with real Drosophila connectome data.
- Increase biological detail only where it supports the experimental goals.
- Adapt the embodied controller to a physical robot when the simulated loop is
  stable and measurable.

This later roadmap is directional and may change as biological assumptions and
simulation results are evaluated.

  ## Milestone 0.2 modeling assumptions

  The initial neural model is a deliberately simplified phenomenological approximation. It is intended for learning and experimentation,
  not as a biologically exact simulation.

  - NeuralActivity.lplc2 and NeuralActivity.lc4 are dimensionless activity proxies normalized to the range [0, 1]. They are not firing
    rates, calcium signals, membrane voltages, or measurements from individual neurons.

  - The model represents aggregate pathway activity rather than spatial populations of individual LPLC2 and LC4 neurons.
  - LPLC2 is modeled as an angular-size channel. Its response is a log-Gaussian function that peaks at a preferred angular size:

    lplc2 = exp(
        -log(theta / preferred_theta)^2
        / (2 * size_tuning_width^2)
    )

  - The initial LPLC2 parameters are a preferred angular size of 42 degrees and a logarithmic tuning width of 0.52. These values are
    adapted from a published empirical model of the LPLC2 contribution to the Giant Fiber pathway; they should not be interpreted as
    universal biological constants.

  - At zero angular size, LPLC2 activity is defined as zero to avoid taking the logarithm of zero.
  - LPLC2 activity depends only on angular size. Consequently, a stationary object can produce LPLC2 activity if it has an appropriate
    apparent size. This represents the angular-size signal attributed to the LPLC2 pathway, not the complete biological selectivity of
    LPLC2 neurons for radial expansion.

  - LC4 is modeled as a positive angular-expansion-velocity channel with a saturating response:

    expansion_velocity = max(0, angular_velocity)

    lc4 = expansion_velocity / (
        expansion_velocity + half_saturation_velocity
    )

  - Negative angular velocity, representing contraction, produces zero LC4 activity.
  - The LC4 half-saturation velocity is an engineering parameter, not a fitted biological constant. An initial value of 100 degrees/second
    gives a useful response range for the current default trial and remains configurable.

  - Both response functions are instantaneous and stateless. The initial model does not include neural transmission delays, membrane
    dynamics, adaptation, persistence, noise, or stochastic firing.

  - Brain.reset() is still part of the interface so temporal state can be introduced later without changing the simulation architecture.
  - The model receives only global angular size and angular velocity. It does not model contrast, luminance, object position, receptive
    fields, retinotopy, directional motion channels, or the radial-motion opponency associated with biological LPLC2 neurons.

  - Angular velocity retains the finite-difference behavior of VisionSystem. Sudden changes in object radius therefore cause a genuine
    transient in LC4 activity.

  - Time to collision is not available to the brain. It remains an experimenter-facing diagnostic.
  - The neural outputs do not trigger escape behavior during Milestone 0.2. Giant Fiber integration, thresholds, spikes, and motor actions
    remain later milestones.

## Current controls

- `Space`: reset the trial to its initial parameters
- `P`: pause or resume the current trial
- `Up` / `Down`: increase / decrease approach speed
- `Right` / `Left`: increase / decrease object radius
- `Escape`: quit

## Running the simulation

The project uses Python 3.13, Pygame, and `uv`:

```bash
uv run python main.py
```

Run the unit tests with:

```bash
uv run python -m unittest discover -s tests -v
```
