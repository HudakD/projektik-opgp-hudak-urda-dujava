import pygame
import random
import socket
from src.settings import *
from src.road.road import Road
from src.cars.player import Player
from src.cars.obstacle import ObstacleCar
from src.cars.bonus import Shield
from src.score.score_manager import ScoreManager
from src.ui.ui_manager import UIManager
from src.audio.audio_manager import AudioManager
from src.network import PacketType, HostServer, ClientPeer

MIN_OBSTACLE_GAP = 300
MIN_SHIELD_GAP = 1000


class GameMode:
    SINGLEPLAYER = 0
    HOST = 1
    CLIENT = 2


class GameState:
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    ENTERING_NAME = 3
    PAUSED = 4
    MP_CLIENT_SETUP = 5
    MP_WAITING = 6
    MP_RESULT = 7


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("F1 TURBO")
        self.clock = pygame.time.Clock()
        self.running = True

        self.score_manager = ScoreManager()
        self.ui_manager = UIManager()
        self.audio = AudioManager()

        self.state = GameState.MENU
        self.mode = GameMode.SINGLEPLAYER
        self.player_name = ""

        self.road = None
        self.player = None
        self.players = []
        self.obstacles = []

        self.shield = []

        self.current_speed = INITIAL_SCROLL_SPEED
        self.obstacle_spawn_rate = 80000
        self.shield_spawn_rate = 20 #TODO
        self.next_shield_spawn_time = 0
        self.last_difficulty_score = 0

        self.network = None
        self.network_seed = None
        self.local_player_index = 0
        self.remote_input = {"left": False, "right": False, "up": False, "down": False, "frame": 0}
        self.local_input = {"left": False, "right": False, "up": False, "down": False, "frame": 0}
        self.frame_count = 0
        self.join_ip = ""
        self.connection_message = ""
        self.multiplayer_result_text = ""
        self.connection_lost = False
        self.local_crashed = False
        self.remote_crashed = False
        self.multiplayer_crash_sent = False
        self.host_setup_sent = False
        self.host_setup_sent = False
        self.host_setup_sent = False

    def get_local_ip(self):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            if local_ip.startswith("127."):
                raise ValueError
            return local_ip
        except Exception:
            return "127.0.0.1"

    def reset_game(self, seed=None, multiplayer=False):
        if multiplayer:
            self.network_seed = seed if seed is not None else random.randint(0, 2**31 - 1)
            self.rng = random.Random(self.network_seed)
            self.road = Road(self.rng)
            self.players = [
                Player(WIDTH // 2, HEIGHT - 130, color=PLAYER_COLOR),
                Player(WIDTH // 2, HEIGHT - 130, color=OBSTACLE_COLOR)
            ]
            self.player = self.players[self.local_player_index]
        else:
            self.rng = random.Random()
            self.road = Road(self.rng)
            self.player = Player(WIDTH // 2, HEIGHT - 130)
            self.players = [self.player]

        self.obstacles = []
        self.shield = []
        self.score_manager.reset_score()
        self.current_speed = INITIAL_SCROLL_SPEED
        self.obstacle_spawn_rate = 8
        self.last_difficulty_score = 0
        self.player_name = ""
        self.frame_count = 0
        self.local_input = {"left": False, "right": False, "up": False, "down": False, "frame": 0}
        self.remote_input = {"left": False, "right": False, "up": False, "down": False, "frame": 0}
        self.local_crashed = False
        self.remote_crashed = False
        self.multiplayer_crash_sent = False
        self.audio.start_engine()

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

        if self.rng.randint(0, self.obstacle_spawn_rate) == 0:
            new_obstacle = ObstacleCar(-OBSTACLE_HEIGHT)
            new_obstacle.offset = self.rng.randint(-ROAD_WIDTH // 3, ROAD_WIDTH // 3)
            self.obstacles.append(new_obstacle)

    def spawn_shield(self):
        if self.shield:
            highest = min(s.y for s in self.shield)
            if highest > - MIN_SHIELD_GAP:
                return

        if self.rng.randint(0, self.shield_spawn_rate) == 0:
            new_shield = Shield(-SHIELD_HEIGHT)
            new_shield.offset = self.rng.randint(-ROAD_WIDTH // 3, ROAD_WIDTH // 3)
            new_shield.offset = self.rng.randint(-ROAD_WIDTH // 3, ROAD_WIDTH // 3)
            self.shield.append(new_shield)

    def update_obstacles(self):
        for o in self.obstacles:
            o.y += self.current_speed

        before_count = len(self.obstacles)
        self.obstacles = [o for o in self.obstacles if o.y < HEIGHT + 200]
        after_count = len(self.obstacles)

        passed = before_count - after_count
        if passed > 0:
            self.score_manager.increment_score(passed * 10)

    def update_shields(self):
        for s in self.shield:
            s.y += self.current_speed
        self.shield = [s for s in self.shield if s.y < HEIGHT + 200]

    def check_collisions(self, player):
        center_at_player = self.road.get_center_at(player.y + PLAYER_HEIGHT // 2)
        left_edge = center_at_player - ROAD_WIDTH // 2
        right_edge = center_at_player + ROAD_WIDTH // 2

        if player.x - PLAYER_WIDTH // 2 < left_edge or player.x + PLAYER_WIDTH // 2 > right_edge:
            if player.has_shield:
                player.has_shield = False
                player.x = center_at_player
                return False
            return True

        player_rect = pygame.Rect(
            player.x - PLAYER_WIDTH // 2,
            player.y,
            PLAYER_WIDTH,
            PLAYER_HEIGHT
        )

        current_time = pygame.time.get_ticks()
        for s in self.shield[:]:
            c = self.road.get_center_at(s.y + SHIELD_HEIGHT // 2) + s.offset
            shield_rect = pygame.Rect(
                c - SHIELD_WIDTH // 2,
                s.y,
                SHIELD_WIDTH,
                SHIELD_HEIGHT
            )
            if player_rect.colliderect(shield_rect):
                player.has_shield = True
                player.shield_expiry = current_time + 5000
                self.shield.remove(s)

        for o in self.obstacles[:]:
            c = self.road.get_center_at(o.y + OBSTACLE_HEIGHT // 2) + o.offset
            obstacle_rect = pygame.Rect(
                c - OBSTACLE_WIDTH // 2,
                o.y,
                OBSTACLE_WIDTH,
                OBSTACLE_HEIGHT
            )
            if player_rect.colliderect(obstacle_rect):
                if player.has_shield:
                    player.has_shield = False  # Shield absorbs the hit and breaks
                    self.obstacles.remove(o)
                    return False
                return True

        return False

    def handle_menu_input(self, event, mouse_pos, mouse_clicked):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.audio.play_sfx('click')
                self.mode = GameMode.SINGLEPLAYER
                self.reset_game()
                self.state = GameState.PLAYING

    def handle_join_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and len(self.join_ip) > 0:
                self.audio.play_sfx('click')
                self.network = ClientPeer(self.join_ip, MULTIPLAYER_PORT)
                self.network.connect()
                if self.network.is_connected():
                    self.connection_message = f"Pripojené na {self.join_ip}:{MULTIPLAYER_PORT}. Čakám na hostiteľa..."
                    self.network.send_packet({"type": PacketType.HELLO, "role": "client"})
                    self.state = GameState.MP_WAITING
                else:
                    self.connection_message = "Nepodarilo sa pripojiť. Skontroluj IP a skúšaj znova."
            elif event.key == pygame.K_BACKSPACE:
                self.join_ip = self.join_ip[:-1]
            elif len(self.join_ip) < 22:
                if event.unicode.isdigit() or event.unicode == '.' or event.unicode == ':':
                    self.join_ip += event.unicode

    def handle_playing_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.PAUSED

    def handle_paused_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.audio.play_sfx('click')
                self.state = GameState.PLAYING
            elif event.key == pygame.K_q:
                self.audio.stop_engine()
                self.cleanup_network()
                self.state = GameState.MENU

    def handle_game_over_input(self, event, mouse_pos, mouse_clicked):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                score = self.score_manager.get_current_score()
                if self.score_manager.is_highscore(score):
                    self.audio.play_sfx('highscore')
                    self.state = GameState.ENTERING_NAME
                else:
                    self.audio.play_sfx('click')
                    self.state = GameState.MENU
            elif event.key == pygame.K_ESCAPE:
                self.audio.play_sfx('click')
                self.state = GameState.MENU

    def handle_multiplayer_result_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.request_rematch()
            elif event.key == pygame.K_ESCAPE:
                self.cleanup_network()
                self.state = GameState.MENU

    def handle_name_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(self.player_name) > 0:
                self.audio.play_sfx('click')
                self.score_manager.add_score(self.player_name, self.score_manager.get_current_score())
                self.state = GameState.MENU
            elif event.key == pygame.K_BACKSPACE:
                if len(self.player_name) > 0:
                    self.audio.play_sfx('click')
                self.player_name = self.player_name[:-1]
            elif len(self.player_name) < 15:
                if event.unicode.isalnum() or event.unicode == ' ':
                    self.audio.play_sfx('click')
                    self.player_name += event.unicode

    def start_host_session(self):
        self.mode = GameMode.HOST
        self.local_player_index = 0
        self.network = HostServer(port=MULTIPLAYER_PORT)
        self.network.start()
        self.connection_message = f"Čakám na hráča...\nIP: {self.get_local_ip()}:{MULTIPLAYER_PORT}"
        self.state = GameState.MP_WAITING
        self.reset_game(seed=random.randint(0, 2**31 - 1), multiplayer=True)
        self.host_setup_sent = False

    def send_setup(self):
        if self.network and self.mode == GameMode.HOST and self.network.is_connected():
            packet = {"type": PacketType.SETUP, "seed": self.network_seed}
            self.network.send_packet(packet)
            self.host_setup_sent = True

    def send_start(self):
        if self.network and self.network.is_connected():
            packet = {"type": PacketType.START}
            self.network.send_packet(packet)

    def send_input(self, left, right, up=False, down=False):
        if self.network and self.network.is_connected():
            packet = {
                "type": PacketType.INPUT,
                "frame": self.frame_count,
                "player": self.local_player_index,
                "left": left,
                "right": right,
                "up": up,
                "down": down
            }
            self.network.send_packet(packet)

    def send_crash(self, player_index):
        if self.network and self.network.is_connected() and not self.multiplayer_crash_sent:
            packet = {"type": PacketType.CRASH, "player": player_index, "frame": self.frame_count}
            self.network.send_packet(packet)
            self.multiplayer_crash_sent = True

    def send_result(self, outcome):
        if self.network and self.network.is_connected():
            packet = {"type": PacketType.RESULT, "outcome": outcome}
            self.network.send_packet(packet)

    def send_rematch_response(self):
        if self.network and self.network.is_connected():
            packet = {"type": PacketType.REMATCH_RESPONSE}
            self.network.send_packet(packet)

    def request_rematch(self):
        if self.network and self.network.is_connected():
            packet = {"type": PacketType.REMATCH_REQUEST}
            self.network.send_packet(packet)
            self.connection_message = "Žiadosť o rematch odoslaná. Čakám..."
            self.state = GameState.MP_WAITING

    def cleanup_network(self):
        if self.network:
            try:
                self.network.send_packet({"type": PacketType.DISCONNECT})
            except Exception:
                pass
            self.network.stop()
        self.network = None
        self.connection_message = ""
        self.connection_lost = False

    def process_network_messages(self):
        if not self.network:
            return

        packets = self.network.get_packets()
        for packet in packets:
            if not isinstance(packet, dict) or "type" not in packet:
                continue
            if self.mode == GameMode.HOST:
                self.handle_host_packet(packet)
            else:
                self.handle_client_packet(packet)

    def handle_host_packet(self, packet):
        packet_type = packet["type"]

        if packet_type == PacketType.HELLO:
            self.connection_message = "Hráč sa pripojil. Čakám na READY..."
            if not self.host_setup_sent:
                self.send_setup()
        elif packet_type == PacketType.READY:
            self.connection_message = "Hráč je pripravený. Štartujem..."
            self.send_start()
            self.state = GameState.PLAYING
            self.frame_count = 0
        elif packet_type == PacketType.INPUT:
            if packet.get("player") == 1:
                self.remote_input["left"] = packet.get("left", False)
                self.remote_input["right"] = packet.get("right", False)
                self.remote_input["up"] = packet.get("up", False)
                self.remote_input["down"] = packet.get("down", False)
                self.remote_input["frame"] = packet.get("frame", self.frame_count)
        elif packet_type == PacketType.CRASH:
            self.remote_crashed = True
            if self.local_crashed and packet.get("frame") == self.frame_count:
                self.multiplayer_result_text = "DRAW"
                self.send_result("DRAW")
                self.state = GameState.MP_RESULT
            elif not self.local_crashed:
                self.multiplayer_result_text = "WIN"
                self.send_result("WIN")
                self.state = GameState.MP_RESULT
        elif packet_type == PacketType.REMATCH_REQUEST:
            if self.state == GameState.MP_RESULT:
                self.send_rematch_response()
                self.network_seed = random.randint(0, 2**31 - 1)
                self.reset_game(seed=self.network_seed, multiplayer=True)
                self.host_setup_sent = False
                self.state = GameState.MP_WAITING
                self.send_setup()
        elif packet_type == PacketType.DISCONNECT:
            self.connection_lost = True
            self.connection_message = "Spojenie bolo prerušené."
            self.multiplayer_result_text = "CONNECTION LOST"
            self.state = GameState.MP_RESULT

    def handle_client_packet(self, packet):
        packet_type = packet["type"]

        if packet_type == PacketType.SETUP:
            self.network_seed = packet.get("seed")
            self.local_player_index = 1
            self.reset_game(seed=self.network_seed, multiplayer=True)
            self.player = self.players[self.local_player_index]
            self.network.send_packet({"type": PacketType.READY})
            self.connection_message = "Nastavenie dokončené. Čakám na štart..."
            self.state = GameState.MP_WAITING
        elif packet_type == PacketType.START:
            self.state = GameState.PLAYING
            self.frame_count = 0
        elif packet_type == PacketType.INPUT:
            if packet.get("player") == 0:
                self.remote_input["left"] = packet.get("left", False)
                self.remote_input["right"] = packet.get("right", False)
                self.remote_input["up"] = packet.get("up", False)
                self.remote_input["down"] = packet.get("down", False)
                self.remote_input["frame"] = packet.get("frame", self.frame_count)
        elif packet_type == PacketType.RESULT:
            self.multiplayer_result_text = packet.get("outcome", "LOSE")
            self.state = GameState.MP_RESULT
        elif packet_type == PacketType.REMATCH_RESPONSE:
            self.connection_message = "Rematch akceptovaný. Čakám na nový zápas..."
            self.state = GameState.MP_WAITING
        elif packet_type == PacketType.DISCONNECT:
            self.connection_lost = True
            self.multiplayer_result_text = "CONNECTION LOST"
            self.state = GameState.MP_RESULT

    def update_singleplayer(self):
        if self.player.has_shield and pygame.time.get_ticks() > self.player.shield_expiry:
            self.player.has_shield = False

        keys = pygame.key.get_pressed()
        self.player.update(keys)
        self.road.update(self.current_speed)
        self.spawn_obstacle()
        self.spawn_shield()
        self.update_obstacles()
        self.update_shields()
        self.update_difficulty()
        self.audio.update_engine_pitch(self.current_speed)
        self.score_manager.increment_score(self.current_speed / 100)

        if self.check_collisions(self.player):
            self.audio.stop_engine()
            self.audio.play_sfx('crash')
            self.state = GameState.GAME_OVER

    def update_multiplayer(self):
        if not self.network or not self.network.is_connected():
            return
        current_time = pygame.time.get_ticks()
        for p in self.players:
            if p.has_shield and current_time > p.shield_expiry:
                p.has_shield = False

        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT]
        right = keys[pygame.K_RIGHT]
        up = keys[pygame.K_UP]
        down = keys[pygame.K_DOWN]
        self.local_input.update({"left": left, "right": right, "up": up, "down": down, "frame": self.frame_count})
        self.send_input(left, right, up=up, down=down)

        # apply local and remote inputs (Player.update accepts flags)
        self.players[self.local_player_index].update(left=left, right=right, up=up, down=down)
        remote_index = 1 - self.local_player_index
        self.players[remote_index].update(left=self.remote_input["left"], right=self.remote_input["right"], up=self.remote_input.get("up", False), down=self.remote_input.get("down", False))

        self.road.update(self.current_speed)
        self.spawn_obstacle()
        self.update_obstacles()
        self.update_difficulty()
        self.audio.update_engine_pitch(self.current_speed)
        self.score_manager.increment_score(self.current_speed / 100)

        if self.check_collisions(self.players[self.local_player_index]):
            if not self.local_crashed:
                self.local_crashed = True
                self.send_crash(self.local_player_index)
                if self.mode == GameMode.CLIENT:
                    self.connection_message = "Krach. Čakám na výsledok..."
                    self.state = GameState.MP_WAITING
                elif self.mode == GameMode.HOST and not self.remote_crashed:
                    self.multiplayer_result_text = "LOSE"
                    self.send_result("LOSE")
                    self.state = GameState.MP_RESULT
        if self.mode == GameMode.HOST and self.remote_crashed and self.state != GameState.MP_RESULT:
            self.multiplayer_result_text = "WIN"
            self.send_result("WIN")
            self.state = GameState.MP_RESULT

        self.frame_count += 1

    def draw_shield_glow(self, player):
        mid_x = player.x
        mid_y = player.y + PLAYER_HEIGHT // 2

        glow_radius = max(PLAYER_WIDTH, PLAYER_HEIGHT) * 1.2
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_color = (0, 128, 255)

        for radius in range(int(glow_radius), int(PLAYER_WIDTH // 2), -4):
            alpha = int(50 * (1.0 - (radius / glow_radius) ** 2))
            if alpha > 0:
                pygame.draw.circle(glow_surface, (*glow_color, alpha), (glow_radius, glow_radius), radius)

        self.screen.blit(glow_surface, (mid_x - glow_radius, mid_y - glow_radius))

        border_rect = pygame.Rect(
            player.x - PLAYER_WIDTH // 2 - 2,
            player.y - 2,
            PLAYER_WIDTH + 4,
            PLAYER_HEIGHT + 4
        )
        border_thickness = 3

        pygame.draw.rect(self.screen, glow_color, border_rect, border_thickness, border_radius=4)

    def draw_game(self):
        self.screen.fill(GRASS_COLOR)
        self.road.draw(self.screen)
        for o in self.obstacles:
            c = self.road.get_center_at(o.y + OBSTACLE_HEIGHT // 2) + o.offset
            o.draw(self.screen, c)
        for s in self.shield:
            c = self.road.get_center_at(s.y + SHIELD_HEIGHT // 2) + s.offset
            s.draw(self.screen, c)
        if self.mode == GameMode.SINGLEPLAYER:
            if self.player.has_shield:
                self.draw_shield_glow(self.player)
            self.player.draw(self.screen)
        else:
            for p in self.players:
                if p.has_shield:
                    self.draw_shield_glow(p)
                p.draw(self.screen)

        self.ui_manager.draw_hud(self.screen, int(self.score_manager.get_current_score()), self.current_speed,
                                 self.audio)

    def draw_pause_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 200))
        self.screen.blit(overlay, (0, 0))
        panel_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 150, 500, 300)
        self.ui_manager.draw_glass_panel(self.screen, panel_rect, alpha=255)
        self.ui_manager.draw_text(self.screen, "PAUZA", self.ui_manager.font_large, UI_GOLD, WIDTH // 2,
                                  panel_rect.y + 80, center=True)
        self.ui_manager.draw_text(self.screen, "ESC - Pokračovať", self.ui_manager.font_medium, UI_TEXT_MAIN,
                                  WIDTH // 2, panel_rect.y + 160, center=True)
        self.ui_manager.draw_text(self.screen, "Q - Späť do menu", self.ui_manager.font_medium, UI_TEXT_DIM,
                                  WIDTH // 2, panel_rect.y + 210, center=True)

    def draw_multiplayer_status(self):
        self.ui_manager.draw_connection_status(self.screen, "Multiplayer", self.connection_message)

    def draw_multiplayer_result(self):
        result = self.multiplayer_result_text
        if result == "WIN":
            caption = "VYHRAL SI"
        elif result == "LOSE":
            caption = "PREHRAL SI"
        elif result == "DRAW":
            caption = "REMÍZA"
        else:
            caption = result
        self.ui_manager.draw_multiplayer_result(self.screen, caption)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.audio.toggle_mute()
                    elif event.key == pygame.K_PLUS:
                        if self.audio.muted:
                            self.audio.toggle_mute()
                        self.audio.change_volume(0.1)
                    elif event.key == pygame.K_MINUS:
                        self.audio.change_volume(-0.1)
                        if self.audio.engine_volume <= 0.01 and not self.audio.muted:
                            self.audio.toggle_mute()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_clicked = True

                if self.state == GameState.MENU:
                    self.handle_menu_input(event, mouse_pos, mouse_clicked)
                elif self.state == GameState.MP_CLIENT_SETUP:
                    self.handle_join_input(event)
                elif self.state == GameState.PLAYING:
                    self.handle_playing_input(event)
                elif self.state == GameState.PAUSED:
                    self.handle_paused_input(event)
                elif self.state == GameState.MP_RESULT:
                    self.handle_multiplayer_result_input(event)
                elif self.state == GameState.GAME_OVER:
                    self.handle_game_over_input(event, mouse_pos, mouse_clicked)
                elif self.state == GameState.ENTERING_NAME:
                    self.handle_name_input(event)

            self.process_network_messages()

            if self.state == GameState.MENU:
                action = self.ui_manager.draw_menu(self.screen, self.score_manager.get_highscores(), mouse_pos,
                                                   mouse_clicked)
                if action == "single":
                    self.audio.play_sfx('click')
                    self.mode = GameMode.SINGLEPLAYER
                    self.reset_game()
                    self.state = GameState.PLAYING
                elif action == "host":
                    self.audio.play_sfx('click')
                    self.start_host_session()
                elif action == "join":
                    self.audio.play_sfx('click')
                    self.mode = GameMode.CLIENT
                    self.join_ip = ""
                    self.state = GameState.MP_CLIENT_SETUP

            elif self.state == GameState.MP_CLIENT_SETUP:
                self.screen.fill(GRASS_COLOR)
                action = self.ui_manager.draw_multiplayer_setup(self.screen, "JOIN GAME",
                                                               "Zadaj IP hostiteľa a stlač ENTER:", self.join_ip,
                                                               mouse_pos, mouse_clicked)
                if action == "join" and len(self.join_ip) > 0:
                    self.audio.play_sfx('click')
                    self.network = ClientPeer(self.join_ip, MULTIPLAYER_PORT)
                    self.network.connect()
                    if self.network.is_connected():
                        self.connection_message = f"Pripojené na {self.join_ip}:{MULTIPLAYER_PORT}. Čakám na hostiteľa..."
                        self.network.send_packet({"type": PacketType.HELLO, "role": "client"})
                        self.state = GameState.MP_WAITING
                    else:
                        self.connection_message = "Nepodarilo sa pripojiť. Skontroluj IP a skúšaj znova."
                elif action == "back":
                    self.state = GameState.MENU

            elif self.state == GameState.MP_WAITING:
                self.screen.fill(GRASS_COLOR)
                self.draw_multiplayer_status()

            elif self.state == GameState.PLAYING:
                if self.mode == GameMode.SINGLEPLAYER:
                    self.update_singleplayer()
                else:
                    self.update_multiplayer()
                self.draw_game()

            elif self.state == GameState.PAUSED:
                self.draw_game()
                self.draw_pause_screen()

            elif self.state == GameState.GAME_OVER:
                self.draw_game()
                score = self.score_manager.get_current_score()
                if self.ui_manager.draw_game_over_screen(self.screen, int(score),
                                                         self.score_manager.is_highscore(score), mouse_pos,
                                                         mouse_clicked):
                    self.audio.play_sfx('click')
                    self.state = GameState.MENU

            elif self.state == GameState.ENTERING_NAME:
                self.draw_game()
                self.ui_manager.draw_game_over_screen(self.screen, int(self.score_manager.get_current_score()), True,
                                                      mouse_pos, False)
                self.ui_manager.draw_name_input(self.screen, self.player_name)

            elif self.state == GameState.MP_RESULT:
                self.draw_game()
                self.draw_multiplayer_result()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_TAB]:
                self.ui_manager.draw_leaderboard(self.screen, self.score_manager.get_highscores())

            pygame.display.flip()

        self.cleanup_network()
        pygame.quit()
