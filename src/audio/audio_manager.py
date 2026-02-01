import pygame
import os
from src.settings import *


class AudioManager:
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.muted = not SOUND_ON
        self.sfx_volume = SFX_VOLUME
        self.engine_volume = ENGINE_VOLUME
        self.path = os.path.join("assets", "sounds")
        self.sounds = {}

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.load_assets()

    def load_assets(self):
        sound_files = {'crash': 'crash.mp3', 'click': 'click.mp3', 'highscore': 'goal.mp3'}
        for key, file in sound_files.items():
            full_path = os.path.join(self.path, file)
            if os.path.exists(full_path):
                try:
                    self.sounds[key] = pygame.mixer.Sound(full_path)
                except:
                    print(f"Chyba pri nacitani: {file}")
        self.update_volumes()

    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        self.update_volumes()

    def change_volume(self, amount):
        self.sfx_volume = max(0.0, min(1.0, self.sfx_volume + amount))
        self.engine_volume = max(0.0, min(1.0, self.engine_volume + amount))
        self.update_volumes()

    def update_volumes(self):
        mult = 0 if self.muted else 1
        for s in self.sounds.values():
            s.set_volume(self.sfx_volume * mult)
        pygame.mixer.music.set_volume(self.engine_volume * mult)

    def play_sfx(self, name):
        if not self.muted and name in self.sounds:
            self.sounds[name].play()

    def start_engine(self):
        path = os.path.join(self.path, 'engine.mp3')
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            self.update_volumes()
            pygame.mixer.music.play(-1)

    def stop_engine(self):
        pygame.mixer.music.stop()

    def update_engine_pitch(self, speed):
        if not self.muted:
            vol = self.engine_volume + (speed / MAX_SCROLL_SPEED) * 0.2
            pygame.mixer.music.set_volume(min(vol, 0.8))