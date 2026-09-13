from dataclasses import dataclass
import math
from vision import VisualObservation

@dataclass(frozen=True)
class NeuralActivity:
    lplc2: float
    lc4: float

@dataclass(frozen=True)
class BrainParameters:
    lplc2_preffered_angle: float = math.radians(42.0)
    lplc2_log_width: float = 0.52
    lc4_half_saturation_velocity: float = math.radians(100.0)

class Brain:
    def __init__(self, parameters: BrainParameters | None = None):
        self.parameters = parameters or BrainParameters()

    def process(self, observation: VisualObservation, dt: float) -> NeuralActivity:
        if dt <= 0 or not math.isfinite(dt):
              raise ValueError("dt must be finite and positive")

        theta = observation.angular_size
        theta_dot = observation.angular_velocity

        if theta == 0:
            lplc2 = 0.0
        else:
            log_distance = math.log(theta / self.parameters.lplc2_preffered_angle)
            lplc2 = math.exp(-(log_distance**2) / (2 * self.parameters.lplc2_log_width**2))

        expansion_velocity = max(0.0, theta_dot)
        lc4 = expansion_velocity / (
              expansion_velocity
              + self.parameters.lc4_half_saturation_velocity
          )

        return NeuralActivity(lplc2=lplc2, lc4=lc4)

    def reset(self) -> None:
        """Initial brain model has no temporal state"""