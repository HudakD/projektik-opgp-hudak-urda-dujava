import pygame
import math
from src.settings import *


class ModernButton:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hover_progress = 0.0
        self.is_hovered = False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if self.is_hovered else 0.0
        self.hover_progress += (target - self.hover_progress) * 0.2

    def draw(self, screen):
        alpha = int(180 + 75 * self.hover_progress)
        bg_color = (
            int(UI_PANEL_BG[0] + (UI_ACCENT[0] - UI_PANEL_BG[0]) * 0.1 * self.hover_progress),
            int(UI_PANEL_BG[1] + (UI_ACCENT[1] - UI_PANEL_BG[1]) * 0.1 * self.hover_progress),
            int(UI_PANEL_BG[2] + (UI_ACCENT[2] - UI_PANEL_BG[2]) * 0.1 * self.hover_progress),
        )

        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*bg_color, alpha), s.get_rect(), border_radius=12)

        border_color = (
            int(100 + (UI_ACCENT[0] - 100) * self.hover_progress),
            int(100 + (UI_ACCENT[1] - 100) * self.hover_progress),
            int(100 + (UI_ACCENT[2] - 100) * self.hover_progress)
        )
        border_width = 2 if self.hover_progress < 0.5 else 3
        pygame.draw.rect(s, border_color, s.get_rect(), border_width, border_radius=12)
        screen.blit(s, self.rect.topleft)

        text_color = UI_TEXT_MAIN
        y_offset = -2 * self.hover_progress

        shadow_surf = self.font.render(self.text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(self.rect.centerx + 2, self.rect.centery + 2 + y_offset))
        screen.blit(shadow_surf, shadow_rect)

        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.centery + y_offset))
        screen.blit(text_surf, text_rect)

        if self.hover_progress > 0.1:
            glow_rect = pygame.Rect(
                self.rect.x - 5,
                self.rect.y - 5,
                self.rect.width + 10,
                self.rect.height + 10
            )
            pygame.draw.rect(screen, (*UI_ACCENT, int(30 * self.hover_progress)), glow_rect, 2, border_radius=15)

    def is_clicked(self, mouse_pos, mouse_clicked):
        return self.is_hovered and mouse_clicked


