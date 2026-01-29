import pygame
import random
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
        self.center = WIDTH // 2   # stred presne pod hráčom
        self.direction = 0
        self.timer = 0
        self._init_segments()

    def _init_segments(self):
        # CESTA ZAČÍNA AJ DOLE NA OBRAZOVKE
        y = HEIGHT
        for _ in range(SEGMENTS_COUNT):
            self.segments.append(RoadSegment(y, self.center))
            y -= SEGMENT_HEIGHT

    def update(self):
        for seg in self.segments:
            seg.y += SCROLL_SPEED

        # tvrdé, kockaté zmeny smeru
        self.timer += 1
        if self.timer > 20:
            self.timer = 0
            self.direction = random.choice([-1, 0, 1])

        self.center += self.direction * 20
        self.center = max(
            ROAD_WIDTH // 2 + 30,
            min(WIDTH - ROAD_WIDTH // 2 - 30, self.center)
        )

        # odstránenie segmentov dole
        while self.segments and self.segments[0].y > HEIGHT + SEGMENT_HEIGHT:
            self.segments.pop(0)

        # pridanie hore
        while len(self.segments) < SEGMENTS_COUNT:
            last = self.segments[-1]
            self.segments.append(
                RoadSegment(last.y - SEGMENT_HEIGHT, self.center)
            )

    def draw(self, screen):
        for seg in self.segments:
            pygame.draw.rect(screen, GRASS_COLOR, (0, seg.y, WIDTH, SEGMENT_HEIGHT))
            pygame.draw.rect(
                screen,
                ROAD_COLOR,
                (
                    seg.center - ROAD_WIDTH // 2,
                    seg.y,
                    ROAD_WIDTH,
                    SEGMENT_HEIGHT
                )
            )

    def get_center_at(self, y):
        for seg in self.segments:
            if seg.y <= y < seg.y + SEGMENT_HEIGHT:
                return seg.center
        return self.center
