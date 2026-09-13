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
