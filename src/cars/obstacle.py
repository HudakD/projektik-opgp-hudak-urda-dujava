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
        return rect
