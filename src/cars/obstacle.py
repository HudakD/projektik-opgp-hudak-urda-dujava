import pygame
from src.settings import *


class ObstacleCar:

    def __init__(self, y):
        self.y = y

    def draw(self, screen, center):
        rect = pygame.Rect(
            center - OBSTACLE_WIDTH // 2,
            self.y,
            OBSTACLE_WIDTH,
            OBSTACLE_HEIGHT
        )
        pygame.draw.rect(screen, OBSTACLE_COLOR, rect)

        window_rect = pygame.Rect(
            center - OBSTACLE_WIDTH // 4,
            self.y + OBSTACLE_HEIGHT - 40,
            OBSTACLE_WIDTH // 2,
            OBSTACLE_HEIGHT // 3
        )
        pygame.draw.rect(screen, (150, 150, 255), window_rect)

        return rect