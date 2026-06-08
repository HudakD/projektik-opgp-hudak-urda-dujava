import pygame
import math
from src.settings import COIN_SIZE, UI_GOLD


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = COIN_SIZE
        self.anim_offset = 0.0

    def update(self, speed):
        self.y += speed
        self.anim_offset += 0.15

    def draw(self, screen):
        # Pulsating gold coin
        pulse = math.sin(self.anim_offset) * 3
        r = int(self.size // 2 + pulse)
        # Outer glow
        glow_surf = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 215, 0, 40), (r * 2, r * 2), r * 2)
        screen.blit(glow_surf, (int(self.x) - r * 2, int(self.y) - r * 2))
        # Main coin body
        pygame.draw.circle(screen, UI_GOLD, (int(self.x), int(self.y)), r)
        pygame.draw.circle(screen, (200, 170, 0), (int(self.x), int(self.y)), r, 2)
        # Inner highlight
        pygame.draw.circle(screen, (255, 240, 150), (int(self.x) - r // 3, int(self.y) - r // 3), r // 3)
        # "$" symbol
        small_font = pygame.font.Font(None, r + 4)
        txt = small_font.render("$", True, (180, 150, 0))
        tr = txt.get_rect(center=(int(self.x), int(self.y) + 1))
        screen.blit(txt, tr)

    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

    def is_offscreen(self):
        return self.y > pygame.display.get_surface().get_height() + 50
