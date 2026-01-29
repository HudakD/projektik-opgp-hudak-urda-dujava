import pygame
import random
from src.settings import *
from src.road.road import Road
from src.cars.player import Player
from src.cars.obstacle import ObstacleCar
from src.score.score_manager import ScoreManager
from src.ui.ui_manager import UIManager

MIN_OBSTACLE_GAP = 300


class GameState:
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    ENTERING_NAME = 3
    PAUSED = 4


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("F1 TURBO")
        self.clock = pygame.time.Clock()
        self.running = True

        self.score_manager = ScoreManager()
        self.ui_manager = UIManager()

        self.state = GameState.MENU
        self.player_name = ""

        self.road = None
        self.player = None
        self.obstacles = []

        self.current_speed = INITIAL_SCROLL_SPEED
        self.obstacle_spawn_rate = 8
        self.last_difficulty_score = 0

    def reset_game(self):
        self.road = Road()
        self.player = Player(WIDTH // 2, HEIGHT - 130)
        self.obstacles = []
        self.score_manager.reset_score()
        self.current_speed = INITIAL_SCROLL_SPEED
        self.obstacle_spawn_rate = 8
        self.last_difficulty_score = 0
        self.player_name = ""

    def increase_difficulty(self):
        if self.current_speed < MAX_SCROLL_SPEED:
            self.current_speed += SPEED_INCREASE

        if self.obstacle_spawn_rate > 3:
            self.obstacle_spawn_rate -= OBSTACLE_SPAWN_INCREASE

    def update_difficulty(self):
        score = self.score_manager.get_current_score()

        if score >= self.last_difficulty_score + DIFFICULTY_INCREASE_INTERVAL:
            self.increase_difficulty()
            self.last_difficulty_score = score

    def spawn_obstacle(self):
        if self.obstacles:
            highest = min(o.y for o in self.obstacles)
            if highest > -MIN_OBSTACLE_GAP:
                return

        if random.randint(0, self.obstacle_spawn_rate) == 0:
            self.obstacles.append(ObstacleCar(-OBSTACLE_HEIGHT))

    def update_obstacles(self):
        for o in self.obstacles:
            o.y += self.current_speed

        before_count = len(self.obstacles)
        self.obstacles = [o for o in self.obstacles if o.y < HEIGHT + 200]
        after_count = len(self.obstacles)

        passed = before_count - after_count - sum(1 for o in self.obstacles if o.y < self.player.y)
        if passed > 0:
            self.score_manager.increment_score(passed)

    def check_collisions(self):
        center = self.road.get_center_at(self.player.y + PLAYER_HEIGHT // 2)
        left = center - ROAD_WIDTH // 2
        right = center + ROAD_WIDTH // 2

        if self.player.x - PLAYER_WIDTH // 2 < left or self.player.x + PLAYER_WIDTH // 2 > right:
            return True

        player_rect = pygame.Rect(
            self.player.x - PLAYER_WIDTH // 2,
            self.player.y,
            PLAYER_WIDTH,
            PLAYER_HEIGHT
        )

        for o in self.obstacles:
            c = self.road.get_center_at(o.y + OBSTACLE_HEIGHT // 2)
            obstacle_rect = pygame.Rect(
                c - OBSTACLE_WIDTH // 2,
                o.y,
                OBSTACLE_WIDTH,
                OBSTACLE_HEIGHT
            )
            if player_rect.colliderect(obstacle_rect):
                return True

        return False

    def handle_menu_input(self, event, mouse_pos, mouse_clicked):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.reset_game()
                self.state = GameState.PLAYING

    def handle_playing_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.PAUSED

    def handle_paused_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.PLAYING
            elif event.key == pygame.K_q:
                self.state = GameState.MENU

    def handle_game_over_input(self, event, mouse_pos, mouse_clicked):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                score = self.score_manager.get_current_score()
                if self.score_manager.is_highscore(score):
                    self.state = GameState.ENTERING_NAME
                else:
                    self.state = GameState.MENU
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU

    def handle_name_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(self.player_name) > 0:
                self.score_manager.add_score(self.player_name, self.score_manager.get_current_score())
                self.state = GameState.MENU
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif len(self.player_name) < 15:
                if event.unicode.isalnum() or event.unicode == ' ':
                    self.player_name += event.unicode

    def update_game(self):
        keys = pygame.key.get_pressed()

        self.player.update(keys)
        self.road.update(self.current_speed)
        self.spawn_obstacle()
        self.update_obstacles()
        self.update_difficulty()

        if pygame.time.get_ticks() % 10 == 0:
            self.score_manager.increment_score(0.1)

        if self.check_collisions():
            self.state = GameState.GAME_OVER

    def draw_game(self):
        self.screen.fill(GRASS_COLOR)
        self.road.draw(self.screen)

        for o in self.obstacles:
            c = self.road.get_center_at(o.y + OBSTACLE_HEIGHT // 2)
            o.draw(self.screen, c)

        self.player.draw(self.screen)

        self.ui_manager.draw_hud(self.screen, int(self.score_manager.get_current_score()), self.current_speed)

    def draw_pause_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 200))
        self.screen.blit(overlay, (0, 0))

        panel_width = 500
        panel_height = 300
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        self.ui_manager.draw_glass_panel(self.screen, panel_rect, alpha=255)

        self.ui_manager.draw_text(self.screen, "PAUZA", self.ui_manager.font_large,
                                  UI_GOLD, WIDTH // 2, panel_y + 80, center=True)

        self.ui_manager.draw_text(self.screen, "ESC - Pokračovať", self.ui_manager.font_medium,
                                  UI_TEXT_MAIN, WIDTH // 2, panel_y + 160, center=True)
        self.ui_manager.draw_text(self.screen, "Q - Späť do menu", self.ui_manager.font_medium,
                                  UI_TEXT_DIM, WIDTH // 2, panel_y + 210, center=True)

    def run(self):
        while self.running:
            self.clock.tick(FPS)

            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_clicked = True

                if self.state == GameState.MENU:
                    self.handle_menu_input(event, mouse_pos, mouse_clicked)
                elif self.state == GameState.PLAYING:
                    self.handle_playing_input(event)
                elif self.state == GameState.PAUSED:
                    self.handle_paused_input(event)
                elif self.state == GameState.GAME_OVER:
                    self.handle_game_over_input(event, mouse_pos, mouse_clicked)
                elif self.state == GameState.ENTERING_NAME:
                    self.handle_name_input(event)

            if self.state == GameState.MENU:
                if self.ui_manager.draw_menu(self.screen, self.score_manager.get_highscores(), mouse_pos,
                                             mouse_clicked):
                    self.reset_game()
                    self.state = GameState.PLAYING

            elif self.state == GameState.PLAYING:
                self.update_game()
                self.draw_game()

            elif self.state == GameState.PAUSED:
                self.draw_game()
                self.draw_pause_screen()

            elif self.state == GameState.GAME_OVER:
                self.draw_game()
                score = self.score_manager.get_current_score()
                is_highscore = self.score_manager.is_highscore(score)
                if self.ui_manager.draw_game_over_screen(self.screen, int(score), is_highscore, mouse_pos,
                                                         mouse_clicked):
                    self.state = GameState.MENU

            elif self.state == GameState.ENTERING_NAME:
                self.draw_game()
                score = self.score_manager.get_current_score()
                self.ui_manager.draw_game_over_screen(self.screen, int(score), True, mouse_pos, False)
                self.ui_manager.draw_name_input(self.screen, self.player_name)

            pygame.display.flip()

        pygame.quit()