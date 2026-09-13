import math
from dataclasses import dataclass

@dataclass
class LoomingObject:
    distance: float
    radius: float
    speed: float

@dataclass
class World:
    threat: LoomingObject

    @property
    def collision_occurred(self) -> bool:
        return self.threat.distance <= 0.0

    def step(self, dt: float) -> None:
        if dt < 0.0:
            raise ValueError("dt must not be negative")

        if dt == 0.0 or self.collision_occurred:
            return

        displacement = self.threat.speed * dt
        self.threat.distance = max(0.0, self.threat.distance - displacement)