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
        x, y = self.x, self.y
        w, h = PLAYER_WIDTH, PLAYER_HEIGHT

        # 1. Zadné kolesá (väčšie, dole)
        pygame.draw.rect(screen, (20, 20, 20), (x - w//2 - 5, y + h - 35, 16, 25))
        pygame.draw.rect(screen, (20, 20, 20), (x + w//2 - 11, y + h - 35, 16, 25))

        # 2. Telo (zužujúce sa smerom hore)
        # Hlavný trup
        pygame.draw.rect(screen, (200, 0, 0), (x - w//4, y + 15, w//2, h - 25))
        # Nos formuly
        pygame.draw.polygon(screen, (255, 0, 0), [
            (x - w//4, y + 15), (x + w//4, y + 15), (x, y)
        ])

        # 3. Predné kolesá (menšie, hore)
        pygame.draw.rect(screen, (20, 20, 20), (x - w//2 - 2, y + 15, 12, 18))
        pygame.draw.rect(screen, (20, 20, 20), (x + w//2 - 10, y + 15, 12, 18))

        # 4. Spojlery
        pygame.draw.rect(screen, (150, 0, 0), (x - w//2, y + h - 10, w, 10)) # Zadný
        pygame.draw.rect(screen, (50, 50, 50), (x - w//3, y + 5, w//1.5, 5)) # Predný krídelko

        # 5. Kokpit (prilba)
        pygame.draw.circle(screen, (255, 255, 255), (x, y + h // 2 + 5), w // 6)

        return pygame.Rect(x - w//2, y, w, h)