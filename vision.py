from world import World
from dataclasses import dataclass
import math

@dataclass
class VisualObservation:
    angular_size: float
    angular_velocity: float
    time_to_collision: float

    
class VisionSystem:
    def __init__(self):
        self._previous_theta: float | None = None

    def observe(self, world: World, dt: float) -> VisualObservation:
        threat = world.threat

        theta = 2 * math.atan2(threat.radius, threat.distance)

        if self._previous_theta is None:
            theta_dot = 0.0
        else:
            theta_dot = (theta - self._previous_theta) / dt

        self._previous_theta = theta

        if threat.speed > 0:
            ttc = threat.distance / threat.speed
        else:
            ttc = math.inf

        return VisualObservation(
            angular_size=theta,
            angular_velocity=theta_dot,
            time_to_collision=ttc
        )

    def reset(self) -> None:
        self._previous_theta = None
    