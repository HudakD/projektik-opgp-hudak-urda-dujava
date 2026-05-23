import pygame
from src.settings import *

class Player:
    def __init__(self, x, y, color=PLAYER_COLOR):
        self.x = x
        self.y = y
        self.speed = 8
        self.color = color

    def update(self, keys=None, left=False, right=False, up=False, down=False):
        """
        Update player position.

        Accepts either a pygame key state (`keys`) or boolean flags (left/right/up/down).
        This keeps compatibility with older call sites that pass booleans.
        """
        if keys is not None:
            if keys[pygame.K_LEFT]:
                self.x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.x += self.speed
            # vertical movement from key state
            if keys[pygame.K_UP]:
                self.y -= self.speed
            if keys[pygame.K_DOWN]:
                self.y += self.speed
        else:
            if left:
                self.x -= self.speed
            if right:
                self.x += self.speed
            if up:
                self.y -= self.speed
            if down:
                self.y += self.speed
        self.x = max(PLAYER_WIDTH // 2, min(WIDTH - PLAYER_WIDTH // 2, self.x))
        self.y = max(0, min(HEIGHT - PLAYER_HEIGHT, self.y))

    def draw(self, screen):
        x, y = self.x, self.y
        w, h = PLAYER_WIDTH, PLAYER_HEIGHT
        color = self.color

        # 1. Zadné kolesá (väčšie, dole)
        pygame.draw.rect(screen, (20, 20, 20), (x - w//2 - 5, y + h - 35, 16, 25))
        pygame.draw.rect(screen, (20, 20, 20), (x + w//2 - 11, y + h - 35, 16, 25))

        # 2. Telo (zužujúce sa smerom hore)
        # Hlavný trup
        pygame.draw.rect(screen, color, (x - w//4, y + 15, w//2, h - 25))
        # Nos formuly
        pygame.draw.polygon(screen, color, [
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