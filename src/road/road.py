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
        self.start_center = WIDTH // 2
        self.target_center = WIDTH // 2
        self.curve_timer = 0
        self.curve_duration = 100
        self._init_segments()

    def _init_segments(self):
        y = HEIGHT
        for _ in range(SEGMENTS_COUNT):
            self.segments.append(RoadSegment(y, WIDTH // 2))
            y -= SEGMENT_HEIGHT

    def update(self, scroll_speed):
        for seg in self.segments:
            seg.y += scroll_speed

        self.curve_timer -= 1
        if self.curve_timer <= 0:
            margin = ROAD_WIDTH // 2 + 50
            self.start_center = self.center
            self.target_center = random.randint(margin, WIDTH - margin)
            self.curve_duration = random.randint(80, 160)
            self.curve_timer = self.curve_duration

        t = 1.0 - (self.curve_timer / self.curve_duration)
        eased_t = t * t * (3 - 2 * t)

        self.center = self.start_center + (self.target_center - self.start_center) * eased_t

        while self.segments and self.segments[0].y > HEIGHT + SEGMENT_HEIGHT:
            self.segments.pop(0)

        while len(self.segments) < SEGMENTS_COUNT:
            last = self.segments[-1]
            self.segments.append(RoadSegment(last.y - SEGMENT_HEIGHT, self.center))

    def draw(self, screen):
        for i, seg in enumerate(self.segments):
            if -SEGMENT_HEIGHT < seg.y < HEIGHT + SEGMENT_HEIGHT:
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