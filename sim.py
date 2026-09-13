import math
import pygame
from dataclasses import dataclass
from world import World
from world import LoomingObject
from vision import VisionSystem
from render import Renderer

WIDTH = 1000
HEIGHT = 700
FPS = 60

SPEED_STEP = 0.25
RADIUS_STEP = 0.05

@dataclass(frozen=True)
class TrialParameters:
      distance: float = 10.0
      radius: float = 0.5
      speed: float = 2.0


INITIAL_TRIAL = TrialParameters()

def create_world(parameters: TrialParameters) -> World:
      return World(
          threat=LoomingObject(
              distance=parameters.distance,
              radius=parameters.radius,
              speed=parameters.speed,
          )
      )

def run_sim() -> None:
    pygame.init()
    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
    )
    clock = pygame.time.Clock()

    renderer = Renderer(
        screen=screen,
        width=WIDTH,
        height=HEIGHT,
    )


    world = create_world(INITIAL_TRIAL)

    vision = VisionSystem()

    observation = None
    trial_running = True
    running = True
    trial_was_reset = False

    while running:

        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    world = create_world(INITIAL_TRIAL)
                    vision.reset()

                    trial_running = True
                    trial_was_reset = True
                elif event.key == pygame.K_UP:
                    world.threat.speed += SPEED_STEP

                elif event.key == pygame.K_DOWN:
                    world.threat.speed = max(
                        0.0,
                        world.threat.speed - SPEED_STEP,
                    )

                elif event.key == pygame.K_RIGHT:
                    world.threat.radius += RADIUS_STEP

                elif event.key == pygame.K_LEFT:
                    world.threat.radius = max(
                        0.05,
                        world.threat.radius - RADIUS_STEP,
        )

        if not running:
            break

        if trial_running:
            world.step(dt)

        observation = vision.observe(world, dt)

        if world.collision_occurred:
            trial_running = False

        renderer.draw(
            world=world,
            observation=observation,
        )

    pygame.quit()
