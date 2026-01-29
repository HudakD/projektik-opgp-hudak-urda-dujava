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

    def draw(self, screen):
        rect = pygame.Rect(
            self.x - PLAYER_WIDTH // 2,
            self.y,
            PLAYER_WIDTH,
            PLAYER_HEIGHT
        )
        pygame.draw.rect(screen, PLAYER_COLOR, rect)
        return rect
