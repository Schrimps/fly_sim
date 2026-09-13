import math
from dataclasses import dataclass

@dataclass
class LoomingObject:
    distance: float
    radius: float
    speed: float

    def __post_init__(self) -> None:
        values = (self.distance, self.radius, self.speed)

        if not all(math.isfinite(value) for value in values):
            raise ValueError("Object parameters must be finite")

        if self.distance <= 0:
            raise ValueError("Initial distance must be positive")

        if self.radius <= 0:
            raise ValueError("Radius must be positive")

        if self.speed < 0:
            raise ValueError("Approach speed must be non-negative")

@dataclass
class World:
    threat: LoomingObject

    @property
    def collision_occurred(self) -> bool:
        return self.threat.distance <= 0.0

    def step(self, dt: float) -> None:
        if dt < 0.0 or not math.isfinite(dt):
            raise ValueError("dt must ne a finite non-negative number")

        if dt == 0.0 or self.collision_occurred:
            return

        new_distance = (
          self.threat.distance
          - self.threat.speed * dt
        )

        if new_distance <= 0:
            self.threat.distance = 0.0
            self.threat.speed = 0.0
        else:
            self.threat.distance = new_distance