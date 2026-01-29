import pygame
import random
from src.settings import *
from src.road.road import Road
from src.cars.player import Player
from src.cars.obstacle import ObstacleCar

MIN_OBSTACLE_GAP = 300

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("F1 TURBO")
        self.clock = pygame.time.Clock()
        self.running = True

        self.road = Road()
        self.player = Player(WIDTH // 2, HEIGHT - 130)
        self.obstacles = []

    def spawn_obstacle(self):
        if self.obstacles:
            highest = min(o.y for o in self.obstacles)
            if highest > -MIN_OBSTACLE_GAP:
                return

        if random.randint(0, 8) == 0:
            self.obstacles.append(ObstacleCar(-OBSTACLE_HEIGHT))

    def update_obstacles(self):
        for o in self.obstacles:
            o.y += SCROLL_SPEED
        self.obstacles = [o for o in self.obstacles if o.y < HEIGHT + 200]

    def check_collisions(self):
        center = self.road.get_center_at(self.player.y + PLAYER_HEIGHT // 2)
        left = center - ROAD_WIDTH // 2
        right = center + ROAD_WIDTH // 2

        # mimo cesty
        if self.player.x < left or self.player.x > right:
            self.running = False

        player_rect = pygame.Rect(
            self.player.x - PLAYER_WIDTH // 2,
            self.player.y,
            PLAYER_WIDTH,
            PLAYER_HEIGHT
        )

        for o in self.obstacles:
            c = self.road.get_center_at(o.y + OBSTACLE_HEIGHT // 2)
            obstacle_rect = pygame.Rect(
                c - OBSTACLE_WIDTH // 2,
                o.y,
                OBSTACLE_WIDTH,
                OBSTACLE_HEIGHT
            )
            if player_rect.colliderect(obstacle_rect):
                self.running = False

    def draw(self):
        self.screen.fill(GRASS_COLOR)
        self.road.draw(self.screen)

        for o in self.obstacles:
            c = self.road.get_center_at(o.y + OBSTACLE_HEIGHT // 2)
            o.draw(self.screen, c)

        self.player.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()

            self.player.update(keys)
            self.road.update()
            self.spawn_obstacle()
            self.update_obstacles()
            self.draw()
            self.check_collisions()

        pygame.quit()
