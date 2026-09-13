import math
import unittest

from vision import VisionSystem
from world import LoomingObject, World


class VisionSystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.world = World(
            threat=LoomingObject(
                distance=10.0,
                radius=0.5,
                speed=2.0,
            )
        )
        self.vision = VisionSystem()

    def test_angular_size_uses_object_geometry(self) -> None:
        observation = self.vision.observe(
            self.world,
            dt=0.1,
        )

        expected = 2 * math.atan2(0.5, 10.0)

        self.assertAlmostEqual(
            observation.angular_size,
            expected,
        )

    def test_first_angular_velocity_is_zero(self) -> None:
        observation = self.vision.observe(
            self.world,
            dt=0.1,
        )

        self.assertEqual(
            observation.angular_velocity,
            0.0,
        )

    def test_angular_velocity_is_finite_difference(self) -> None:
        first = self.vision.observe(
            self.world,
            dt=0.1,
        )

        self.world.threat.distance = 9.0

        second = self.vision.observe(
            self.world,
            dt=0.1,
        )

        expected = (
            second.angular_size - first.angular_size
        ) / 0.1

        self.assertAlmostEqual(
            second.angular_velocity,
            expected,
        )
        self.assertGreater(
            second.angular_velocity,
            0.0,
        )

    def test_reset_clears_angular_velocity_history(self) -> None:
        self.vision.observe(self.world, dt=0.1)

        self.world.threat.distance = 9.0
        self.vision.observe(self.world, dt=0.1)

        self.vision.reset()

        observation = self.vision.observe(
            self.world,
            dt=0.1,
        )

        self.assertEqual(
            observation.angular_velocity,
            0.0,
        )

    def test_non_positive_dt_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.vision.observe(self.world, dt=0.0)

        with self.assertRaises(ValueError):
            self.vision.observe(self.world, dt=-0.1)

    def test_angular_size_at_collision_is_180_degrees(self) -> None:
        self.world.threat.distance = 0.0

        observation = self.vision.observe(
            self.world,
            dt=0.1,
        )

        self.assertAlmostEqual(
            observation.angular_size,
            math.pi,
        )


if __name__ == "__main__":
    unittest.main()