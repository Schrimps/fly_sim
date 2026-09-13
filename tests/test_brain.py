import math
import unittest

from brain import Brain, BrainParameters, NeuralActivity
from vision import VisualObservation


class BrainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parameters = BrainParameters()
        self.brain = Brain(self.parameters)

    def process(
        self,
        angular_size: float,
        angular_velocity: float = 0.0,
        dt: float = 0.1,
    ) -> NeuralActivity:
        return self.brain.process(
            VisualObservation(
                angular_size=angular_size,
                angular_velocity=angular_velocity,
            ),
            dt=dt,
        )

    def test_default_parameters_match_documented_assumptions(self) -> None:
        self.assertAlmostEqual(
            self.parameters.lplc2_preferred_angle,
            math.radians(42.0),
        )
        self.assertAlmostEqual(
            self.parameters.lplc2_log_width,
            0.52,
        )
        self.assertAlmostEqual(
            self.parameters.lc4_half_saturation_velocity,
            math.radians(100.0),
        )

    def test_lplc2_is_zero_at_zero_angular_size(self) -> None:
        activity = self.process(angular_size=0.0)

        self.assertEqual(activity.lplc2, 0.0)

    def test_lplc2_peaks_at_preferred_angular_size(self) -> None:
        activity = self.process(
            angular_size=self.parameters.lplc2_preferred_angle,
        )

        self.assertAlmostEqual(activity.lplc2, 1.0)

    def test_lplc2_falls_on_both_sides_of_preferred_size(self) -> None:
        preferred = self.parameters.lplc2_preferred_angle

        smaller = self.process(angular_size=preferred / 2)
        preferred_activity = self.process(angular_size=preferred)
        larger = self.process(angular_size=preferred * 2)

        self.assertLess(smaller.lplc2, preferred_activity.lplc2)
        self.assertLess(larger.lplc2, preferred_activity.lplc2)

    def test_lplc2_is_symmetric_in_log_angular_size(self) -> None:
        preferred = self.parameters.lplc2_preferred_angle
        width = self.parameters.lplc2_log_width

        smaller = self.process(
            angular_size=preferred * math.exp(-width),
        )
        larger = self.process(
            angular_size=preferred * math.exp(width),
        )

        self.assertAlmostEqual(smaller.lplc2, larger.lplc2)

    def test_lc4_is_zero_for_non_expanding_stimuli(self) -> None:
        stationary = self.process(
            angular_size=math.radians(20.0),
            angular_velocity=0.0,
        )
        contracting = self.process(
            angular_size=math.radians(20.0),
            angular_velocity=math.radians(-50.0),
        )

        self.assertEqual(stationary.lc4, 0.0)
        self.assertEqual(contracting.lc4, 0.0)

    def test_lc4_is_half_active_at_half_saturation_velocity(self) -> None:
        activity = self.process(
            angular_size=math.radians(20.0),
            angular_velocity=(
                self.parameters.lc4_half_saturation_velocity
            ),
        )

        self.assertAlmostEqual(activity.lc4, 0.5)

    def test_lc4_increases_with_expansion_velocity(self) -> None:
        slow = self.process(
            angular_size=math.radians(20.0),
            angular_velocity=math.radians(10.0),
        )
        fast = self.process(
            angular_size=math.radians(20.0),
            angular_velocity=math.radians(200.0),
        )

        self.assertLess(slow.lc4, fast.lc4)

    def test_activities_are_bounded(self) -> None:
        observations = [
            (0.0, 0.0),
            (math.radians(1.0), math.radians(-100.0)),
            (math.radians(42.0), math.radians(100.0)),
            (math.pi, math.radians(1_000_000.0)),
        ]

        for angular_size, angular_velocity in observations:
            with self.subTest(
                angular_size=angular_size,
                angular_velocity=angular_velocity,
            ):
                activity = self.process(
                    angular_size=angular_size,
                    angular_velocity=angular_velocity,
                )

                self.assertGreaterEqual(activity.lplc2, 0.0)
                self.assertLessEqual(activity.lplc2, 1.0)
                self.assertGreaterEqual(activity.lc4, 0.0)
                self.assertLessEqual(activity.lc4, 1.0)

    def test_non_positive_or_non_finite_dt_is_rejected(self) -> None:
        for dt in (0.0, -0.1, math.nan, math.inf, -math.inf):
            with self.subTest(dt=dt):
                with self.assertRaises(ValueError):
                    self.process(
                        angular_size=math.radians(20.0),
                        dt=dt,
                    )

    def test_invalid_observation_is_rejected(self) -> None:
        invalid_observations = [
            VisualObservation(-0.1, 0.0),
            VisualObservation(math.nan, 0.0),
            VisualObservation(math.inf, 0.0),
            VisualObservation(0.1, math.nan),
            VisualObservation(0.1, math.inf),
        ]

        for observation in invalid_observations:
            with self.subTest(observation=observation):
                with self.assertRaises(ValueError):
                    self.brain.process(observation, dt=0.1)

    def test_invalid_parameters_are_rejected(self) -> None:
        invalid_parameters = [
            BrainParameters(lplc2_preferred_angle=0.0),
            BrainParameters(lplc2_preferred_angle=-0.1),
            BrainParameters(lplc2_log_width=0.0),
            BrainParameters(lplc2_log_width=-0.1),
            BrainParameters(lc4_half_saturation_velocity=0.0),
            BrainParameters(lc4_half_saturation_velocity=-0.1),
            BrainParameters(lplc2_preferred_angle=math.inf),
            BrainParameters(lplc2_log_width=math.nan),
            BrainParameters(lc4_half_saturation_velocity=math.inf),
        ]

        for parameters in invalid_parameters:
            with self.subTest(parameters=parameters):
                with self.assertRaises(ValueError):
                    Brain(parameters)

    def test_reset_preserves_stateless_response(self) -> None:
        observation = VisualObservation(
            angular_size=math.radians(42.0),
            angular_velocity=math.radians(100.0),
        )

        before_reset = self.brain.process(observation, dt=0.1)
        self.brain.reset()
        after_reset = self.brain.process(observation, dt=0.1)

        self.assertEqual(after_reset, before_reset)


if __name__ == "__main__":
    unittest.main()
