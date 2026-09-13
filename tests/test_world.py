import unittest

from world import LoomingObject, World


class WorldTests(unittest.TestCase):
    def test_step_reduces_distance(self) -> None:
        world = World(
            threat=LoomingObject(
                distance=10.0,
                radius=0.5,
                speed=2.0,
            )
        )

        world.step(0.5)

        self.assertAlmostEqual(
            world.threat.distance,
            9.0,
        )

    def test_step_with_zero_dt_changes_nothing(self) -> None:
        world = World(
            threat=LoomingObject(
                distance=10.0,
                radius=0.5,
                speed=2.0,
            )
        )

        world.step(0.0)

        self.assertEqual(world.threat.distance, 10.0)
        self.assertEqual(world.threat.speed, 2.0)

    def test_negative_dt_is_rejected(self) -> None:
        world = World(
            threat=LoomingObject(
                distance=10.0,
                radius=0.5,
                speed=2.0,
            )
        )

        with self.assertRaises(ValueError):
            world.step(-0.1)

    def test_collision_clamps_distance_and_speed(self) -> None:
        world = World(
            threat=LoomingObject(
                distance=0.1,
                radius=0.5,
                speed=2.0,
            )
        )

        world.step(1.0)

        self.assertEqual(world.threat.distance, 0.0)
        self.assertEqual(world.threat.speed, 0.0)

    def test_zero_speed_leaves_distance_unchanged(self) -> None:
        world = World(
            threat=LoomingObject(
                distance=10.0,
                radius=0.5,
                speed=0.0,
            )
        )

        world.step(1.0)

        self.assertEqual(world.threat.distance, 10.0)


if __name__ == "__main__":
    unittest.main()