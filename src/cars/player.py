import pygame
from src.settings import *


class Player:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 8

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed

        self.x = max(PLAYER_WIDTH // 2, min(WIDTH - PLAYER_WIDTH // 2, self.x))

    def draw(self, screen):
        rect = pygame.Rect(
            self.x - PLAYER_WIDTH // 2,
            self.y,
            PLAYER_WIDTH,
            PLAYER_HEIGHT
        )
        pygame.draw.rect(screen, PLAYER_COLOR, rect)

        window_rect = pygame.Rect(
            self.x - PLAYER_WIDTH // 4,
            self.y + 10,
            PLAYER_WIDTH // 2,
            PLAYER_HEIGHT // 3
        )
        pygame.draw.rect(screen, (255, 200, 200), window_rect)

        return rect