class UIManager:
    def __init__(self):
        pygame.font.init()
        self.font_title = pygame.font.SysFont("impact", 100)
        if not self.font_title:
            self.font_title = pygame.font.Font(None, 100)

        self.font_large = pygame.font.Font(None, 60)
        self.font_medium = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tech = pygame.font.SysFont("consolas", 24, bold=True)

        btn_width = 320
        btn_height = 65
        center_x = WIDTH // 2 - btn_width // 2

        self.start_button = ModernButton(center_x, 340, btn_width, btn_height, "ŠTART PRETEKOV", self.font_medium)
        self.continue_button = ModernButton(center_x, HEIGHT // 2 + 80, btn_width, btn_height, "POKRAČOVAŤ",
                                            self.font_medium)

        self.time_tracker = 0

    def draw_glass_panel(self, screen, rect, alpha=200, border=True):
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill((*UI_PANEL_BG, alpha))
        screen.blit(s, rect.topleft)

        if border:
            pygame.draw.rect(screen, (255, 255, 255), rect, 1, border_radius=0)
            corner_len = 20
            pygame.draw.line(screen, UI_ACCENT, rect.topleft, (rect.x + corner_len, rect.y), 3)
            pygame.draw.line(screen, UI_ACCENT, rect.topleft, (rect.x, rect.y + corner_len), 3)
            pygame.draw.line(screen, UI_ACCENT, rect.bottomright, (rect.right - corner_len, rect.bottom), 3)
            pygame.draw.line(screen, UI_ACCENT, rect.bottomright, (rect.right, rect.bottom - corner_len), 3)

    def draw_glowing_text(self, screen, text, font, color, center_pos, glow_radius=2):
        glow_surf = font.render(text, True, color)
        for x in range(-glow_radius, glow_radius + 1):
            for y in range(-glow_radius, glow_radius + 1):
                r = glow_surf.get_rect(center=(center_pos[0] + x, center_pos[1] + y))
                s = glow_surf.copy()
                s.set_alpha(30)
                screen.blit(s, r)

        main_surf = font.render(text, True, (255, 255, 255))
        r = main_surf.get_rect(center=center_pos)
        screen.blit(main_surf, r)

    def draw_animated_bg(self, screen):
        self.time_tracker += 1
        screen.fill(UI_BG_DARK)

        grid_spacing = 60
        offset = (self.time_tracker * 0.5) % grid_spacing

        for x in range(0, WIDTH, grid_spacing):
            pygame.draw.line(screen, (40, 40, 60), (x, 0), (x, HEIGHT))

        for y in range(-grid_spacing, HEIGHT, grid_spacing):
            draw_y = y + offset
            alpha = min(255, int((draw_y / HEIGHT) * 50))
            color = (40 + alpha // 2, 40 + alpha // 2, 60 + alpha)
            pygame.draw.line(screen, color, (0, draw_y), (WIDTH, draw_y))

    def draw_menu(self, screen, highscores, mouse_pos, mouse_clicked):
        self.draw_animated_bg(screen)

        title_text = "F1 TURBO"

        shadow = self.font_title.render(title_text, True, (0, 0, 0))
        s_rect = shadow.get_rect(center=(WIDTH // 2 + 5, 125))
        screen.blit(shadow, s_rect)

        logo_center = (WIDTH // 2, 120)
        self.draw_glowing_text(screen, title_text, self.font_title, UI_ACCENT, logo_center, glow_radius=4)

        self.draw_text(screen, "ULTIMATE RACING EXPERIENCE", self.font_small, UI_TEXT_DIM, WIDTH // 2, 180, center=True)

        self.start_button.update(mouse_pos)
        self.start_button.draw(screen)

        panel_rect = pygame.Rect(WIDTH // 2 - 350, 450, 700, 220)
        self.draw_glass_panel(screen, panel_rect)

        self.draw_text(screen, "TOP JAZDCI", self.font_medium, UI_GOLD, WIDTH // 2, 475, center=True)

        y_off = 520
        for i, entry in enumerate(highscores[:4]):
            color = UI_GOLD if i == 0 else UI_TEXT_MAIN
            name = entry['name'][:12]
            score_val = int(entry['score'])
            score = f"{score_val:05d}"

            self.draw_text(screen, f"{i + 1}.", self.font_small, color, panel_rect.x + 150, y_off)
            self.draw_text(screen, name, self.font_small, UI_TEXT_DIM, panel_rect.x + 200, y_off)

            score_surf = self.font_tech.render(score, True, UI_ACCENT)
            screen.blit(score_surf, (panel_rect.right - 200, y_off))

            y_off += 35

        # UPRAVENÁ NÁPOVEDA PRE ŠÍPKY
        keys_info = "[ TAB: TOP 20 ] [ ESC: PAUZA ] [ M: MUTE ] [ ŠÍPKY HORE/DOLE: HLASITOSŤ ]"
        self.draw_text(screen, keys_info, self.font_tech, (80, 80, 100), WIDTH // 2, HEIGHT - 30, center=True)

        return self.start_button.is_clicked(mouse_pos, mouse_clicked)

    def draw_leaderboard(self, screen, highscores):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 215))
        screen.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 340, 500, 680)
        self.draw_glass_panel(screen, panel_rect, alpha=245)
        self.draw_glowing_text(screen, "TOP 20 REKORDOV", self.font_medium, UI_GOLD, (WIDTH // 2, panel_rect.y + 45))

        y_off = panel_rect.y + 110
        for i, entry in enumerate(highscores[:20]):
            color = UI_GOLD if i == 0 else UI_TEXT_MAIN
            if i % 2 == 0:
                s = pygame.Surface((panel_rect.width - 40, 24), pygame.SRCALPHA)
                s.fill((255, 255, 255, 10))
                screen.blit(s, (panel_rect.x + 20, y_off - 2))
            self.draw_text(screen, f"{i + 1}.", self.font_small, color, panel_rect.x + 40, y_off)
            self.draw_text(screen, entry['name'][:15], self.font_small, UI_TEXT_MAIN, panel_rect.x + 100, y_off)
            self.draw_text(screen, f"{int(entry['score']):06d}", self.font_tech, UI_ACCENT, panel_rect.right - 120,
            y_off)
            y_off += 27

    def draw_hud(self, screen, score, speed, audio_manager):
        top_bar_height = 50
        s = pygame.Surface((WIDTH, top_bar_height))
        s.set_alpha(230)
        s.fill((10, 10, 15))
        screen.blit(s, (0, 0))

        pygame.draw.line(screen, UI_ACCENT, (0, top_bar_height), (WIDTH, top_bar_height), 2)

        score_formatted = f"{int(score):06d}"
        self.draw_text(screen, "SCORE", self.font_small, UI_TEXT_DIM, 40, 12)
        score_surf = self.font_tech.render(score_formatted, True, UI_TEXT_MAIN)
        screen.blit(score_surf, (130, 10))

        # Zobrazenie hlasitosti
        vol_pct = int(audio_manager.engine_volume * 100) if not audio_manager.muted else 0
        vol_color = UI_ACCENT if not audio_manager.muted else UI_WARNING
        vol_text = f"VOL: {vol_pct}%" if not audio_manager.muted else "MUTE"
        self.draw_text(screen, vol_text, self.font_tech, vol_color, 280, 10)

        level = int(score // DIFFICULTY_INCREASE_INTERVAL) + 1
        level_text = f"STAGE {level}"
        level_rect = self.draw_text(screen, level_text, self.font_medium, UI_GOLD, WIDTH // 2, 25, center=True)

        pygame.draw.circle(screen, UI_WARNING, (level_rect.left - 20, 25), 5)
        pygame.draw.circle(screen, UI_WARNING, (level_rect.right + 20, 25), 5)

        self.draw_digital_tachometer(screen, speed)

    def draw_digital_tachometer(self, screen, speed):
        panel_width = 200
        panel_height = 140
        panel_x = WIDTH - panel_width - 20
        panel_y = 70

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        s = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*UI_PANEL_BG, 240), s.get_rect(), border_radius=10)
        screen.blit(s, (panel_x, panel_y))

        pygame.draw.rect(screen, UI_ACCENT, panel_rect, 2, border_radius=10)

        corner_size = 15
        corner_thickness = 3
        corners = [
            [(panel_x, panel_y), (panel_x + corner_size, panel_y)],
            [(panel_x, panel_y), (panel_x, panel_y + corner_size)],
            [(panel_x + panel_width, panel_y), (panel_x + panel_width - corner_size, panel_y)],
            [(panel_x + panel_width, panel_y), (panel_x + panel_width, panel_y + corner_size)],
            [(panel_x, panel_y + panel_height), (panel_x + corner_size, panel_y + panel_height)],
            [(panel_x, panel_y + panel_height), (panel_x, panel_y + panel_height - corner_size)],
            [(panel_x + panel_width, panel_y + panel_height),
            (panel_x + panel_width - corner_size, panel_y + panel_height)],
            [(panel_x + panel_width, panel_y + panel_height),
            (panel_x + panel_width, panel_y + panel_height - corner_size)],
        ]

        for corner in corners:
            pygame.draw.line(screen, UI_ACCENT, corner[0], corner[1], corner_thickness)

        label_y = panel_y + 20
        self.draw_text(screen, "SPEED", self.font_small, UI_TEXT_DIM, panel_x + panel_width // 2, label_y, center=True)

        speed_val = int(speed * 18)
        speed_ratio = min(speed / MAX_SCROLL_SPEED, 1.0)

        if speed_ratio < 0.5:
            color = GAUGE_LOW
        elif speed_ratio < 0.8:
            color = GAUGE_MID
        else:
            color = GAUGE_HIGH

        speed_font = pygame.font.Font(None, 70)
        speed_text = str(speed_val)

        for offset_x in range(-2, 3):
            for offset_y in range(-2, 3):
                if offset_x != 0 or offset_y != 0:
                    glow = speed_font.render(speed_text, True, color)
                    glow.set_alpha(20)
                    glow_rect = glow.get_rect(center=(panel_x + panel_width // 2 + offset_x, panel_y + 70 + offset_y))
                    screen.blit(glow, glow_rect)

        speed_surf = speed_font.render(speed_text, True, (255, 255, 255))
        speed_rect = speed_surf.get_rect(center=(panel_x + panel_width // 2, panel_y + 70))
        screen.blit(speed_surf, speed_rect)

        unit_y = panel_y + 105
        self.draw_text(screen, "KM/H", self.font_tech, UI_TEXT_DIM, panel_x + panel_width // 2, unit_y, center=True)

        bar_width = panel_width - 40
        bar_height = 6
        bar_x = panel_x + 20
        bar_y = panel_y + panel_height - 20

        pygame.draw.rect(screen, (30, 30, 40), (bar_x, bar_y, bar_width, bar_height), border_radius=3)

        filled_width = int(bar_width * speed_ratio)
        if filled_width > 0:
            pygame.draw.rect(screen, color, (bar_x, bar_y, filled_width, bar_height), border_radius=3)

            for i in range(0, filled_width, 2):
                pulse_alpha = int(50 + 50 * math.sin(self.time_tracker * 0.1 + i * 0.1))
                pulse_surf = pygame.Surface((2, bar_height), pygame.SRCALPHA)
                pulse_surf.fill((*color, pulse_alpha))
                screen.blit(pulse_surf, (bar_x + i, bar_y))

    def draw_game_over_screen(self, screen, score, is_highscore, mouse_pos, mouse_clicked):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(240)
        overlay.fill((5, 5, 10))
        screen.blit(overlay, (0, 0))

        panel_width = 600
        panel_height = 400
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        glow_rect = panel_rect.copy()
        glow_rect.inflate_ip(20, 20)
        pygame.draw.rect(screen, (UI_WARNING[0], UI_WARNING[1], UI_WARNING[2], 50), glow_rect, border_radius=20)

        self.draw_glass_panel(screen, panel_rect, alpha=255)

        title = "MISSION FAILED" if not is_highscore else "NEW RECORD!"
        color = UI_WARNING if not is_highscore else UI_GOLD

        self.draw_glowing_text(screen, title, self.font_large, color, (WIDTH // 2, panel_y + 60))

        pygame.draw.rect(screen, (0, 0, 0), (WIDTH // 2 - 150, panel_y + 120, 300, 80), border_radius=10)
        pygame.draw.rect(screen, color, (WIDTH // 2 - 150, panel_y + 120, 300, 80), 2, border_radius=10)

        self.draw_text(screen, "FINAL SCORE", self.font_small, UI_TEXT_DIM, WIDTH // 2, panel_y + 135, center=True)
        self.draw_text(screen, str(int(score)), self.font_large, (255, 255, 255), WIDTH // 2, panel_y + 170,
        center=True)

        if is_highscore:
            self.draw_text(screen, "Zadaj meno a stlač ENTER", self.font_small, UI_ACCENT, WIDTH // 2, panel_y + 225,
            center=True)
        else:
            self.continue_button.update(mouse_pos)
            self.continue_button.draw(screen)
            return self.continue_button.is_clicked(mouse_pos, mouse_clicked)

        return False

    def draw_name_input(self, screen, name):
        input_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 + 50, 400, 60)
        pygame.draw.rect(screen, (0, 0, 0), input_rect, border_radius=5)
        pygame.draw.rect(screen, UI_ACCENT, input_rect, 2, border_radius=5)

        cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        txt_surf = self.font_medium.render(name + cursor, True, UI_TEXT_MAIN)
        screen.blit(txt_surf, (input_rect.x + 20, input_rect.y + 15))

    def draw_text(self, screen, text, font, color, x, y, center=False):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()

        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)

        screen.blit(text_surface, text_rect)
        return text_rect