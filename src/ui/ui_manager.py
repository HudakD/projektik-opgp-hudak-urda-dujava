import pygame
from src.settings import *


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color

        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3, border_radius=10)

        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def is_clicked(self, mouse_pos, mouse_clicked):
        if self.rect.collidepoint(mouse_pos) and mouse_clicked:
            return True
        return False


class UIManager:
    def __init__(self):
        pygame.font.init()
        self.font_title = pygame.font.Font(None, 100)
        self.font_large = pygame.font.Font(None, 60)
        self.font_medium = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)

        self.menu_bg_color = (15, 15, 25)
        self.accent_color = (255, 69, 0)
        self.accent_hover = (255, 100, 40)
        self.secondary_color = (30, 30, 50)
        self.text_color = (240, 240, 240)
        self.gold_color = (255, 215, 0)
        self.silver_color = (192, 192, 192)
        self.bronze_color = (205, 127, 50)

        button_width = 350
        button_height = 70
        button_x = WIDTH // 2 - button_width // 2

        self.start_button = Button(
            button_x, 320,
            button_width, button_height,
            "ŠTART HRY",
            self.accent_color, self.accent_hover, (255, 255, 255)
        )

        self.continue_button = Button(
            button_x, HEIGHT // 2 + 60,
            button_width, button_height,
            "POKRAČOVAŤ",
            self.secondary_color, (50, 50, 70), self.text_color
        )

    def draw_text(self, screen, text, font, color, x, y, center=False):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()

        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)

        screen.blit(text_surface, text_rect)
        return text_rect

    def draw_gradient_bg(self, screen, color1, color2):
        for y in range(HEIGHT):
            blend = y / HEIGHT
            r = int(color1[0] * (1 - blend) + color2[0] * blend)
            g = int(color1[1] * (1 - blend) + color2[1] * blend)
            b = int(color1[2] * (1 - blend) + color2[2] * blend)
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    def draw_menu(self, screen, highscores, mouse_pos, mouse_clicked):
        self.draw_gradient_bg(screen, (10, 10, 20), (30, 15, 40))

        title_y = 100
        for i in range(3):
            offset = 3 - i
            shadow_color = (255 - i * 60, 69 - i * 20, 0)
            self.draw_text(screen, "F1 TURBO", self.font_title, shadow_color,
                           WIDTH // 2 + offset, title_y + offset, center=True)

        self.draw_text(screen, "F1 TURBO", self.font_title, self.gold_color,
                       WIDTH // 2, title_y, center=True)

        subtitle_text = "RACING CHALLENGE"
        self.draw_text(screen, subtitle_text, self.font_small, self.text_color,
                       WIDTH // 2, title_y + 75, center=True)

        self.start_button.check_hover(mouse_pos)
        self.start_button.draw(screen, self.font_medium)

        controls_y = 420
        controls = [
            "← →  Pohyb auta",
            "ESC  Menu / Pauza"
        ]

        for i, control in enumerate(controls):
            self.draw_text(screen, control, self.font_tiny, (180, 180, 180),
                           WIDTH // 2, controls_y + i * 30, center=True)

        scores_title_y = 500
        self.draw_text(screen, "TOP JAZDCI", self.font_large, self.gold_color,
                       WIDTH // 2, scores_title_y, center=True)

        panel_y = scores_title_y + 70
        panel_height = 155
        panel_rect = pygame.Rect(WIDTH // 2 - 400, panel_y, 800, panel_height)

        s = pygame.Surface((panel_rect.width, panel_rect.height))
        s.set_alpha(180)
        s.fill(self.secondary_color)
        screen.blit(s, panel_rect)
        pygame.draw.rect(screen, self.accent_color, panel_rect, 2, border_radius=8)

        y_offset = panel_y + 15
        displayed_count = min(len(highscores), 4)

        for i in range(displayed_count):
            entry = highscores[i]
            rank = i + 1

            if rank == 1:
                rank_color = self.gold_color
            elif rank == 2:
                rank_color = self.silver_color
            elif rank == 3:
                rank_color = self.bronze_color
            else:
                rank_color = self.text_color

            rank_text = f"{rank}."
            name_text = entry['name'][:15]
            score_text = f"{entry['score']} bodov"

            self.draw_text(screen, rank_text, self.font_small, rank_color,
                           WIDTH // 2 - 370, y_offset)
            self.draw_text(screen, name_text, self.font_small, self.text_color,
                           WIDTH // 2 - 320, y_offset)
            self.draw_text(screen, score_text, self.font_small, self.accent_color,
                           WIDTH // 2 + 240, y_offset)

            y_offset += 35

        if len(highscores) == 0:
            self.draw_text(screen, "Zatiaľ žiadne skóre", self.font_small, (120, 120, 120),
                           WIDTH // 2, panel_y + 70, center=True)

        return self.start_button.is_clicked(mouse_pos, mouse_clicked)

    def draw_game_over_screen(self, screen, score, is_highscore, mouse_pos, mouse_clicked):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((10, 10, 15))
        screen.blit(overlay, (0, 0))

        panel_width = 700
        panel_height = 450
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (25, 25, 40), panel_rect, border_radius=20)
        pygame.draw.rect(screen, self.accent_color, panel_rect, 4, border_radius=20)

        self.draw_text(screen, "GAME OVER", self.font_large, self.accent_color,
                       WIDTH // 2, panel_y + 70, center=True)

        score_bg = pygame.Rect(WIDTH // 2 - 250, panel_y + 160, 500, 100)
        pygame.draw.rect(screen, (15, 15, 25), score_bg, border_radius=10)
        pygame.draw.rect(screen, self.gold_color, score_bg, 3, border_radius=10)

        self.draw_text(screen, "SKÓRE", self.font_small, (180, 180, 180),
                       WIDTH // 2, panel_y + 185, center=True)
        self.draw_text(screen, str(int(score)), self.font_large, self.gold_color,
                       WIDTH // 2, panel_y + 220, center=True)

        if is_highscore:
            self.draw_text(screen, "NOVÝ REKORD!", self.font_large, self.gold_color,
                           WIDTH // 2, panel_y + 300, center=True)
            self.draw_text(screen, "Zadaj svoje meno:", self.font_medium, self.text_color,
                           WIDTH // 2, panel_y + 355, center=True)
        else:
            self.continue_button.check_hover(mouse_pos)
            self.continue_button.draw(screen, self.font_medium)
            return self.continue_button.is_clicked(mouse_pos, mouse_clicked)

        return False

    def draw_hud(self, screen, score, speed):
        bar_height = 6
        bar_y = HEIGHT - 30

        pygame.draw.rect(screen, (40, 40, 60), (0, bar_y, WIDTH, 30))

        speed_progress = min(speed / MAX_SCROLL_SPEED, 1.0)
        bar_width = int(WIDTH * speed_progress)

        for i in range(0, bar_width, 2):
            alpha = int(255 * (i / WIDTH))
            color_r = int(255 * speed_progress)
            color_g = int(69 + (186 * (1 - speed_progress)))
            pygame.draw.rect(screen, (color_r, color_g, 0), (i, bar_y, 2, bar_height))

        top_bar_height = 60
        s = pygame.Surface((WIDTH, top_bar_height))
        s.set_alpha(200)
        s.fill((15, 15, 25))
        screen.blit(s, (0, 0))

        score_x = 30
        self.draw_text(screen, "SKÓRE", self.font_tiny, (150, 150, 150), score_x, 8)
        self.draw_text(screen, str(int(score)), self.font_medium, self.gold_color, score_x, 28)

        speed_text = f"{int(speed * 10)} KM/H"
        speed_x = WIDTH - 230
        self.draw_text(screen, "RÝCHLOSŤ", self.font_tiny, (150, 150, 150), speed_x, 8)
        self.draw_text(screen, speed_text, self.font_medium, self.accent_color, speed_x, 28)

        center_panel_width = 250
        center_x = WIDTH // 2 - center_panel_width // 2

        level = int(score // DIFFICULTY_INCREASE_INTERVAL) + 1
        self.draw_text(screen, "LEVEL", self.font_tiny, (150, 150, 150), center_x, 8)
        self.draw_text(screen, str(level), self.font_medium, (100, 200, 255), center_x, 28)

        pygame.draw.line(screen, self.accent_color, (0, top_bar_height), (WIDTH, top_bar_height), 2)

    def draw_name_input(self, screen, name):
        input_panel = pygame.Rect(WIDTH // 2 - 280, HEIGHT // 2 + 70, 560, 70)
        pygame.draw.rect(screen, (15, 15, 25), input_panel, border_radius=10)
        pygame.draw.rect(screen, self.gold_color, input_panel, 3, border_radius=10)

        display_text = name + "_" if len(name) < 15 else name
        self.draw_text(screen, display_text, self.font_medium, self.text_color,
                       WIDTH // 2, HEIGHT // 2 + 105, center=True)

        self.draw_text(screen, "ENTER pre potvrdenie | BACKSPACE pre zmazanie",
                       self.font_tiny, (150, 150, 150), WIDTH // 2, HEIGHT // 2 + 160, center=True)