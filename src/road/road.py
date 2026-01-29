import pygame
import random
import math
from src.settings import *

SEGMENT_HEIGHT = 20
SEGMENTS_COUNT = 200


class RoadSegment:
    def __init__(self, y, center):
        self.y = y
        self.center = center


class Road:
    def __init__(self):
        self.segments = []
        self.center = WIDTH // 2
        self.curve_speed = 0
        self.curve_change_timer = 0
        self.curve_duration = random.randint(60, 120)
        self._init_segments()

    def _init_segments(self):
        y = HEIGHT
        for _ in range(SEGMENTS_COUNT):
            self.segments.append(RoadSegment(y, WIDTH // 2))
            y -= SEGMENT_HEIGHT

    def update(self, scroll_speed):
        for seg in self.segments:
            seg.y += scroll_speed

        self.curve_change_timer += 1

        if self.curve_change_timer >= self.curve_duration:
            self.curve_change_timer = 0
            self.curve_duration = random.randint(60, 120)

            direction = random.choice([-1, 0, 0, 1])
            self.curve_speed = direction * random.uniform(0.3, 0.8)

        self.center += self.curve_speed
        self.center = max(
            ROAD_WIDTH // 2 + 50,
            min(WIDTH - ROAD_WIDTH // 2 - 50, self.center)
        )

        if self.center <= ROAD_WIDTH // 2 + 50 or self.center >= WIDTH - ROAD_WIDTH // 2 - 50:
            self.curve_speed *= -0.5

        while self.segments and self.segments[0].y > HEIGHT + SEGMENT_HEIGHT:
            self.segments.pop(0)

        while len(self.segments) < SEGMENTS_COUNT:
            last = self.segments[-1]
            new_center = self.center + random.uniform(-5, 5)
            new_center = max(ROAD_WIDTH // 2 + 50, min(WIDTH - ROAD_WIDTH // 2 - 50, new_center))
            self.segments.append(
                RoadSegment(last.y - SEGMENT_HEIGHT, new_center)
            )

    def draw(self, screen):
        for i, seg in enumerate(self.segments):
            pygame.draw.rect(screen, GRASS_COLOR, (0, seg.y, WIDTH, SEGMENT_HEIGHT))

            road_rect = pygame.Rect(
                seg.center - ROAD_WIDTH // 2,
                seg.y,
                ROAD_WIDTH,
                SEGMENT_HEIGHT
            )
            pygame.draw.rect(screen, ROAD_COLOR, road_rect)

            if i % 4 < 2:
                line_rect = pygame.Rect(
                    seg.center - 3,
                    seg.y,
                    6,
                    SEGMENT_HEIGHT
                )
                pygame.draw.rect(screen, YELLOW, line_rect)

    def get_center_at(self, y):
        for seg in self.segments:
            if seg.y <= y < seg.y + SEGMENT_HEIGHT:
                return seg.center
        return self.center