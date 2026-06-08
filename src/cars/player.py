import pygame
from src.settings import *

class Player:
    def __init__(self, x, y, color=PLAYER_COLOR, skin=None):
        self.x = x
        self.y = y
        self.speed = 8
        self.color = color
        self.skin = skin

    def update(self, keys=None, left=False, right=False, up=False, down=False):
        if keys is not None:
            if keys[pygame.K_LEFT]:
                self.x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.x += self.speed
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

        if self.skin:
            body_c = self.skin["body"]
            spoiler_c = self.skin["spoiler"]
            wing_c = self.skin["wing"]
            helmet_c = self.skin["helmet"]
        else:
            body_c = self.color
            spoiler_c = (150, 0, 0)
            wing_c = (50, 50, 50)
            helmet_c = (255, 255, 255)

        # 1. Zadne kolesa
        pygame.draw.rect(screen, (20, 20, 20), (x - w//2 - 5, y + h - 35, 16, 25))
        pygame.draw.rect(screen, (20, 20, 20), (x + w//2 - 11, y + h - 35, 16, 25))

        # 2. Telo
        pygame.draw.rect(screen, body_c, (x - w//4, y + 15, w//2, h - 25))
        pygame.draw.polygon(screen, body_c, [
            (x - w//4, y + 15), (x + w//4, y + 15), (x, y)
        ])

        # 3. Predne kolesa
        pygame.draw.rect(screen, (20, 20, 20), (x - w//2 - 2, y + 15, 12, 18))
        pygame.draw.rect(screen, (20, 20, 20), (x + w//2 - 10, y + 15, 12, 18))

        # 4. Spoilery
        pygame.draw.rect(screen, spoiler_c, (x - w//2, y + h - 10, w, 10))
        pygame.draw.rect(screen, wing_c, (x - w//3, y + 5, w//1.5, 5))

        # 5. Kokpit
        pygame.draw.circle(screen, helmet_c, (x, y + h // 2 + 5), w // 6)

        return pygame.Rect(x - w//2, y, w, h)
