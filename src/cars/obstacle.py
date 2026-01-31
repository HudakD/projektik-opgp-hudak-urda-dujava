import pygame
from src.settings import *

class ObstacleCar:
    def __init__(self, y):
        self.y = y

    def draw(self, screen, center):
        x, y = center, self.y
        w, h = OBSTACLE_WIDTH, OBSTACLE_HEIGHT

        # 1. Zadné kolesá (väčšie, hore - lebo je otočené)
        pygame.draw.rect(screen, (20, 20, 20), (x - w//2 - 5, y + 10, 16, 25))
        pygame.draw.rect(screen, (20, 20, 20), (x + w//2 - 11, y + 10, 16, 25))

        # 2. Telo (zužujúce sa smerom dole)
        # Hlavný trup
        pygame.draw.rect(screen, (0, 0, 200), (x - w//4, y + 10, w//2, h - 25))
        # Nos formuly smerom dole
        pygame.draw.polygon(screen, (0, 0, 255), [
            (x - w//4, y + h - 15), (x + w//4, y + h - 15), (x, y + h)
        ])

        # 3. Predné kolesá (menšie, dole)
        pygame.draw.rect(screen, (20, 20, 20), (x - w//2 - 2, y + h - 33, 12, 18))
        pygame.draw.rect(screen, (20, 20, 20), (x + w//2 - 10, y + h - 33, 12, 18))

        # 4. Spojlery
        pygame.draw.rect(screen, (0, 0, 150), (x - w//2, y, w, 10)) # Zadný hore
        pygame.draw.rect(screen, (50, 50, 50), (x - w//3, y + h - 10, w//1.5, 5)) # Predný krídelko dole

        # 5. Kokpit
        pygame.draw.circle(screen, (255, 255, 0), (x, y + h // 2 - 5), w // 6)

        return pygame.Rect(x - w//2, y, w, h)