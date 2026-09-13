# renderer.py

import math

from brain import NeuralActivity
import pygame

from vision import VisualObservation
from world import World


class Renderer:
    STIMULUS_HEIGHT = 500
    DEBUG_HEIGHT = 200

    def __init__(
        self,
        screen: pygame.Surface,
        width: int,
        height: int,
        horizontal_fov: float = math.radians(120),
    ) -> None:
        self.screen = screen
        self.width = width
        self.height = height

        if height < self.STIMULUS_HEIGHT + self.DEBUG_HEIGHT:
            raise ValueError(
                f"Renderer requires a height of at least "
                f"{self.STIMULUS_HEIGHT + self.DEBUG_HEIGHT}px"
            )

        self.horizontal_fov = horizontal_fov
        self.pixels_per_radian = width / horizontal_fov

        self.stimulus_center = (
            width // 2,
            self.STIMULUS_HEIGHT // 2,
        )

        self.font = pygame.font.SysFont(None, 28)

    def draw(
        self,
        world: World,
        observation: VisualObservation,
        activity: NeuralActivity,
        paused: bool,
    ) -> None:
        self.screen.fill("white")

        self._draw_stimulus(observation)
        self._draw_separator()
        self._draw_debug_info(world, observation, activity, paused)

        pygame.display.flip()

    def _draw_stimulus(
        self,
        observation: VisualObservation,
    ) -> None:
        """
        Render the apparent angular size of the looming object.

        The visual field spans `horizontal_fov` radians across
        the full window width.
        """

        diameter_px = (
            observation.angular_size
            * self.pixels_per_radian
        )

        radius_px = max(
            1,
            round(diameter_px / 2),
        )

        previous_clip = self.screen.get_clip()

        self.screen.set_clip(
            pygame.Rect(
                0,
                0,
                self.width,
                self.STIMULUS_HEIGHT,
            )
        )
    
        pygame.draw.circle(
            self.screen,
            "black",
            self.stimulus_center,
            radius_px,
        )

        self.screen.set_clip(previous_clip)

    def _draw_separator(self) -> None:
        pygame.draw.line(
            self.screen,
            "black",
            (0, self.STIMULUS_HEIGHT),
            (self.width, self.STIMULUS_HEIGHT),
            width=1,
        )

    def _draw_debug_info(
        self,
        world: World,
        observation: VisualObservation,
        activity: NeuralActivity,
        paused: bool,
    ) -> None:
        threat = world.threat

        if threat.distance <= 0:
            ttc = 0.0
        elif threat.speed > 0:
            ttc = (threat.distance / threat.speed) if threat.speed > 0 else math.inf
        else:
            ttc = math.inf

        angular_size_deg = math.degrees(
            observation.angular_size
        )

        angular_velocity_deg = math.degrees(
            observation.angular_velocity
        )

        if world.collision_occurred:
            status = "Collision"
        elif paused:
            status = "Paused"
        else:
            status = "Running"

        lines = [
            f"Status:            {status}",
            f"Distance:          {threat.distance:.3f}",
            f"Object radius:     {threat.radius:.3f}",
            f"Approach speed:    {threat.speed:.3f}",
            f"Angular size:      {angular_size_deg:.2f} deg",
            f"Angular velocity:  {angular_velocity_deg:.2f} deg/s",
            f"TTC:               {ttc:.3f} s",
            f"LPLC2:             {activity.lplc2:.3f}",
            f"LC4:               {activity.lc4:.3f}",
        ]

        x = 20
        y = self.STIMULUS_HEIGHT + 15
        line_height = 28
        lines_per_column = (len(lines) + 1) // 2

        for i, line in enumerate(lines):
            column = i // lines_per_column
            row = i % lines_per_column

            text = self.font.render(
                line,
                True,
                "black",
            )

            self.screen.blit(
                text,
                (
                    x + column * (self.width // 2),
                    y + row * line_height,
                ),
            )
